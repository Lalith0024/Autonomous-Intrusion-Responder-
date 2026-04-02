"""Page 1: Live Analysis — real-time agent pipeline execution."""

import json
import time
from pathlib import Path

import httpx
import streamlit as st

API_BASE = "http://127.0.0.1:8000"
RESULTS_PATH = Path("data/results/batch_results.json")
SAMPLE_LOG = "Mar 18 22:00:01 server sshd[1234]: Failed password for root from 45.33.32.156 port 54832 ssh2 — 47 failed attempts in 60 seconds"

SEV_PILL = {
    "critical": '<span class="pill pill-critical">⬤ CRITICAL</span>',
    "high":     '<span class="pill pill-high">⬤ HIGH</span>',
    "medium":   '<span class="pill pill-medium">⬤ MEDIUM</span>',
    "low":      '<span class="pill pill-low">⬤ LOW</span>',
    "info":     '<span class="pill pill-info">⬤ INFO</span>',
}

SEV_ACCENT = {
    "critical": "red", "high": "red", "medium": "amber", "low": "green", "info": "blue",
}

CONF_COLOR = lambda c: "#10b981" if c >= 0.8 else "#f59e0b" if c >= 0.6 else "#ef4444"

NODE_LABELS = {
    "triage_node":       ("🔍", "Triage Agent"),
    "severity_router":   ("🔀", "Policy Router"),
    "response_agent":    ("🛠", "Response Agent"),
    "human_review_node": ("👁", "Human Review"),
}

NODE_DESC = {
    "triage_node":       lambda d: f"Classified as <strong>{d.get('attack_type','?').replace('_',' ').title()}</strong> — confidence {d.get('confidence_score',0):.0%}",
    "severity_router":   lambda d: f"Routed to <strong>{'Human Review' if d.get('needs_human_review') else 'Response Agent' if d.get('response_plan') else 'End'}</strong> based on severity + confidence",
    "response_agent":    lambda d: f"Generated <strong>{len((d.get('response_plan') or {}).get('response_steps', []))} containment steps</strong>",
    "human_review_node": lambda _: "Confidence below threshold — <strong>flagged for analyst review</strong>",
}


def _call_api(payload: dict) -> dict | None:
    try:
        resp = httpx.post(f"{API_BASE}/analyze", json=payload, timeout=60.0)
        if resp.status_code == 200:
            return resp.json()
        st.error(f"API error {resp.status_code}: {resp.text[:300]}")
    except httpx.ConnectError:
        st.error("⚠ Cannot reach the API — make sure FastAPI is running: `python run.py`")
    except httpx.ReadTimeout:
        st.error("⚠ Request timed out — Groq may be under load, try again.")
    return None


def render_trace(data: dict) -> None:
    st.markdown('<div class="sec-label">EXECUTION TRACE</div>', unsafe_allow_html=True)
    placeholder = st.empty()
    built = []
    graph_path = data.get("graph_path", [])

    for i, node in enumerate(graph_path):
        time.sleep(0.35)
        icon, label = NODE_LABELS.get(node, ("⚙", node))
        desc_fn = NODE_DESC.get(node)
        desc = desc_fn(data) if desc_fn else ""
        is_final = (i == len(graph_path) - 1)
        built.append(f"""
        <div class="trace-step done">
            <div class="trace-icon">✅</div>
            <div>
                <div class="trace-node">{icon} {label}</div>
                <div class="trace-desc">{desc}</div>
            </div>
            {"<div style='margin-left:auto; font-size:0.7rem; color:#15803d; font-weight:600;'>FINAL OUTPUT</div>" if is_final and not data.get('needs_human_review') else ""}
        </div>""")
        placeholder.markdown("".join(built), unsafe_allow_html=True)

    if data.get("needs_human_review"):
        st.markdown("""
        <div class="banner banner-purple">
            <div class="banner-icon">⚠</div>
            <div><strong>Low Confidence Detection</strong> — This event has been flagged for human analyst review. Automated response withheld.</div>
        </div>""", unsafe_allow_html=True)


def render_incident(data: dict) -> None:
    sev = data.get("severity", "info")
    conf = data.get("confidence_score", 0)
    attack = data.get("attack_type", "unknown").replace("_", " ").title()
    action = data.get("recommended_action", "monitor").replace("_", " ").title()
    accent = SEV_ACCENT.get(sev, "blue")
    conf_color = CONF_COLOR(conf)
    pill = SEV_PILL.get(sev, SEV_PILL["info"])

    st.markdown('<div class="sec-label">INCIDENT REPORT</div>', unsafe_allow_html=True)

    # 3 metric cards
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"""
        <div class="metric-card card-accent-{accent}">
            <div class="metric-label">Attack Type</div>
            <div class="metric-val metric-dark" style="font-size:1.3rem;">{attack}</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="metric-card card-accent-{accent}">
            <div class="metric-label">Severity</div>
            <div style="margin-top:4px;">{pill}</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class="metric-card card-accent-{accent}">
            <div class="metric-label">Confidence</div>
            <div class="metric-val" style="color:{conf_color};">{conf:.0%}</div>
            <div class="conf-bar-wrap">
                <div class="conf-bar-fill" style="width:{conf*100}%; background:{conf_color};"></div>
            </div>
        </div>""", unsafe_allow_html=True)

    # Action + reasoning row
    left, right = st.columns([3, 2])
    with left:
        st.markdown('<div class="sec-label">ANALYST REASONING</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="reasoning">{data.get("reasoning", "No reasoning provided.")}</div>', unsafe_allow_html=True)
    with right:
        st.markdown('<div class="sec-label">RECOMMENDED ACTION</div>', unsafe_allow_html=True)
        action_color = "#10b981" if "block" in action.lower() or "quarantine" in action.lower() else "#3b82f6"
        st.markdown(f"""
        <div class="card" style="padding:0.9rem 1.1rem;">
            <div style="font-size:1.1rem; font-weight:800; color:{action_color};">{action}</div>
            <div style="font-size:0.72rem; color:#9ca3af; margin-top:4px;">Automated policy decision</div>
        </div>""", unsafe_allow_html=True)

    # Indicators
    iocs = data.get("indicators", [])
    if iocs:
        st.markdown('<div class="sec-label">INDICATORS OF COMPROMISE</div>', unsafe_allow_html=True)
        tags = "".join(f'<span class="ioc-tag">{i}</span>' for i in iocs)
        st.markdown(f'<div class="ioc-wrap">{tags}</div>', unsafe_allow_html=True)

    # Event metadata
    lat = data.get("processing_time_ms", 0)
    eid = data.get("event_id", "")[:8]
    ts  = data.get("timestamp", "")[:19].replace("T", " ")
    st.markdown(f'<div style="font-size:0.7rem; color:#9ca3af; margin-top:0.5rem; padding-top:0.5rem; border-top:1px solid #f3f4f6;">Event {eid}... · {ts} · {lat}ms processing</div>', unsafe_allow_html=True)


def render_playbook(data: dict) -> None:
    plan = data.get("response_plan")
    if not plan:
        return

    steps = plan.get("response_steps", [])
    escalate = plan.get("escalate_to_tier2", False)
    impact = plan.get("estimated_impact", "")
    n_steps = len(steps)

    st.markdown('<div class="sec-label">CONTAINMENT PLAYBOOK</div>', unsafe_allow_html=True)

    # Header banner
    st.markdown(f"""
    <div class="banner banner-green">
        <div class="banner-icon">✅</div>
        <div><strong>Response Plan Generated</strong> — {n_steps}-step containment playbook ready for execution.</div>
    </div>""", unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    steps_html = "".join(f"""
        <div class="playbook-step">
            <div class="step-num">{i}</div>
            <div class="step-txt">{step}</div>
        </div>""" for i, step in enumerate(steps, 1))
    st.markdown(steps_html + '</div>', unsafe_allow_html=True)

    if impact:
        st.markdown(f'<div class="impact-box">💥 <strong>Estimated Impact:</strong> {impact}</div>', unsafe_allow_html=True)

    if escalate:
        st.markdown("""
        <div class="banner banner-red" style="margin-top: 0.75rem;">
            <div class="banner-icon">🔺</div>
            <div><strong>Escalate to Tier 2 SOC Analyst</strong> — This incident requires immediate human intervention.</div>
        </div>""", unsafe_allow_html=True)


# ── Layout ─────────────────────────────────────────────────────────────────────
st.markdown('<div class="sec-label" style="margin-top:0;">LIVE ANALYSIS</div>', unsafe_allow_html=True)
st.markdown('<div class="page-header"><h1>Analyze a Threat Event</h1><p>Paste a raw log or select from the CICIDS dataset · Full agent pipeline runs in real time</p></div>', unsafe_allow_html=True)

left, right = st.columns([4, 6], gap="large")

with left:
    mode = st.radio("Input", ["✏️  Paste Log", "📂  From Dataset"], horizontal=True, label_visibility="collapsed")

    if "Paste" in mode:
        raw_log = st.text_area(
            "Raw Log Entry",
            value=SAMPLE_LOG,
            height=130,
            help="Paste any server log — sshd, nginx, firewall, Apache, etc.",
        )
        with st.expander("⚙ Log Metadata (optional)"):
            mc1, mc2 = st.columns(2)
            with mc1:
                src_ip   = st.text_input("Source IP", "45.33.32.156")
                protocol = st.selectbox("Protocol", ["TCP", "UDP", "ICMP"])
            with mc2:
                dst_ip     = st.text_input("Dest IP", "192.168.1.10")
                event_type = st.text_input("Event Type", "failed_login")
            dst_port = st.number_input("Destination Port", value=22, min_value=0, max_value=65535)

        clicked = st.button("⚡  Run Analysis", use_container_width=True, type="primary")
        st.markdown('<div style="text-align:center; font-size:0.72rem; color:#9ca3af; margin-top:6px;">Triage Agent → Policy Router → Response Agent</div>', unsafe_allow_html=True)

        if clicked:
            payload = {
                "timestamp": "2026-04-02T00:00:00Z",
                "source_ip": src_ip, "destination_ip": dst_ip,
                "destination_port": int(dst_port), "protocol": protocol,
                "event_type": event_type, "raw_log": raw_log,
            }
            with st.spinner("Agent pipeline running..."):
                result = _call_api(payload)
            if result:
                st.session_state["live_result"] = result
                st.rerun()

    else:  # From Dataset
        if not RESULTS_PATH.exists():
            st.markdown("""
            <div class="card card-accent-amber">
                <div style="font-size:0.85rem; font-weight:700; color:#b45309; margin-bottom:6px;">⚠ No batch data yet</div>
                <div style="font-size:0.8rem; color:#6b7280; line-height:1.5;">
                    Run the batch analyzer first:<br>
                    <code>python src/data/batch_runner.py</code>
                </div>
            </div>""", unsafe_allow_html=True)
        else:
            try:
                batch = json.loads(RESULTS_PATH.read_text())
                results_list = batch.get("results", [])
                sev_icons = {"critical": "🔴", "high": "🔴", "medium": "🟡", "low": "🟢", "info": "🔵"}

                options = [
                    f"{sev_icons.get(r['incident_report'].get('severity',''),'⚪')} {r['incident_report'].get('attack_type','?').replace('_',' ').title()} — {r['incident_report'].get('source_ip','?')}"
                    for r in results_list
                ]
                idx = st.selectbox("Select event", range(len(options)), format_func=lambda i: options[i])

                if st.button("📂  Load Event", use_container_width=True, type="primary"):
                    st.session_state["live_result"] = results_list[idx]["incident_report"]
                    st.rerun()

            except Exception as e:
                st.error(f"Failed to load results: {e}")

with right:
    result = st.session_state.get("live_result")

    if not result:
        st.markdown("""
        <div class="empty-state">
            <div class="empty-icon">🛡</div>
            <div class="empty-title">Awaiting analysis</div>
            <div class="empty-sub">Paste a log and click <strong>Run Analysis</strong><br>to see the agent pipeline execute in real time.</div>
        </div>""", unsafe_allow_html=True)
    else:
        render_trace(result)
        st.divider()
        render_incident(result)
        render_playbook(result)
