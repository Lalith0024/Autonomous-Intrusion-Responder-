"""Page 1: Live Analysis — paste a log or pick from CICIDS dataset."""

import json
import time
from pathlib import Path

import httpx
import streamlit as st

API_BASE = "http://127.0.0.1:8000"
RESULTS_PATH = Path("data/results/batch_results.json")
SAMPLE_LOG = "Mar 18 22:00:01 server sshd[1234]: Failed password for root from 45.33.32.156 port 54832 ssh2"

SEV_CLASS = {
    "critical": "sev-critical",
    "high": "sev-high",
    "medium": "sev-medium",
    "low": "sev-low",
    "info": "sev-info",
}

NODE_DESC_TEMPLATES = {
    "triage_node": lambda d: f"Analyzed log — identified <b>{d.get('attack_type','?').replace('_',' ').title()}</b> with <b>{d.get('confidence_score',0):.0%}</b> confidence",
    "severity_router": lambda d: f"Routed to <b>{'human review' if d.get('needs_human_review') else 'response agent' if d.get('response_plan') else 'END'}</b> based on severity and confidence",
    "response_agent": lambda d: f"Generated <b>{len((d.get('response_plan') or {}).get('response_steps', []))}-step</b> containment playbook",
    "human_review_node": lambda _: "Flagged for analyst review — confidence below threshold",
}


def _sev_pill(sev: str) -> str:
    cls = SEV_CLASS.get(sev.lower(), "sev-info")
    return f'<span class="{cls}">{sev.upper()}</span>'


def _call_api(payload: dict) -> dict | None:
    try:
        with httpx.Client(timeout=60.0) as client:
            resp = client.post(f"{API_BASE}/analyze", json=payload)
        if resp.status_code == 200:
            return resp.json()
        st.error(f"API returned {resp.status_code}: {resp.text[:200]}")
    except httpx.ConnectError:
        st.error("Cannot reach the API. Make sure FastAPI is running: `python run.py`")
    except httpx.ReadTimeout:
        st.error("Request timed out. The LLM may be slow — try again.")
    return None


def render_trace(data: dict) -> None:
    st.markdown('<div class="section-label">EXECUTION TRACE</div>', unsafe_allow_html=True)
    placeholder = st.empty()
    rendered = []

    for node in data.get("graph_path", []):
        time.sleep(0.3)
        desc_fn = NODE_DESC_TEMPLATES.get(node)
        desc = desc_fn(data) if desc_fn else node

        rendered.append(f"""
        <div class="trace-step">
            <div class="trace-check">✓</div>
            <div>
                <div class="trace-node">{node.replace('_', ' ').title()}</div>
                <div class="trace-desc">{desc}</div>
            </div>
        </div>""")
        placeholder.markdown("".join(rendered), unsafe_allow_html=True)

    if data.get("needs_human_review"):
        st.markdown("""
        <div class="review-banner" style="margin-top:8px;">
            ⚠ Low confidence detection — flagged for human review
        </div>""", unsafe_allow_html=True)


def render_incident(data: dict) -> None:
    st.markdown('<div class="section-label">INCIDENT REPORT</div>', unsafe_allow_html=True)

    sev = data.get("severity", "info")
    conf = data.get("confidence_score", 0)
    attack = data.get("attack_type", "unknown").replace("_", " ").title()
    action = data.get("recommended_action", "monitor").replace("_", " ").title()

    # Three metric cards
    c1, c2, c3 = st.columns(3)
    with c1:
        with st.container(border=True):
            st.markdown('<div class="stat-lbl">Attack Type</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="stat-val" style="font-size:1.2rem;">{attack}</div>', unsafe_allow_html=True)
    with c2:
        with st.container(border=True):
            st.markdown('<div class="stat-lbl">Severity</div>', unsafe_allow_html=True)
            st.markdown(f'<div style="margin-top:4px;">{_sev_pill(sev)}</div>', unsafe_allow_html=True)
    with c3:
        with st.container(border=True):
            st.markdown('<div class="stat-lbl">Confidence</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="stat-val">{conf:.0%}</div>', unsafe_allow_html=True)
            st.progress(conf)

    # Recommended action
    with st.container(border=True):
        st.markdown('<div class="stat-lbl">Recommended Action</div>', unsafe_allow_html=True)
        st.markdown(f'<div style="font-weight:600; color:#1a1a1a; font-size:0.95rem;">{action}</div>', unsafe_allow_html=True)

    # Reasoning
    reasoning = data.get("reasoning", "")
    if reasoning:
        st.markdown('<div class="section-label">ANALYST REASONING</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="reasoning-block">{reasoning}</div>', unsafe_allow_html=True)

    # Indicators
    indicators = data.get("indicators", [])
    if indicators:
        st.markdown('<div class="section-label">INDICATORS OF COMPROMISE</div>', unsafe_allow_html=True)
        tags = " ".join(f'<span class="ioc-tag">{i}</span>' for i in indicators)
        st.markdown(tags, unsafe_allow_html=True)

    latency = data.get("processing_time_ms", 0)
    st.markdown(f'<div style="font-size:0.72rem; color:#9ca3af; margin-top:0.75rem;">Processed in {latency}ms · Event ID: {data.get("event_id","")[:8]}...</div>', unsafe_allow_html=True)


def render_playbook(data: dict) -> None:
    plan = data.get("response_plan")
    if not plan:
        return

    st.markdown('<div class="section-label">CONTAINMENT PLAYBOOK</div>', unsafe_allow_html=True)
    with st.container(border=True):
        for i, step in enumerate(plan.get("response_steps", []), 1):
            st.markdown(f"""
            <div class="step-row">
                <div class="step-num">{i}</div>
                <div class="step-text">{step}</div>
            </div>""", unsafe_allow_html=True)

        impact = plan.get("estimated_impact", "")
        if impact:
            st.markdown(f'<div class="impact-card" style="margin-top:12px;">Estimated Impact: {impact}</div>', unsafe_allow_html=True)

        if plan.get("escalate_to_tier2"):
            st.markdown('<div class="escalate-banner" style="margin-top:12px;">↑ Escalate to Tier 2 SOC Analyst immediately</div>', unsafe_allow_html=True)


# ── Main Layout ───────────────────────────────────────────────────────────────

st.markdown('<div class="section-label" style="margin-top:0;">LIVE ANALYSIS</div>', unsafe_allow_html=True)
st.markdown("# Analyze a Threat Event")
st.markdown('<p style="color:#6b7280; margin-bottom:1.5rem;">Paste a raw log or select from the analyzed CICIDS dataset. The full agent pipeline runs in real time.</p>', unsafe_allow_html=True)

left, right = st.columns([4, 6], gap="large")

with left:
    input_mode = st.radio("Input method", ["Paste Log", "From Dataset"], horizontal=True, label_visibility="collapsed")

    if input_mode == "Paste Log":
        raw_log = st.text_area(
            "Raw Log Entry",
            value=SAMPLE_LOG,
            height=130,
            placeholder="Paste a server log line here...",
            help="sshd, nginx, firewall, or any raw log format",
        )

        with st.expander("Log Metadata (optional)"):
            mc1, mc2 = st.columns(2)
            with mc1:
                src_ip = st.text_input("Source IP", "45.33.32.156")
                protocol = st.selectbox("Protocol", ["TCP", "UDP", "ICMP"])
            with mc2:
                dst_ip = st.text_input("Dest IP", "192.168.1.10")
                event_type = st.text_input("Event Type", "failed_login")
            dst_port = st.number_input("Destination Port", value=22, min_value=0, max_value=65535)

        run_clicked = st.button("Run Analysis", use_container_width=True, type="primary")
        st.markdown('<div style="font-size:0.75rem; color:#9ca3af; text-align:center; margin-top:6px;">Agent pipeline: Triage → Policy Router → Response Agent</div>', unsafe_allow_html=True)

        if run_clicked:
            payload = {
                "timestamp": "2026-04-02T00:00:00Z",
                "source_ip": src_ip,
                "destination_ip": dst_ip,
                "destination_port": int(dst_port),
                "protocol": protocol,
                "event_type": event_type,
                "raw_log": raw_log,
            }
            with st.spinner("Running agent pipeline..."):
                result = _call_api(payload)
            if result:
                st.session_state["live_result"] = result

    else:  # From Dataset
        if not RESULTS_PATH.exists():
            st.markdown("""
            <div class="empty-state">
                <div class="empty-state-title">No batch data yet</div>
                <div class="empty-state-sub">Run the batch analyzer first:<br><code>python src/data/batch_runner.py</code></div>
            </div>""", unsafe_allow_html=True)
        else:
            try:
                batch = json.loads(RESULTS_PATH.read_text())
                results_list = batch.get("results", [])

                options = [
                    f"{r['incident_report'].get('attack_type','?').replace('_',' ').title()} — {r['incident_report'].get('source_ip','?')} — {r['incident_report'].get('severity','?').upper()}"
                    for r in results_list
                ]

                selected_idx = st.selectbox("Select an analyzed event", range(len(options)), format_func=lambda i: options[i])

                if st.button("Load Event", use_container_width=True, type="primary"):
                    st.session_state["live_result"] = results_list[selected_idx]["incident_report"]

            except Exception as e:
                st.error(f"Failed to load batch results: {e}")

with right:
    result = st.session_state.get("live_result")

    if not result:
        st.markdown("""
        <div class="empty-state" style="margin-top:4rem;">
            <div style="font-size:2rem; margin-bottom:1rem; color:#d1d5db;">🛡</div>
            <div class="empty-state-title">Results will appear here after analysis</div>
            <div class="empty-state-sub">The agent will show its reasoning and decision path</div>
        </div>""", unsafe_allow_html=True)
    else:
        render_trace(result)
        st.divider()
        render_incident(result)
        render_playbook(result)
