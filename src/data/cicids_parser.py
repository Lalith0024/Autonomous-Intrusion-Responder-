"""Network intrusion dataset parser.

Downloads and parses the network intrusion dataset from Kaggle via kagglehub.
Converts raw flow records into LogEvent-compatible dicts for the agent pipeline.
"""

import os
import random
from pathlib import Path

import pandas as pd

# Maps dataset label strings → our attack_type enum values
LABEL_MAP: dict[str, str] = {
    "BENIGN": "normal_traffic",
    "DoS Hulk": "denial_of_service",
    "DoS GoldenEye": "denial_of_service",
    "DoS slowloris": "denial_of_service",
    "DoS Slowhttptest": "denial_of_service",
    "DDoS": "denial_of_service",
    "PortScan": "port_scan",
    "SSH-Patator": "brute_force",
    "FTP-Patator": "brute_force",
    "Bot": "unknown",
    "Infiltration": "unknown",
    "Heartbleed": "unknown",
}


def _map_label(raw_label: str) -> str:
    """Map a dataset label string to a local attack_type enum value."""
    label = raw_label.strip()
    if label in LABEL_MAP:
        return LABEL_MAP[label]
    if "Web Attack" in label:
        return "sql_injection"
    return "unknown"


def _safe_col(df: pd.DataFrame, *candidates: str) -> str | None:
    """Return the first column name that exists in the dataframe."""
    for c in candidates:
        if c in df.columns:
            return c
    return None


def _build_raw_log(row: pd.Series, col: dict) -> str:
    """Construct a plain-English log line from numeric flow fields."""
    proto = str(row.get(col.get("protocol", ""), "TCP")).strip()
    src_ip = str(row.get(col.get("src_ip", ""), "0.0.0.0")).strip()
    src_port = str(row.get(col.get("src_port", ""), "0")).strip()
    dst_ip = str(row.get(col.get("dst_ip", ""), "0.0.0.0")).strip()
    dst_port = str(row.get(col.get("dst_port", ""), "0")).strip()
    fwd_pkts = str(row.get(col.get("fwd_pkts", ""), "?")).strip() if col.get("fwd_pkts") else "?"
    total_bytes = str(row.get(col.get("total_bytes", ""), "?")).strip() if col.get("total_bytes") else "?"
    duration = str(row.get(col.get("duration", ""), "?")).strip() if col.get("duration") else "?"

    return (
        f"{proto} flow: {src_ip}:{src_port} → {dst_ip}:{dst_port} | "
        f"packets={fwd_pkts} bytes={total_bytes} duration={duration}μs"
    )


def get_ground_truth_label(row: pd.Series) -> str:
    """Return the mapped attack_type label for a given dataset row."""
    raw = str(row.get("Label", "BENIGN"))
    return _map_label(raw)


def _load_dataframe() -> pd.DataFrame:
    """Load the dataset via kagglehub (auto-downloads on first run)."""
    try:
        import kagglehub

        dataset_path = kagglehub.dataset_download("chethuhn/network-intrusion-dataset")
        # Find the first CSV in the downloaded directory
        csv_files = list(Path(dataset_path).rglob("*.csv"))
        if not csv_files:
            raise FileNotFoundError(f"No CSV files found in {dataset_path}")

        # Prefer a file that looks like the main dataset
        main_csv = sorted(csv_files, key=lambda f: f.stat().st_size, reverse=True)[0]
        print(f"  Loading: {main_csv.name}")

        df = pd.read_csv(main_csv, encoding="utf-8", low_memory=False)
        return df

    except ImportError:
        raise ImportError("kagglehub not installed. Run: pip install 'kagglehub[pandas-datasets]'")


def load_cicids_sample(n: int = 50, random_seed: int = 42) -> list[dict]:
    """Load a balanced sample of n rows from the network intrusion dataset.

    Downloads the dataset automatically on first run via kagglehub.
    Tries to sample evenly across attack types for a representative set.

    Args:
        n: Number of rows to return.
        random_seed: Seed for reproducibility.

    Returns:
        List of dicts with LogEvent-compatible keys + _ground_truth_label.
    """
    df = _load_dataframe()

    # Strip leading/trailing whitespace from column names — common dataset issue
    df.columns = [c.strip() for c in df.columns]

    # Drop rows with NaN or infinite values
    df = df.replace([float("inf"), float("-inf")], pd.NA).dropna(subset=["Label"])

    # Discover column names (dataset versions vary slightly)
    col = {
        "src_ip": _safe_col(df, "Source IP", "Src IP", "src_ip", " Source IP"),
        "src_port": _safe_col(df, "Source Port", "Src Port", "src_port"),
        "dst_ip": _safe_col(df, "Destination IP", "Dst IP", "dst_ip"),
        "dst_port": _safe_col(df, "Destination Port", "Dst Port", "dst_port"),
        "protocol": _safe_col(df, "Protocol", "protocol"),
        "fwd_pkts": _safe_col(df, "Total Fwd Packets", "Fwd Packet Length Total"),
        "total_bytes": _safe_col(df, "Total Length of Fwd Packets", "Total Fwd Bytes"),
        "duration": _safe_col(df, "Flow Duration", "flow_duration"),
    }

    # Balanced sampling — equal representation across attack types
    unique_labels = df["Label"].unique().tolist()
    per_label = max(1, n // len(unique_labels))

    sampled_parts = []
    for label in unique_labels:
        subset = df[df["Label"] == label]
        k = min(per_label, len(subset))
        sampled_parts.append(subset.sample(n=k, random_state=random_seed))

    sampled = pd.concat(sampled_parts).head(n)
    sampled = sampled.sample(frac=1, random_state=random_seed).reset_index(drop=True)

    results = []
    for _, row in sampled.iterrows():
        ground_truth = _map_label(str(row["Label"]))

        src_ip = str(row.get(col["src_ip"] or "", "192.168.1.1")).strip() or "192.168.1.1"
        dst_ip = str(row.get(col["dst_ip"] or "", "10.0.0.1")).strip() or "10.0.0.1"
        dst_port_raw = row.get(col["dst_port"] or "", 80)
        protocol_val = str(row.get(col["protocol"] or "", "TCP")).strip() or "TCP"

        try:
            dst_port_int = int(float(str(dst_port_raw)))
        except (ValueError, TypeError):
            dst_port_int = 80

        results.append({
            "timestamp": "2017-07-07T00:00:00Z",
            "source_ip": src_ip,
            "destination_ip": dst_ip,
            "destination_port": dst_port_int,
            "protocol": protocol_val,
            "event_type": "network_flow",
            "raw_log": _build_raw_log(row, col),
            "_ground_truth_label": ground_truth,
        })

    return results
