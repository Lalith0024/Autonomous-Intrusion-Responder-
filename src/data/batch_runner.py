"""Batch runner: analyze network intrusion events through the agent pipeline.

Usage:
    python src/data/batch_runner.py

Requirements:
    - FastAPI server must be running: python run.py
    - GROQ_API_KEY set in .env
    - kagglehub installed: pip install 'kagglehub[pandas-datasets]'

The dataset is downloaded automatically from Kaggle on first run.
Results are saved to data/results/batch_results.json for the dashboard.
"""

import asyncio
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import httpx

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from dotenv import load_dotenv

load_dotenv()

from src.data.cicids_parser import load_cicids_sample

API_BASE = "http://127.0.0.1:8000"
OUTPUT_PATH = Path("data/results/batch_results.json")
SAMPLE_SIZE = 50


async def analyze_event(client: httpx.AsyncClient, event: dict, index: int, total: int) -> dict | None:
    """Send a single event to the /analyze endpoint and return the enriched result."""
    ground_truth = event.pop("_ground_truth_label", "unknown")
    payload = {k: v for k, v in event.items() if not k.startswith("_")}

    start = time.perf_counter()
    try:
        resp = await client.post(f"{API_BASE}/analyze", json=payload, timeout=60.0)
        elapsed = time.perf_counter() - start

        if resp.status_code != 200:
            print(f"  [{index}/{total}] HTTP {resp.status_code} — skipping")
            return None

        report = resp.json()
        predicted = report.get("attack_type", "unknown")
        conf = report.get("confidence_score", 0.0)
        match = predicted == ground_truth

        icon = "✓" if match else "✗"
        print(f"  {icon} [{index}/{total}] {ground_truth.upper():20s} → {predicted:20s} ({conf:.2f}) [{elapsed:.1f}s]")

        return {
            "index": index,
            "ground_truth": ground_truth,
            "incident_report": report,
            "latency_s": round(elapsed, 2),
            "match": match,
        }

    except httpx.ConnectError:
        print(f"\n  ERROR [{index}/{total}] Cannot connect to API — is FastAPI running on {API_BASE}?\n")
        return None
    except Exception as e:
        print(f"  [{index}/{total}] Unexpected error: {e}")
        return None


async def run_batch() -> None:
    print(f"\n{'='*65}")
    print("  Network Intrusion — Batch Analysis")
    print(f"{'='*65}")
    print("  Downloading dataset from Kaggle (cached after first run)...")

    events = load_cicids_sample(n=SAMPLE_SIZE)
    total = len(events)
    print(f"  Loaded {total} events\n")

    results = []
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    # Sequential async — avoids hammering Groq rate limits
    async with httpx.AsyncClient() as client:
        for i, event in enumerate(events, 1):
            result = await analyze_event(client, event, i, total)
            if result:
                results.append(result)
            await asyncio.sleep(0.4)

    if not results:
        print("\n  No results. Check that FastAPI is running: python run.py")
        return

    correct = sum(1 for r in results if r["match"])
    avg_lat = sum(r["latency_s"] for r in results) / len(results)
    accuracy = (correct / len(results)) * 100

    summary = {
        "run_at": datetime.now(timezone.utc).isoformat(),
        "total": len(results),
        "correct": correct,
        "accuracy_pct": round(accuracy, 1),
        "avg_latency_s": round(avg_lat, 2),
        "results": results,
    }

    OUTPUT_PATH.write_text(json.dumps(summary, indent=2))

    print(f"\n{'='*65}")
    print(f"  Total: {len(results)} | Correct: {correct} | Accuracy: {accuracy:.1f}% | Avg latency: {avg_lat:.1f}s")
    print(f"  Results saved → {OUTPUT_PATH}")
    print(f"{'='*65}\n")


if __name__ == "__main__":
    asyncio.run(run_batch())
