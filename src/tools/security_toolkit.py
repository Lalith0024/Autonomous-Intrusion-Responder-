"""Security Toolkit — Real tools that agents can invoke during analysis.

This module provides investigation and response tools that transform the AI agents
from "text generators" into "actors." Each tool performs a real (or simulated) security
operation and returns structured results that get injected into the agent's context.

Production Notes:
    - investigate_ip uses ip-api.com (free, no key required, 45 req/min limit)
    - check_threat_intel uses simulated data (swap for VirusTotal/AbuseIPDB in prod)
    - scan_ports uses simulated nmap output (swap for real nmap subprocess in prod)
    - block_ip writes to a local JSON file (swap for iptables/AWS WAF in prod)
"""

from __future__ import annotations

import json
import logging
import random
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path

import httpx

from src.core.config import settings
from src.models.schemas import (
    IPInvestigation,
    PortInfo,
    PortScanResult,
    ToolCallRecord,
)

logger = logging.getLogger(__name__)

BLOCKED_IPS_PATH = Path(settings.BLOCKED_IPS_PATH)


# ── Tool 1: IP Investigation ────────────────────────────────────────


def investigate_ip(ip_address: str) -> tuple[IPInvestigation, ToolCallRecord]:
    """Look up IP geolocation, ISP, and proxy/tor status.

    Uses ip-api.com for real GeoIP data (free, no API key).
    Falls back to simulated data if the API is unreachable.

    Args:
        ip_address: The IP address to investigate.

    Returns:
        Tuple of (IPInvestigation result, ToolCallRecord for tracing).
    """
    start = time.perf_counter()
    logger.info("Investigating IP: %s", ip_address)

    try:
        resp = httpx.get(
            f"http://ip-api.com/json/{ip_address}",
            params={"fields": "status,country,city,isp,org,proxy,hosting,query"},
            timeout=5.0,
        )
        data = resp.json()

        if data.get("status") == "success":
            result = IPInvestigation(
                ip_address=ip_address,
                country=data.get("country", "Unknown"),
                city=data.get("city", "Unknown"),
                isp=data.get("isp", "Unknown"),
                org=data.get("org", "Unknown"),
                is_proxy=data.get("proxy", False),
                is_tor=False,
                abuse_score=_simulate_abuse_score(ip_address),
                is_known_malicious=_simulate_abuse_score(ip_address) > 70,
                threat_type="Suspicious" if _simulate_abuse_score(ip_address) > 70 else "None",
            )
        else:
            result = _fallback_ip_investigation(ip_address)

    except Exception as e:
        logger.warning("IP investigation failed for %s: %s. Using fallback.", ip_address, e)
        result = _fallback_ip_investigation(ip_address)

    duration = int((time.perf_counter() - start) * 1000)
    record = ToolCallRecord(
        tool_name="investigate_ip",
        arguments={"ip_address": ip_address},
        result=result.model_dump(),
        duration_ms=duration,
        called_by="triage_agent",
    )

    logger.info("IP investigation complete: %s → %s (%s)", ip_address, result.country, f"{duration}ms")
    return result, record


def _simulate_abuse_score(ip_address: str) -> int:
    """Generate a deterministic abuse score based on IP hash (for demo consistency)."""
    hash_val = sum(ord(c) for c in ip_address)
    # Private IPs get low scores, public IPs get variable scores
    if ip_address.startswith(("192.168.", "10.", "172.16.")):
        return hash_val % 20  # 0-19: low risk
    return 30 + (hash_val % 70)  # 30-99: variable risk


def _fallback_ip_investigation(ip_address: str) -> IPInvestigation:
    """Simulated IP investigation when real API is unavailable."""
    abuse = _simulate_abuse_score(ip_address)
    countries = ["United States", "Russia", "China", "Germany", "Netherlands", "Brazil", "India"]
    hash_val = sum(ord(c) for c in ip_address)

    return IPInvestigation(
        ip_address=ip_address,
        country=countries[hash_val % len(countries)],
        city="Unknown (Simulated)",
        isp="Simulated ISP",
        org="Unknown Org",
        is_proxy=abuse > 60,
        is_tor=abuse > 85,
        abuse_score=abuse,
        is_known_malicious=abuse > 70,
        threat_type="Suspicious Activity" if abuse > 70 else "None",
    )


# ── Tool 2: Port Scan ───────────────────────────────────────────────


def scan_ports(ip_address: str) -> tuple[PortScanResult, ToolCallRecord]:
    """Simulate an nmap-style port scan of the target IP.

    In production, this would invoke subprocess nmap or use python-nmap.
    For demo/safety, returns simulated but realistic scan data.

    Args:
        ip_address: The IP address to scan.

    Returns:
        Tuple of (PortScanResult, ToolCallRecord for tracing).
    """
    start = time.perf_counter()
    logger.info("Scanning ports for: %s", ip_address)

    # Simulated common port states
    common_ports = [
        PortInfo(port=22, service="ssh", state="open"),
        PortInfo(port=80, service="http", state="open"),
        PortInfo(port=443, service="https", state="open"),
        PortInfo(port=3306, service="mysql", state="closed"),
        PortInfo(port=5432, service="postgresql", state="closed"),
        PortInfo(port=8080, service="http-proxy", state="filtered"),
        PortInfo(port=3389, service="ms-wbt-server", state="closed"),
        PortInfo(port=21, service="ftp", state="closed"),
        PortInfo(port=25, service="smtp", state="filtered"),
        PortInfo(port=8443, service="https-alt", state="closed"),
    ]

    # Deterministic selection based on IP hash
    hash_val = sum(ord(c) for c in ip_address)
    random.seed(hash_val)
    num_open = random.randint(2, 6)
    selected = random.sample(common_ports, min(num_open, len(common_ports)))

    # Make at least some ports open
    for i in range(min(2, len(selected))):
        selected[i].state = "open"

    os_guesses = ["Linux 4.x-5.x", "Windows Server 2019", "Ubuntu 22.04", "FreeBSD 13", "CentOS 8"]

    result = PortScanResult(
        target_ip=ip_address,
        open_ports=selected,
        os_guess=os_guesses[hash_val % len(os_guesses)],
        scan_time_ms=random.randint(200, 800),
    )

    duration = int((time.perf_counter() - start) * 1000)
    record = ToolCallRecord(
        tool_name="scan_ports",
        arguments={"ip_address": ip_address},
        result=result.model_dump(),
        duration_ms=duration,
        called_by="triage_agent",
    )

    open_count = sum(1 for p in selected if p.state == "open")
    logger.info("Port scan complete: %s → %d open ports (%s)", ip_address, open_count, f"{duration}ms")
    return result, record


# ── Tool 3: Threat Intelligence Check ───────────────────────────────


def check_threat_intel(indicator: str) -> tuple[dict, ToolCallRecord]:
    """Check an IP/domain/hash against threat intelligence feeds.

    In production, this would query VirusTotal, AbuseIPDB, ThreatFox, etc.
    For demo, returns simulated but realistic threat intel data.

    Args:
        indicator: IP address, domain, or file hash to check.

    Returns:
        Tuple of (threat intel dict, ToolCallRecord for tracing).
    """
    start = time.perf_counter()
    logger.info("Checking threat intel for: %s", indicator)

    hash_val = sum(ord(c) for c in indicator)
    is_malicious = hash_val % 3 == 0  # ~33% chance of being known malicious

    threat_types = ["Command and Control", "Botnet", "Phishing", "Malware Distribution", "Scanning"]
    sources = ["ThreatFox", "AbuseIPDB", "VirusTotal", "AlienVault OTX", "Shodan"]

    result = {
        "indicator": indicator,
        "is_known_malicious": is_malicious,
        "threat_type": threat_types[hash_val % len(threat_types)] if is_malicious else "None",
        "confidence": round(0.6 + (hash_val % 40) / 100, 2) if is_malicious else 0.0,
        "first_seen": "2025-08-15T00:00:00Z" if is_malicious else None,
        "last_seen": "2026-03-28T00:00:00Z" if is_malicious else None,
        "sources": [sources[hash_val % len(sources)]] if is_malicious else [],
        "references": [f"https://threatfox.abuse.ch/ioc/{hash_val}"] if is_malicious else [],
        "tags": ["suspicious", "automated"] if is_malicious else [],
    }

    duration = int((time.perf_counter() - start) * 1000)
    record = ToolCallRecord(
        tool_name="check_threat_intel",
        arguments={"indicator": indicator},
        result=result,
        duration_ms=duration,
        called_by="triage_agent",
    )

    logger.info("Threat intel check: %s → malicious=%s", indicator, is_malicious)
    return result, record


# ── Tool 4: Block IP ─────────────────────────────────────────────────


def block_ip(
    ip_address: str,
    reason: str = "Automated block by AIR",
    duration_hours: int = 24,
) -> tuple[dict, ToolCallRecord]:
    """Add an IP to the blocked list.

    In production, this would call a firewall API (iptables, AWS WAF, Cloudflare).
    For demo, appends to a local JSON file that the dashboard reads.

    Args:
        ip_address: The IP address to block.
        reason: Human-readable reason for the block.
        duration_hours: How long to block (default 24h).

    Returns:
        Tuple of (block result dict, ToolCallRecord for tracing).
    """
    start = time.perf_counter()
    logger.info("Blocking IP: %s for %dh — %s", ip_address, duration_hours, reason)

    now = datetime.now(timezone.utc)
    blocked_until = now + timedelta(hours=duration_hours)

    # Load existing blocked IPs
    blocked_list = _load_blocked_ips()

    # Add new entry
    entry = {
        "ip_address": ip_address,
        "reason": reason,
        "blocked_at": now.isoformat().replace("+00:00", "Z"),
        "blocked_until": blocked_until.isoformat().replace("+00:00", "Z"),
        "duration_hours": duration_hours,
        "active": True,
    }

    # Update existing or append
    existing_idx = next((i for i, b in enumerate(blocked_list) if b["ip_address"] == ip_address), None)
    if existing_idx is not None:
        blocked_list[existing_idx] = entry
    else:
        blocked_list.append(entry)

    # Persist
    _save_blocked_ips(blocked_list)

    result = {
        "success": True,
        "ip_address": ip_address,
        "blocked_until": entry["blocked_until"],
        "total_blocked_count": len(blocked_list),
        "message": f"IP {ip_address} blocked until {entry['blocked_until']}",
    }

    duration = int((time.perf_counter() - start) * 1000)
    record = ToolCallRecord(
        tool_name="block_ip",
        arguments={"ip_address": ip_address, "reason": reason, "duration_hours": duration_hours},
        result=result,
        duration_ms=duration,
        called_by="response_agent",
    )

    logger.info("IP blocked: %s until %s (total blocked: %d)", ip_address, entry["blocked_until"], len(blocked_list))
    return result, record


# ── Blocked IP Helpers ───────────────────────────────────────────────


def _load_blocked_ips() -> list[dict]:
    """Load the blocked IPs list from disk."""
    if BLOCKED_IPS_PATH.exists():
        try:
            return json.loads(BLOCKED_IPS_PATH.read_text())
        except (json.JSONDecodeError, OSError):
            return []
    return []


def _save_blocked_ips(blocked_list: list[dict]) -> None:
    """Persist the blocked IPs list to disk."""
    BLOCKED_IPS_PATH.parent.mkdir(parents=True, exist_ok=True)
    BLOCKED_IPS_PATH.write_text(json.dumps(blocked_list, indent=2))


def get_blocked_ips() -> list[dict]:
    """Return all currently blocked IPs, filtering out expired blocks.

    Returns:
        List of active blocked IP entries.
    """
    blocked_list = _load_blocked_ips()
    now = datetime.now(timezone.utc)
    active = []

    for entry in blocked_list:
        try:
            until = datetime.fromisoformat(entry["blocked_until"].replace("Z", "+00:00"))
            if until > now:
                active.append(entry)
        except (KeyError, ValueError):
            continue

    return active


def unblock_ip(ip_address: str) -> dict:
    """Remove an IP from the blocked list.

    Args:
        ip_address: The IP address to unblock.

    Returns:
        Result dict with success status.
    """
    blocked_list = _load_blocked_ips()
    new_list = [b for b in blocked_list if b["ip_address"] != ip_address]

    if len(new_list) == len(blocked_list):
        return {"success": False, "message": f"IP {ip_address} not found in blocked list"}

    _save_blocked_ips(new_list)
    logger.info("IP unblocked: %s", ip_address)
    return {"success": True, "message": f"IP {ip_address} has been unblocked"}
