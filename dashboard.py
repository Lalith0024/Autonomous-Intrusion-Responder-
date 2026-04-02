"""Streamlit dashboard for the Autonomous Intrusion Responder — Neat & Clean White Theme."""

import time

import httpx
import streamlit as st

API_BASE = "http://127.0.0.1:8000"

SAMPLE_LOG = "Mar 18 22:00:01 server sshd[1234]: Failed password for root from 45.33.32.156 port 54832 ssh2"

# Refined colors for a white theme
SEVERITY_COLORS = {
    "critical": {"bg": "#FEF2F2", "text": "#DC2626", "border": "#FECACA"},
    "high": {"bg": "#FFF7ED", "text": "#EA580C", "border": "#FED7AA"},
    "medium": {"bg": "#FEFCE8", "text": "#CA8A04", "border": "#FEF08A"},
    "low": {"bg": "#F0FDF4", "text": "#16A34A", "border": "#BBF7D0"},
    "info": {"bg": "#F0F9FF", "text": "#0284C7", "border": "#BAE6FD"},
}


def configure_page() -> None:
    st.set_page_config(
        page_title="Intrusion Responder",
        page_icon="🛡️",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&family=Inter:wght@400;500;600&display=swap');

        :root {
            --bg-page: #F8FAFC;
            --bg-card: #FFFFFF;
            --text-main: #0F172A;
            --text-muted: #64748B;
            --border-light: #E2E8F0;
            --accent-primary: #3B82F6;
            --radius-main: 16px;
        }

        .stApp {
            background-color: var(--bg-page);
            font-family: 'Outfit', sans-serif;
        }

        /* Sidebar Styling */
        section[data-testid="stSidebar"] {
            background-color: white !important;
            border-right: 1px solid var(--border-light);
        }

        .sidebar-title {
            font-size: 1.5rem;
            font-weight: 700;
            color: var(--text-main);
            letter-spacing: -0.01em;
            margin-bottom: 2rem;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        /* Typography */
        h1, h2, h3 {
            font-family: 'Outfit', sans-serif !important;
            color: var(--text-main) !important;
        }

        .section-label {
            font-size: 0.75rem;
            font-weight: 600;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 0.8rem;
        }

        /* Cards & Symmetry */
        .glass-card {
            background: white;
            border: 1px solid var(--border-light);
            border-radius: var(--radius-main);
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.02), 0 1px 2px rgba(0,0,0,0.06);
            transition: all 0.2s ease;
        }

        .glass-card:hover {
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
            border-color: #CBD5E1;
        }

        .metric-label {
            font-size: 0.85rem;
            color: var(--text-muted);
            margin-bottom: 0.4rem;
            font-weight: 500;
        }

        .metric-value {
            font-size: 1.25rem;
            font-weight: 600;
            color: var(--text-main);
        }

        /* Badges */
        .severity-badge {
            display: inline-flex;
            align-items: center;
            padding: 4px 12px;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.02em;
        }

        /* Log Area */
        textarea {
            font-family: 'JetBrains Mono', monospace !important;
            background-color: #F8FAFC !important;
            border: 1px solid var(--border-light) !important;
            border-radius: 12px !important;
            color: #334155 !important;
            padding: 1rem !important;
        }

        /* Response Steps */
        .step-container {
            display: flex;
            gap: 1rem;
            margin-bottom: 1rem;
            align-items: flex-start;
        }

        .step-number {
            flex-shrink: 0;
            width: 28px;
            height: 28px;
            background: #EFF6FF;
            color: var(--accent-primary);
            font-weight: 700;
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 0.85rem;
            border: 1px solid #DBEAFE;
        }

        .step-text {
            color: #334155;
            font-size: 0.95rem;
            line-height: 1.5;
            padding-top: 2px;
        }

        /* Path visualization */
        .path-node {
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 0.5rem;
        }

        .node-circle {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            border: 2px solid white;
            box-shadow: 0 0 0 1px #E2E8F0;
        }

        .node-label {
            font-family: 'Inter', sans-serif;
            font-size: 0.85rem;
            font-weight: 500;
        }

        .connector-line {
            width: 1px;
            height: 24px;
            background: #E2E8F0;
            margin-left: 5.5px;
            margin-top: -4px;
            margin-bottom: -4px;
        }

        /* Custom spacing for buttons */
        .stButton button {
            border-radius: 12px;
            padding: 0.6rem 2rem;
            font-weight: 600;
            transition: all 0.2s;
            background-color: var(--accent-primary);
            border: none;
        }

        .stButton button:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(59, 130, 246, 0.25);
            background-color: #2563EB;
        }

        /* Banner styling */
        .warning-banner {
            border-radius: 12px;
            padding: 1rem 1.25rem;
            border: 1px solid #FED7AA;
            background-color: #FFF7ED;
            color: #9A3412;
            display: flex;
            gap: 12px;
            align-items: center;
            margin-top: 1rem;
        }

        /* Progress Bar */
        .stProgress > div > div > div > div {
            background-color: var(--accent-primary);
        }

    </style>
    """, unsafe_allow_html=True)


def draw_sidebar(graph_path: list[str] | None) -> None:
    with st.sidebar:
        st.markdown('<div class="sidebar-title">🛡️ AIR OPS</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-label">AGENT FLOW</div>', unsafe_allow_html=True)

        nodes = [
            ("triage_node", "Triage Agent"),
            ("severity_router", "Policy Router"),
            ("response_agent", "Response Agent"),
            ("human_review_node", "Analyst Review"),
        ]

        for i, (node_id, node_label) in enumerate(nodes):
            active = node_id in (graph_path or [])
            dot_color = "#3B82F6" if active else "#E2E8F0"
            text_color = "#1E293B" if active else "#94A3B8"
            weight = "600" if active else "400"

            st.markdown(f"""
                <div class="path-node">
                    <div class="node-circle" style="background: {dot_color}"></div>
                    <div class="node-label" style="color: {text_color}; font-weight: {weight}">{node_label}</div>
                </div>
            """, unsafe_allow_html=True)

            if i < len(nodes) - 1:
                st.markdown('<div class="connector-line"></div>', unsafe_allow_html=True)

        st.divider()
        st.caption("v0.1.0 • Autonomous Intrusion Responder")


def render_header() -> None:
    st.markdown('<div class="section-label">SECURITY INCIDENT TRIAGE</div>', unsafe_allow_html=True)
    st.title("Autonomous Threat Analysis")
    st.markdown("<p style='color:#64748B; margin-top:-1rem; margin-bottom:2rem;'>Real-time analysis and containment with multi-agent orchestration.</p>", unsafe_allow_html=True)


def render_results(data: dict) -> None:
    # 1. Execution Trace Banner
    st.markdown('<div class="section-label">PIPELINE EXECUTION</div>', unsafe_allow_html=True)
    with st.status("Orchestrating agents...", expanded=False) as status:
        for node in data.get("graph_path", []):
            time.sleep(0.3)
            st.markdown(f"**✓ Processing complete at `{node}`**")
        status.update(label="Pipeline Successful", state="complete")

    st.markdown('<div style="height: 1.5rem"></div>', unsafe_allow_html=True)

    # 2. Main Metrics Row
    sev = data.get("severity", "info")
    colors = SEVERITY_COLORS.get(sev, SEVERITY_COLORS["info"])
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
            <div class="glass-card">
                <div class="metric-label">Detected Attack</div>
                <div class="metric-value">{data.get('attack_type', 'unknown').replace('_', ' ').title()}</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
            <div class="glass-card">
                <div class="metric-label">Criticality</div>
                <div class="severity-badge" style="background: {colors['bg']}; color: {colors['text']}; border: 1px solid {colors['border']}">
                    {sev.upper()}
                </div>
            </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
            <div class="glass-card">
                <div class="metric-label">Recommended Strategy</div>
                <div class="metric-value">{data.get('recommended_action', 'monitor').replace('_', ' ').title()}</div>
            </div>
        """, unsafe_allow_html=True)

    # 3. Decision Reasoning & Confidence
    c1, c2 = st.columns([2, 1])
    with c1:
        st.markdown('<div class="section-label">ANALYST REASONING</div>', unsafe_allow_html=True)
        st.markdown(f"<div class='glass-card' style='color:#334155; line-height:1.6;'>{data.get('reasoning', '')}</div>", unsafe_allow_html=True)
    
    with c2:
        st.markdown('<div class="section-label">DETECTION CONFIDENCE</div>', unsafe_allow_html=True)
        conf = data.get("confidence_score", 0)
        st.markdown(f"""
            <div class="glass-card" style="text-align: center;">
                <div style="font-size: 2rem; font-weight: 700; color: #3B82F6;">{conf:.0%}</div>
                <div style="margin-top: 10px;">
                    <div style="height: 6px; background: #F1F5F9; border-radius: 3px;">
                        <div style="height: 6px; width: {conf*100}%; background: #3B82F6; border-radius: 3px;"></div>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

    # 4. IoCs
    st.markdown('<div class="section-label">INDICATORS OF COMPROMISE</div>', unsafe_allow_html=True)
    iocs = data.get("indicators", [])
    if iocs:
        st.markdown(" ".join([f"<code style='background:#F1F5F9; color:#475569; padding: 4px 8px; border-radius:6px; margin-right:8px;'>{i}</code>" for i in iocs]), unsafe_allow_html=True)
    else:
        st.caption("No specific IoCs identified.")

    st.markdown('<div style="height: 2.5rem"></div>', unsafe_allow_html=True)

    # 5. Response Plan (The Response Agent Output)
    plan = data.get("response_plan")
    needs_review = data.get("needs_human_review", False)

    if needs_review:
        st.markdown(f"""
            <div class="warning-banner">
                <span style="font-size: 1.2rem">⚠️</span>
                <div>
                    <div style="font-weight: 600;">Confidence Threshold Not Met</div>
                    <div style="font-size: 0.9rem;">{data.get('human_review_message', 'Flagged for manual review.')}</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
    elif plan:
        st.divider()
        st.markdown('<div class="section-label">CONTAINMENT PLAYBOOK</div>', unsafe_allow_html=True)
        st.subheader("Step-by-Step Response")
        
        for i, step in enumerate(plan.get("response_steps", []), 1):
            st.markdown(f"""
                <div class="step-container">
                    <div class="step-number">{i}</div>
                    <div class="step-text">{step}</div>
                </div>
            """, unsafe_allow_html=True)
        
        st.markdown(f"""
            <div class="glass-card" style="margin-top: 2rem; border-left: 4px solid #3B82F6;">
                <div class="metric-label">Estimated Impact / Blast Radius</div>
                <div style="color: #334155; font-size: 0.95rem;">{plan.get('estimated_impact', '')}</div>
            </div>
        """, unsafe_allow_html=True)

        if plan.get("escalate_to_tier2"):
            st.markdown("""
                <div class="warning-banner" style="background-color: #FEF2F2; border-color: #FECACA; color: #991B1B;">
                    <span style="font-size: 1.2rem">🔺</span>
                    <div>
                        <div style="font-weight: 600;">Escalation Needed</div>
                        <div style="font-size: 0.9rem;">This incident requires immediate Tier 2 analyst intervention.</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)


def main() -> None:
    configure_page()
    
    last_res = st.session_state.get("last_result")
    draw_sidebar(last_res.get("graph_path") if last_res else None)
    
    render_header()
    
    # 1. Log Input Section
    st.markdown('<div class="section-label">RAW LOG ENTRY</div>', unsafe_allow_html=True)
    raw_log = st.text_area(
        "Log Data",
        value=SAMPLE_LOG,
        height=120,
        label_visibility="collapsed",
        placeholder="Paste server logs here (sshd, apache, nginx, firewall)..."
    )

    with st.expander("⚙️ Log Metadata", expanded=False):
        c1, c2, c3 = st.columns(3)
        with c1:
            src_ip = st.text_input("Source IP", "45.33.32.156")
            protocol = st.text_input("Protocol", "TCP")
        with c2:
            dst_ip = st.text_input("Destination IP", "192.168.1.10")
            event_type = st.text_input("Event Type", "failed_login")
        with c3:
            dst_port = st.number_input("Port", 22)

    st.markdown('<div style="height: 1rem"></div>', unsafe_allow_html=True)
    
    if st.button("RUN ANALYSIS", use_container_width=True, type="primary"):
        payload = {
            "timestamp": "2026-04-02T00:00:00Z",
            "source_ip": src_ip,
            "destination_ip": dst_ip,
            "destination_port": int(dst_port),
            "protocol": protocol,
            "event_type": event_type,
            "raw_log": raw_log
        }
        
        try:
            with st.spinner("Processing through agent graph..."):
                resp = httpx.post(f"{API_BASE}/analyze", json=payload, timeout=60.0)
                if resp.status_code == 200:
                    st.session_state["last_result"] = resp.json()
                else:
                    st.error(f"Error: {resp.status_code}")
        except Exception as e:
            st.error(f"Failed to connect to backend: {e}")

    # 2. Results Section
    if st.session_state.get("last_result"):
        st.markdown('<div style="height: 3rem"></div>', unsafe_allow_html=True)
        render_results(st.session_state["last_result"])


if __name__ == "__main__":
    main()
