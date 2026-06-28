"""AIR V2 — Live Analysis Page.

Terminal-style log input, real-time execution trace with tool calls,
incident report cards, memory context display, and containment playbook.
Clean light-mode interface for professional analysts.
"""

import streamlit as st
import json
import time
from pathlib import Path
import httpx
import os

from src.core.config import settings
from src.streamlit_app.layout import inject_ui, get_severity_badge, get_severity_accent

st.set_page_config(page_title="AIR — Live Analyst", layout="wide", initial_sidebar_state="expanded")
inject_ui()

API_BASE = os.getenv("API_BASE", "http://127.0.0.1:8000")
RESULTS_PATH = Path(settings.BATCH_RESULTS_PATH)
SAMPLE_LOG = "Mar 18 22:00:01 server sshd[1234]: Failed password for root from 45.33.32.156 port 54832 ssh2 — 47 failed attempts in 60 seconds"

NODE_LABELS = {
    "investigation_node": "🔍 Checking Data",
    "triage_node":        "🧠 Thinking",
    "severity_router":    "🔀 Decision Point",
    "response_agent":     "🛡️ Taking Action",
    "human_review_node":  "👤 Specialist Review",
    "memory_persist_node": "💾 Saving Info",
}


def _call_api(payload: dict) -> dict | None:
    try:
        resp = httpx.post(f"{API_BASE}/analyze", json=payload, timeout=90.0)
        if resp.status_code == 200:
            return resp.json()
        st.error(f"API Error [{resp.status_code}]: {resp.text[:300]}")
    except httpx.ConnectError:
        st.error("System connection error. Please ensure the Analysis Engine is running.")
    except httpx.ReadTimeout:
        st.error("The analysis is taking too long. Please try again or check the system logs.")
    return None


def render_trace(data: dict):
    """Render the V2 execution trace with tool calls and timing."""
    trace = data.get("execution_trace")
    graph_path = data.get("graph_path", [])

    st.markdown('<div style="font-size:0.75rem; font-weight:800; color:#64748b; text-transform:uppercase; letter-spacing:0.1em; margin-bottom:1.25rem;">Analysis Progress</div>', unsafe_allow_html=True)

    if trace and trace.get("steps"):
        placeholder = st.empty()
        built = []

        for step in trace["steps"]:
            # Micro-delay for visual effect
            time.sleep(0.15)
            name = step.get("display_name", step.get("node_name", "?"))
            summary = step.get("output_summary", "")
            duration = step.get("duration_ms", 0)
            tools = step.get("tools_called", [])

            tools_html = ""
            if tools:
                for tc in tools:
                    tool_name = tc.get("tool_name", "?")
                    tool_dur = tc.get("duration_ms", 0)
                    tools_html += f'''
                    <div class="tool-call">
                        <div class="tool-name">⚙ EXECUTED: {tool_name}</div>
                        <div class="tool-result">Latency: {tool_dur}ms</div>
                    </div>'''

            built.append(f"""
            <div class="trace-item done">
                <div class="trace-title">{name}</div>
                <div class="trace-content">{summary}</div>
                {tools_html}
                <div class="trace-time">{duration}ms cycle</div>
            </div>""")
            placeholder.markdown("".join(built), unsafe_allow_html=True)

        total = trace.get("total_duration_ms", 0)
        st.markdown(f'<div style="text-align:right; font-size:0.75rem; color:#94a3b8; font-family:JetBrains Mono,monospace; margin-top:0.5rem; font-weight:700;">TOTAL PIPELINE: {total}ms</div>', unsafe_allow_html=True)

    else:
        # Fallback for simple paths
        placeholder = st.empty()
        built = []
        for node in graph_path:
            time.sleep(0.2)
            label = NODE_LABELS.get(node, node)
            built.append(f"""<div class="trace-item done"><div class="trace-title">{label}</div></div>""")
            placeholder.markdown("".join(built), unsafe_allow_html=True)

    if data.get("needs_human_review"):
        st.markdown('''<div class="alert alert-amber"><strong>⚠ ESCALATED:</strong> Automated confidence below threshold. Analyst verification required.</div>''', unsafe_allow_html=True)

    if data.get("blocked"):
        st.markdown(f'''<div class="alert alert-red"><strong>Locked:</strong> IP {data.get("source_ip", "?")} has been blocked for safety.</div>''', unsafe_allow_html=True)


def render_investigation(data: dict):
    """Render V2 IP investigation results."""
    ip_inv = data.get("ip_investigation")
    if not ip_inv:
        return

    st.markdown('<div class="section-header">🔍 Threat Intelligence</div>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f'''
        <div class="ui-card border-left-blue">
            <div class="ui-card-title">Origin</div>
            <div style="font-size:1.1rem; font-weight:800; color:#1e293b;">{ip_inv.get("country", "?")}</div>
            <div style="font-size:0.8rem; color:#64748b;">{ip_inv.get("city", "?")} — {ip_inv.get("isp", "?")}</div>
        </div>''', unsafe_allow_html=True)
    with c2:
        score = ip_inv.get("abuse_score", 0)
        score_color = "#dc2626" if score > 70 else "#d97706" if score > 40 else "#16a34a"
        st.markdown(f'''
        <div class="ui-card border-left-red">
            <div class="ui-card-title">Abuse Probability</div>
            <div style="font-size:1.75rem; font-weight:900; color:{score_color};">{score}%</div>
        </div>''', unsafe_allow_html=True)
    with c3:
        flags = []
        if ip_inv.get("is_proxy"):
            flags.append("Proxy")
        if ip_inv.get("is_tor"):
            flags.append("Tor")
        if ip_inv.get("is_known_malicious"):
            flags.append("Malicious")
        flags_str = " | ".join(flags) if flags else "CLEAN"
        flag_col = "#dc2626" if flags else "#16a34a"
        st.markdown(f'''
        <div class="ui-card border-left-slate">
            <div class="ui-card-title">Network Metadata</div>
            <div style="font-size:1rem; font-weight:800; color:{flag_col};">{flags_str}</div>
        </div>''', unsafe_allow_html=True)


def render_memory(data: dict):
    """Render V2 historical context."""
    history = data.get("historical_context", [])
    if not history:
        return

    st.markdown('<div class="section-header">🧠 Historical Context</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="alert alert-info">Found {len(history)} correlations in vector memory.</div>', unsafe_allow_html=True)

    for match in history[:3]:
        st.markdown(f'''
        <div style="display:flex; gap:1.5rem; padding:0.85rem 0; border-bottom:1px solid #f1f5f9; align-items:center;">
            <div style="color:#94a3b8; font-family:JetBrains Mono,monospace; font-size:0.75rem; width:100px;">{match.get("timestamp","?")[:10]}</div>
            <div style="color:#1e293b; font-weight:700; flex:1; font-size:0.9rem;">{match.get("attack_type","?").replace("_"," ").title()}</div>
            <div style="color:#2563eb; font-weight:800; font-size:0.8rem;">{match.get("similarity_score",0):.0%} MATCH</div>
        </div>''', unsafe_allow_html=True)


def render_incident(data: dict):
    """Render the incident report."""
    sev = data.get("severity", "info")
    conf = data.get("confidence_score", 0)
    attack = data.get("attack_type", "unknown").replace("_", " ").title()
    action = data.get("recommended_action", "monitor").replace("_", " ").title()

    accent = get_severity_accent(sev)
    badge = get_severity_badge(sev)

    st.markdown('<div class="section-header">Incident Analysis</div>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    c1.markdown(f'<div class="ui-card {accent}"><div class="ui-card-title">Classification</div><div class="ui-card-value" style="font-size:1.4rem;">{attack}</div></div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="ui-card {accent}"><div class="ui-card-title">Priority</div><div style="margin-top:0.5rem;">{badge}</div></div>', unsafe_allow_html=True)
    
    conf_color = "#16a34a" if conf >= 0.8 else "#d97706" if conf >= 0.6 else "#dc2626"
    c3.markdown(f'<div class="ui-card border-left-slate"><div class="ui-card-title">Confidence</div><div class="ui-card-value" style="color:{conf_color}; font-size:1.4rem;">{conf:.0%}</div></div>', unsafe_allow_html=True)

    st.markdown('<div class="ui-card-title" style="margin-top: 1rem;">Reasoning & Evidence</div>', unsafe_allow_html=True)
    st.markdown(f'''<div style="background:#ffffff; border:1px solid #e2e8f0; border-radius:12px; padding:1.5rem; font-size:0.95rem; color:#334155; line-height:1.8; box-shadow: 0 1px 2px rgba(0,0,0,0.05);"> {data.get("reasoning", "No analyst reasoning available.")} </div>''', unsafe_allow_html=True)

    st.markdown(f'''<div class="ui-card" style="margin-top:1.25rem;"><div class="ui-card-title">Automated Action</div><div style="font-size:1.1rem; font-weight:900; color:#2563eb;">{action}</div></div>''', unsafe_allow_html=True)


def render_playbook(data: dict):
    """Render the containment playbook."""
    plan = data.get("response_plan")
    if not plan:
        return

    steps = plan.get("response_steps", [])
    st.markdown('<div class="section-header">🛡️ Containment Playbook</div>', unsafe_allow_html=True)

    st.markdown('<div class="ui-card" style="padding: 1rem 2rem;">', unsafe_allow_html=True)
    steps_html = "".join(f'''<div class="playbook-step"><div class="playbook-num">{i}</div><div class="playbook-text">{step}</div></div>''' for i, step in enumerate(steps, 1))
    st.markdown(steps_html + '</div>', unsafe_allow_html=True)


# ── Page Layout ──
st.markdown('<div class="page-title">🔍 Live Analyst</div>', unsafe_allow_html=True)
st.markdown('<div class="page-subtitle">Real-time log ingestion and autonomous reasoning loop. Observe the multi-agent orchestration as it investigates and contains threats.</div>', unsafe_allow_html=True)

left, right = st.columns([4, 6], gap="large")

with left:
    mode = st.radio("Source", ["Manual Stream", "Demo Feed"], horizontal=True, label_visibility="collapsed")

    if "Manual" in mode:
        st.markdown('<div class="terminal-header"><div class="terminal-dot red"></div><div class="terminal-dot yellow"></div><div class="terminal-dot green"></div><span style="margin-left: 10px; font-size: 0.7rem; color: #94a3b8; font-family: JetBrains Mono, monospace; font-weight:700;">LOG_INGESTION_SHELL</span></div>', unsafe_allow_html=True)
        raw_log = st.text_area("Log", value=SAMPLE_LOG, height=140, label_visibility="collapsed")

        with st.expander("Advanced Ingestion Metadata"):
            mc1, mc2 = st.columns(2)
            src_ip = mc1.text_input("Source IP", "45.33.32.156")
            protocol = mc1.selectbox("Protocol", ["TCP", "UDP", "ICMP"])
            dst_ip = mc2.text_input("Destination", "10.0.0.5")
            dst_port = mc2.number_input("Port", value=22)

        if st.button("🚀 START ANALYSIS"):
            from datetime import datetime
            payload = {
                "timestamp": datetime.now().isoformat(),
                "source_ip": src_ip,
                "destination_ip": dst_ip,
                "destination_port": int(dst_port),
                "protocol": protocol,
                "event_type": "manual_ingestion",
                "raw_log": raw_log
            }
            with st.spinner("Analyzing threat..."):
                res = _call_api(payload)
            if res:
                st.session_state["live_result"] = res
                st.rerun()

    else:
        st.markdown('<div class="alert alert-info"><strong>CICIDS_2017_FEED:</strong> Pre-processed legitimate vs malicious flow data.</div>', unsafe_allow_html=True)
        if RESULTS_PATH.exists():
            try:
                batch = json.loads(RESULTS_PATH.read_text())
                results_list = batch.get("results", [])
                opts = [f"[{r['incident_report'].get('severity','-').upper()}] {r['incident_report'].get('attack_type','?').replace('_',' ').title()} | {r['incident_report'].get('source_ip','?')}" for r in results_list]
                if opts:
                    idx = st.selectbox("Historical Archive", range(len(opts)), format_func=lambda i: opts[i])
                    if st.button("📂 LOAD ARCHIVE"):
                        st.session_state["live_result"] = results_list[idx]["incident_report"]
                        st.rerun()
            except Exception as e:
                st.error(f"Error loading archive: {e}")

with right:
    result = st.session_state.get("live_result")
    if not result:
        st.markdown('''<div style="display:flex; flex-direction:column; align-items:center; justify-content:center; height:450px; border:2px dashed #e2e8f0; border-radius:20px; background:#ffffff; color:#94a3b8; text-align:center; padding:2rem;">
            <div style="font-size:3rem; margin-bottom:1rem;">🛰️</div>
            <div style="font-size:1.1rem; font-weight:800; color:#64748b; margin-bottom:0.5rem;">READY FOR INGESTION</div>
            <div style="font-size:0.9rem; max-width:320px;">Orchestrator is idle. Inject log data to activate the autonomous multi-agent pipeline.</div>
        </div>''', unsafe_allow_html=True)
    else:
        render_trace(result)
        render_investigation(result)
        render_memory(result)
        render_incident(result)
        render_playbook(result)
