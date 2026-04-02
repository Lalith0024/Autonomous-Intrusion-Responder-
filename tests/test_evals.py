"""Behavioral eval suite — tests the LLM's judgment, not code logic.

Run directly: python tests/test_evals.py
Requires OPENAI_API_KEY in .env
"""

import sys
import time

sys.path.insert(0, ".")

from dotenv import load_dotenv

load_dotenv()

from src.agents.triage_agent import analyze_log_event
from src.models.schemas import LogEvent

EVAL_CASES = [
    {
        "name": "SSH Brute Force",
        "log_event": {
            "timestamp": "2026-04-01T10:00:00Z",
            "source_ip": "45.33.32.156",
            "destination_ip": "192.168.1.10",
            "destination_port": 22,
            "protocol": "TCP",
            "event_type": "failed_login",
            "raw_log": "Mar 18 22:00:01 server sshd[1234]: Failed password for root from 45.33.32.156 port 54832 ssh2 — 47 failed attempts in 60 seconds",
        },
        "expected_attack_type": "brute_force",
        "expected_severity": "high",
    },
    {
        "name": "SQL Injection",
        "log_event": {
            "timestamp": "2026-04-01T10:05:00Z",
            "source_ip": "203.0.113.42",
            "destination_ip": "10.0.0.5",
            "destination_port": 443,
            "protocol": "TCP",
            "event_type": "http_request",
            "raw_log": "203.0.113.42 - - [01/Apr/2026:10:05:00] \"GET /api/users?id=1' OR '1'='1' -- HTTP/1.1\" 200 4892 — response contained 200 user records",
        },
        "expected_attack_type": "sql_injection",
        "expected_severity": "critical",
    },
    {
        "name": "Port Scan",
        "log_event": {
            "timestamp": "2026-04-01T10:10:00Z",
            "source_ip": "10.0.0.99",
            "destination_ip": "192.168.1.10",
            "destination_port": 0,
            "protocol": "TCP",
            "event_type": "port_scan",
            "raw_log": "SYN packets to ports 21,22,23,25,80,443,3389,5432,8080,8443 from 10.0.0.99 within 3 seconds — no established connections",
        },
        "expected_attack_type": "port_scan",
        "expected_severity": "medium",
    },
    {
        "name": "DDoS Signature",
        "log_event": {
            "timestamp": "2026-04-01T10:15:00Z",
            "source_ip": "198.51.100.0",
            "destination_ip": "192.168.1.1",
            "destination_port": 80,
            "protocol": "UDP",
            "event_type": "flood",
            "raw_log": "UDP flood detected: 850,000 packets/sec from 198.51.100.0/24 subnet targeting port 80 — server response time degraded to 12s",
        },
        "expected_attack_type": "denial_of_service",
        "expected_severity": "critical",
    },
    {
        "name": "Malware Beacon",
        "log_event": {
            "timestamp": "2026-04-01T10:20:00Z",
            "source_ip": "192.168.1.50",
            "destination_ip": "185.141.63.120",
            "destination_port": 8443,
            "protocol": "TCP",
            "event_type": "outbound_connection",
            "raw_log": "Periodic HTTPS POST to 185.141.63.120:8443 every 300s — payload 2KB encoded base64 — domain resolves to known C2 infrastructure (ThreatFox hit)",
        },
        "expected_attack_type": "unknown",
        "expected_severity": "high",
    },
    {
        "name": "Suspicious Login",
        "log_event": {
            "timestamp": "2026-04-01T10:25:00Z",
            "source_ip": "91.240.118.172",
            "destination_ip": "10.0.0.2",
            "destination_port": 3389,
            "protocol": "TCP",
            "event_type": "successful_login",
            "raw_log": "Successful RDP login for admin from 91.240.118.172 (GeoIP: Russia) at 03:14 UTC — account previously only accessed from US IPs during business hours",
        },
        "expected_attack_type": "brute_force",
        "expected_severity": "high",
    },
    {
        "name": "Normal Traffic",
        "log_event": {
            "timestamp": "2026-04-01T10:30:00Z",
            "source_ip": "192.168.1.55",
            "destination_ip": "192.168.1.10",
            "destination_port": 80,
            "protocol": "TCP",
            "event_type": "connection",
            "raw_log": "192.168.1.55 - - [01/Apr/2026:10:30:00 +0000] \"GET /index.html HTTP/1.1\" 200 1024",
        },
        "expected_attack_type": "normal_traffic",
        "expected_severity": "low",
    },
    {
        # Deliberately ambiguous — should produce low confidence
        "name": "Ambiguous Activity",
        "log_event": {
            "timestamp": "2026-04-01T10:35:00Z",
            "source_ip": "172.16.0.100",
            "destination_ip": "192.168.1.10",
            "destination_port": 8080,
            "protocol": "TCP",
            "event_type": "connection",
            "raw_log": "Single connection to port 8080 from internal host 172.16.0.100 — 1 GET request to /health — 200 OK — normal payload size",
        },
        "expected_attack_type": "normal_traffic",
        "expected_severity": "low",
    },
]


def run_evals() -> None:
    print(f"\n{'='*60}")
    print("  BEHAVIORAL EVAL SUITE — Autonomous Intrusion Responder")
    print(f"{'='*60}\n")

    correct = 0
    total = len(EVAL_CASES)
    confidences = []
    latencies = []

    for i, case in enumerate(EVAL_CASES, 1):
        name = case["name"]
        log_event = LogEvent(**case["log_event"])

        print(f"[{i}/{total}] {name}...", end=" ", flush=True)

        start = time.perf_counter()
        result = analyze_log_event(log_event)
        elapsed = time.perf_counter() - start

        actual_type = result["attack_type"]
        actual_severity = result["severity"]
        confidence = result["confidence_score"]

        type_match = actual_type == case["expected_attack_type"]
        sev_match = actual_severity == case["expected_severity"]
        passed = type_match and sev_match

        confidences.append(confidence)
        latencies.append(elapsed)

        if passed:
            correct += 1
            print(f"✓ PASS ({elapsed:.1f}s, conf: {confidence:.2f})")
        else:
            print(f"✗ FAIL ({elapsed:.1f}s, conf: {confidence:.2f})")
            if not type_match:
                print(f"    attack_type: expected={case['expected_attack_type']}, got={actual_type}")
            if not sev_match:
                print(f"    severity: expected={case['expected_severity']}, got={actual_severity}")

    avg_conf = sum(confidences) / len(confidences) if confidences else 0
    avg_lat = sum(latencies) / len(latencies) if latencies else 0

    print(f"\n{'='*60}")
    print(f"  Eval Results: {correct}/{total} correct | Avg confidence: {avg_conf:.2f} | Avg latency: {avg_lat:.1f}s")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    run_evals()
