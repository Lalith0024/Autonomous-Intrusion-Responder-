import streamlit as st
import json
import time
from pathlib import Path
import httpx
import sys

# Fix import path for UI module
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from src.streamlit_app.layout import inject_ui, get_severity_badge, get_severity_accent

st.set_page_config(page_title="AIR - Live Analysis", layout="wide", initial_sidebar_state="expanded")
inject_ui()

API_BASE = "http://127.0.0.1:8000"
RESULTS_PATH = Path("data/results/batch_results.json")
SAMPLE_LOG = "Mar 18 22:00:01 server sshd[1234]: Failed password for root from 45.33.32.156 port 54832 ssh2 — 47 failed attempts in 60 seconds"

NODE_LABELS = {
    "triage_node":       "Triage Agent",
    "severity_router":   "Policy Router",
    "response_agent":    "Response Agent",
    "human_review_node": "Human Review",
}

NODE_DESC = {
    "triage_node":       lambda d: f"Classified as <span class='text-slate' style='font-weight:600;'>{d.get('attack_type','?').replace('_',' ').title()}</span>, Confidence: {d.get('confidence_score',0):.0%}",
    "severity_router":   lambda d: f"Conditional routing applied. Delegating to <span class='text-slate' style='font-weight:600;'>{'Human Review' if d.get('needs_human_review') else 'Response Agent' if d.get('response_plan') else 'Terminal State'}</span>.",
    "response_agent":    lambda d: f"Formulated <span class='text-blue'>{len((d.get('response_plan') or {}).get('response_steps', []))} containment steps</span>.",
    "human_review_node": lambda _: "Confidence below operational threshold. Flagged for direct analyst intervention.",
}

def _call_api(payload: dict) -> dict | None:
    try:
        resp = httpx.post(f"{API_BASE}/analyze", json=payload, timeout=60.0)
        if resp.status_code == 200:
            return resp.json()
        st.error(f"API Error [{resp.status_code}]: {resp.text[:300]}")
    except httpx.ConnectError:
        st.error("Connection Failed. Ensure FastAPI is active on 127.0.0.1:8000.")
    except httpx.ReadTimeout:
        st.error("Request Timeout. Groq inference rate limit or heavy load.")
    return None

def render_trace(data: dict):
    st.markdown('<div style="font-size:0.8rem; font-weight:700; color:#64748b; text-transform:uppercase; letter-spacing:0.05em; margin-bottom:1rem;">Execution Trace</div>', unsafe_allow_html=True)
    placeholder = st.empty()
    built = []
    graph_path = data.get("graph_path", [])

    for i, node in enumerate(graph_path):
        time.sleep(0.3)
        label = NODE_LABELS.get(node, node)
        desc_fn = NODE_DESC.get(node)
        desc = desc_fn(data) if desc_fn else ""
        
        built.append(f"""
        <div class="trace-item done">
            <div class="trace-title">{label}</div>
            <div class="trace-content">{desc}</div>
        </div>""")
        placeholder.markdown("".join(built), unsafe_allow_html=True)
    
    if data.get("needs_human_review"):
        st.markdown('''
        <div class="alert alert-amber" style="margin-top: 1rem;">
            <strong>Low Confidence Flag:</strong> Event has been routed for manual analyst review. Autonomous response blocked.
        </div>
        ''', unsafe_allow_html=True)

def render_incident(data: dict):
    sev = data.get("severity", "info")
    conf = data.get("confidence_score", 0)
    attack = data.get("attack_type", "unknown").replace("_", " ").title()
    action = data.get("recommended_action", "monitor").replace("_", " ").title()
    
    accent = get_severity_accent(sev)
    badge = get_severity_badge(sev)
    
    st.markdown('<div class="section-header" style="margin-top: 2rem;">Incident Report</div>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f'<div class="ui-card {accent}"><div class="ui-card-title">Attack Type</div><div class="ui-card-value">{attack}</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="ui-card {accent}"><div class="ui-card-title">Assessed Severity</div><div style="margin-top:0.75rem;">{badge}</div></div>', unsafe_allow_html=True)
    with c3:
        color = "#22c55e" if conf >= 0.8 else "#f59e0b" if conf >= 0.6 else "#ef4444"
        st.markdown(f'''
        <div class="ui-card border-left-slate">
            <div class="ui-card-title">Agent Confidence</div>
            <div class="ui-card-value" style="color:{color};">{conf:.0%}</div>
        </div>
        ''', unsafe_allow_html=True)

    left, right = st.columns([3, 2])
    with left:
        st.markdown('<div class="ui-card-title" style="margin-top: 1rem;">Agent Reasoning</div>', unsafe_allow_html=True)
        st.markdown(f'<div style="background:#f1f5f9; border:1px solid #e2e8f0; border-radius:8px; padding:1.25rem; font-size:0.9rem; color:#475569; line-height:1.6;">{data.get("reasoning", "No context provided.")}</div>', unsafe_allow_html=True)
    with right:
        st.markdown('<div class="ui-card-title" style="margin-top: 1rem;">Enforced Action</div>', unsafe_allow_html=True)
        action_col = "#22c55e" if "block" in action.lower() or "quarantine" in action.lower() else "#3b82f6"
        st.markdown(f'<div class="ui-card"><div style="font-size:1.15rem; font-weight:800; color:{action_col};">{action}</div><div style="font-size:0.75rem; color:#94a3b8; margin-top:0.5rem; text-transform:uppercase; letter-spacing:0.05em;">Orchestrated Decision</div></div>', unsafe_allow_html=True)

    iocs = data.get("indicators", [])
    if iocs:
        st.markdown('<div class="ui-card-title" style="margin-top: 1.5rem;">Extracted Indicators (IOCs)</div>', unsafe_allow_html=True)
        tags = "".join(f'<span class="mono" style="background:#f8fafc; border:1px solid #cbd5e1; padding:0.25rem 0.75rem; border-radius:4px; margin:0 0.5rem 0.5rem 0; display:inline-block; color:#0f172a;">{i}</span>' for i in iocs)
        st.markdown(f'<div>{tags}</div>', unsafe_allow_html=True)

def render_playbook(data: dict):
    plan = data.get("response_plan")
    if not plan:
        return

    steps = plan.get("response_steps", [])
    escalate = plan.get("escalate_to_tier2", False)
    impact = plan.get("estimated_impact", "")
    
    st.markdown('<div class="section-header" style="margin-top: 2.5rem;">Containment Playbook</div>', unsafe_allow_html=True)

    st.markdown(f'''
    <div class="alert alert-info">
        <strong>Response Plan Initiated</strong> &mdash; Generated sequence of {len(steps)} operational steps.
    </div>''', unsafe_allow_html=True)

    st.markdown('<div class="ui-card" style="padding: 0.5rem 1.5rem;">', unsafe_allow_html=True)
    steps_html = "".join(f"""
        <div class="playbook-step">
            <div class="playbook-num">{i}</div>
            <div class="playbook-text">{step}</div>
        </div>""" for i, step in enumerate(steps, 1))
    st.markdown(steps_html + '</div>', unsafe_allow_html=True)

    if impact:
        st.markdown(f'<div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:8px; padding:1rem 1.25rem; font-size:0.85rem; color:#334155; margin-top:1rem;"><strong>Estimated Infrastructure Impact:</strong> {impact}</div>', unsafe_allow_html=True)

    if escalate:
        st.markdown('''
        <div class="alert alert-red" style="margin-top: 1rem;">
            <strong>Immediate Escalation Required</strong> &mdash; Tier 2 SOC Analyst intervention mandatory.
        </div>''', unsafe_allow_html=True)

st.markdown('<div class="page-title">Live Analysis</div>', unsafe_allow_html=True)
st.markdown('<div class="page-subtitle">Inject raw network streams or query historical dataset to observe the autonomous pipeline. <br><strong>Note:</strong> Inference triggers only upon explicit execution.</div>', unsafe_allow_html=True)

left, right = st.columns([4, 5], gap="large")

with left:
    mode = st.radio("Input Source", ["Manual Input", "Demo Dataset"], horizontal=True, label_visibility="collapsed")

    if "Manual" in mode:
        st.markdown('<div style="font-size:0.8rem; font-weight:600; color:#64748b; margin-top:0.5rem;">Raw Feed</div>', unsafe_allow_html=True)
        raw_log = st.text_area(
            "Log Feed",
            value=SAMPLE_LOG,
            height=120,
            label_visibility="collapsed"
        )
        
        with st.expander("Overridden Network Metadata (Optional)"):
            mc1, mc2 = st.columns(2)
            src_ip = mc1.text_input("Source IP", "45.33.32.156")
            protocol = mc1.selectbox("Protocol", ["TCP", "UDP", "ICMP"])
            dst_ip = mc2.text_input("Destination IP", "192.168.1.10")
            event_type = mc2.text_input("Event Signature", "failed_login")
            dst_port = st.number_input("Target Port", value=22)

        st.markdown('<div style="margin: 1.5rem 0 0.5rem;"></div>', unsafe_allow_html=True)
        clicked = st.button("Execute Pipeline", use_container_width=True, type="primary")

        if clicked:
            payload = {
                "timestamp": "2026-04-02T00:00:00Z",
                "source_ip": src_ip, "destination_ip": dst_ip,
                "destination_port": int(dst_port), "protocol": protocol,
                "event_type": event_type, "raw_log": raw_log,
            }
            with st.spinner("Executing Inference..."):
                result = _call_api(payload)
            if result:
                st.session_state["live_result"] = result
                st.rerun()

    else:
        st.markdown('<div class="alert alert-info" style="margin-top: 1rem;"><strong>Using Demo Dataset (CICIDS 2017)</strong> &mdash; This is processed historical data. Only re-run an event if you wish to see tracing.</div>', unsafe_allow_html=True)
        if not RESULTS_PATH.exists():
            st.markdown('<div class="alert alert-amber">Dataset results are currently generating in the background. Please wait a moment.</div>', unsafe_allow_html=True)
        else:
            try:
                batch = json.loads(RESULTS_PATH.read_text())
                results_list = batch.get("results", [])
                
                options = [
                    f"[{r['incident_report'].get('severity','-').upper()}] {r['incident_report'].get('attack_type','?').replace('_',' ').title()} - {r['incident_report'].get('source_ip','?')}"
                    for r in results_list
                ]
                idx = st.selectbox("Select Historical Event", range(len(options)), format_func=lambda i: options[i])

                st.markdown('<div style="margin: 1.5rem 0 0.5rem;"></div>', unsafe_allow_html=True)
                if st.button("Load Pre-Analysed State", use_container_width=True, type="primary"):
                    st.session_state["live_result"] = results_list[idx]["incident_report"]
                    st.rerun()

            except Exception as e:
                st.error(f"Failed to mount dataset: {e}")

with right:
    result = st.session_state.get("live_result")

    if not result:
        st.markdown("""
        <div style="display:flex; flex-direction:column; align-items:center; justify-content:center; height:300px; border:2px dashed #cbd5e1; border-radius:12px; background:#f8fafc; margin-top:1rem;">
            <div style="font-size:1.1rem; font-weight:600; color:#64748b; margin-bottom:0.5rem;">Awaiting Data Feed</div>
            <div style="font-size:0.85rem; color:#94a3b8; text-align:center;">Execute manual inference or load from dataset to observe the LangGraph pipeline execution matrix.</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        render_trace(result)
        render_incident(result)
        render_playbook(result)
