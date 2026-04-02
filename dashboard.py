"""Dashboard entry point — global design system, branded sidebar, page config."""

import json
from pathlib import Path

import streamlit as st

st.set_page_config(
    page_title="AIR — Autonomous Intrusion Responder",
    page_icon="🛡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ══════════════════════════════════════════════════════════════════════════════
# GLOBAL DESIGN SYSTEM — shared by all pages via this entry point CSS injection
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

/* ── Reset & Base ── */
*, *::before, *::after { box-sizing: border-box; margin: 0; }
html, body, .stApp {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    background-color: #f0f2f5;
    color: #111827;
}

/* ── Remove Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 1.5rem 2rem 2rem; max-width: none; }

/* ── Dark Sidebar ── */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%) !important;
    border-right: 1px solid #334155;
    min-width: 260px !important;
}
section[data-testid="stSidebar"] * { color: #cbd5e1 !important; }
section[data-testid="stSidebar"] .stMarkdown { color: #cbd5e1 !important; }

/* ── Logo ── */
.air-logo {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 1.25rem 0 1rem;
    border-bottom: 1px solid #334155;
    margin-bottom: 1.25rem;
}
.air-logo-icon {
    width: 40px; height: 40px;
    background: linear-gradient(135deg, #10b981, #059669);
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.2rem;
    box-shadow: 0 0 20px rgba(16,185,129,0.3);
    flex-shrink: 0;
}
.air-logo-text { line-height: 1.2; }
.air-logo-name { font-size: 1.1rem; font-weight: 800; color: #f1f5f9 !important; letter-spacing: -0.02em; }
.air-logo-sub  { font-size: 0.68rem; color: #64748b !important; font-weight: 500; text-transform: uppercase; letter-spacing: 0.06em; }

/* ── Sidebar Nav Labels ── */
.nav-label {
    font-size: 0.62rem; font-weight: 700; color: #475569 !important;
    text-transform: uppercase; letter-spacing: 0.1em;
    padding: 0.5rem 0 0.4rem;
}

/* ── Pipeline diagram nodes ── */
.pipeline-wrap { padding: 0.75rem 0; }
.p-node {
    display: flex; align-items: center; gap: 10px;
    padding: 7px 10px; border-radius: 8px; margin-bottom: 4px;
    transition: background 0.15s;
}
.p-node:hover { background: rgba(255,255,255,0.05); }
.p-node-dot {
    width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0;
}
.p-node-text { font-size: 0.8rem; font-weight: 500; color: #94a3b8 !important; }
.p-node.active .p-node-text { color: #f1f5f9 !important; font-weight: 600; }
.p-connector {
    width: 1px; height: 16px; background: #334155;
    margin-left: 13px; margin-bottom: 2px;
}

/* ── Status dot ── */
.status-dot {
    display: inline-block; width: 8px; height: 8px;
    border-radius: 50%; margin-right: 6px;
    animation: pulse 2s infinite;
}
.status-dot.green { background: #10b981; box-shadow: 0 0 0 0 rgba(16,185,129,0.4); }
.status-dot.red   { background: #ef4444; box-shadow: 0 0 0 0 rgba(239,68,68,0.4); animation: pulse-red 2s infinite; }
@keyframes pulse {
    0%   { box-shadow: 0 0 0 0 rgba(16,185,129,0.4); }
    70%  { box-shadow: 0 0 0 6px rgba(16,185,129,0); }
    100% { box-shadow: 0 0 0 0 rgba(16,185,129,0); }
}
@keyframes pulse-red {
    0%   { box-shadow: 0 0 0 0 rgba(239,68,68,0.4); }
    70%  { box-shadow: 0 0 0 6px rgba(239,68,68,0); }
    100% { box-shadow: 0 0 0 0 rgba(239,68,68,0); }
}

/* ── Main Content Cards ── */
.card {
    background: #ffffff;
    border: 1px solid #e5e7eb;
    border-radius: 14px;
    padding: 1.25rem 1.5rem;
    margin-bottom: 1rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}
.card-accent-green  { border-left: 4px solid #10b981; }
.card-accent-red    { border-left: 4px solid #ef4444; }
.card-accent-amber  { border-left: 4px solid #f59e0b; }
.card-accent-blue   { border-left: 4px solid #3b82f6; }
.card-accent-purple { border-left: 4px solid #8b5cf6; }

/* ── Section Labels ── */
.sec-label {
    font-size: 0.65rem; font-weight: 700; color: #6b7280;
    text-transform: uppercase; letter-spacing: 0.1em;
    margin-bottom: 0.6rem; margin-top: 1.5rem;
}

/* ── Page Header ── */
.page-header { margin-bottom: 1.5rem; }
.page-header h1 {
    font-size: 1.6rem; font-weight: 800; color: #111827;
    letter-spacing: -0.03em; margin-bottom: 4px;
}
.page-header p { font-size: 0.88rem; color: #6b7280; font-weight: 400; }

/* ── Severity Pills ── */
.pill {
    display: inline-flex; align-items: center; gap: 5px;
    padding: 3px 10px; border-radius: 9999px;
    font-size: 0.7rem; font-weight: 700;
    text-transform: uppercase; letter-spacing: 0.05em;
}
.pill-critical { background: #fef2f2; color: #dc2626; border: 1px solid #fecaca; }
.pill-high     { background: #fff7ed; color: #c2410c; border: 1px solid #fdba74; }
.pill-medium   { background: #fffbeb; color: #b45309; border: 1px solid #fcd34d; }
.pill-low      { background: #f0fdf4; color: #15803d; border: 1px solid #86efac; }
.pill-info     { background: #eff6ff; color: #1d4ed8; border: 1px solid #93c5fd; }
.pill-pass     { background: #f0fdf4; color: #15803d; border: 1px solid #86efac; }
.pill-fail     { background: #fef2f2; color: #dc2626; border: 1px solid #fecaca; }

/* ── Metric Cards ── */
.metric-card {
    background: #fff; border: 1px solid #e5e7eb; border-radius: 12px;
    padding: 1.1rem 1.25rem;
    display: flex; flex-direction: column; gap: 4px;
}
.metric-val   { font-size: 1.8rem; font-weight: 800; letter-spacing: -0.04em; line-height: 1; }
.metric-label { font-size: 0.72rem; font-weight: 600; color: #9ca3af; text-transform: uppercase; letter-spacing: 0.05em; }
.metric-green { color: #10b981; }
.metric-red   { color: #ef4444; }
.metric-amber { color: #f59e0b; }
.metric-blue  { color: #3b82f6; }
.metric-dark  { color: #111827; }

/* ── Trace Steps ── */
.trace-step {
    display: flex; align-items: flex-start; gap: 12px;
    padding: 10px 14px; border-radius: 10px; margin-bottom: 6px;
    border: 1px solid #e5e7eb; background: #f9fafb;
    transition: all 0.2s;
}
.trace-step.done   { background: #f0fdf4; border-color: #86efac; }
.trace-step.active { background: #fffbeb; border-color: #fcd34d; }
.trace-icon { font-size: 0.9rem; flex-shrink: 0; margin-top: 1px; }
.trace-node   { font-size: 0.82rem; font-weight: 700; color: #111827; }
.trace-desc   { font-size: 0.76rem; color: #6b7280; margin-top: 2px; line-height: 1.4; }
.trace-step.done .trace-node { color: #15803d; }

/* ── IoC Tags ── */
.ioc-wrap { display: flex; flex-wrap: wrap; gap: 6px; margin: 0.5rem 0; }
.ioc-tag {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem; font-weight: 500;
    background: #f1f5f9; color: #334155;
    border: 1px solid #cbd5e1;
    border-radius: 6px; padding: 3px 8px;
}

/* ── Playbook Steps ── */
.playbook-step {
    display: flex; align-items: flex-start; gap: 12px;
    padding: 10px 0; border-bottom: 1px solid #f3f4f6;
}
.playbook-step:last-child { border-bottom: none; }
.step-num {
    width: 24px; height: 24px; border-radius: 6px; flex-shrink: 0;
    background: #eff6ff; color: #2563eb; border: 1px solid #bfdbfe;
    font-size: 0.72rem; font-weight: 800;
    display: flex; align-items: center; justify-content: center;
}
.step-txt { font-size: 0.85rem; color: #374151; line-height: 1.5; }

/* ── Banners ── */
.banner {
    border-radius: 10px; padding: 12px 16px;
    display: flex; align-items: flex-start; gap: 10px;
    font-size: 0.84rem; font-weight: 500; margin: 0.75rem 0;
}
.banner-green  { background: #f0fdf4; border: 1px solid #bbf7d0; color: #15803d; }
.banner-red    { background: #fef2f2; border: 1px solid #fecaca; color: #dc2626; }
.banner-amber  { background: #fffbeb; border: 1px solid #fcd34d; color: #b45309; }
.banner-purple { background: #faf5ff; border: 1px solid #e9d5ff; color: #7c3aed; }
.banner-icon   { font-size: 1rem; flex-shrink: 0; margin-top: 1px; }

/* ── Reasoning ── */
.reasoning {
    background: #f9fafb; border: 1px solid #e5e7eb; border-radius: 10px;
    padding: 12px 16px; font-size: 0.84rem; color: #4b5563;
    line-height: 1.65; font-style: italic;
}

/* ── Impact Card ── */
.impact-box {
    background: #eff6ff; border: 1px solid #bfdbfe; border-radius: 10px;
    padding: 10px 14px; font-size: 0.84rem; color: #1e40af; margin-top: 0.75rem;
}

/* ── Empty state ── */
.empty-state {
    display: flex; flex-direction: column; align-items: center;
    justify-content: center; padding: 4rem 2rem; color: #9ca3af;
    text-align: center;
}
.empty-icon  { font-size: 3rem; margin-bottom: 1rem; opacity: 0.4; }
.empty-title { font-size: 1rem; font-weight: 600; color: #6b7280; margin-bottom: 0.5rem; }
.empty-sub   { font-size: 0.82rem; line-height: 1.5; }

/* ── Confidence bar ── */
.conf-bar-wrap { height: 6px; background: #e5e7eb; border-radius: 9999px; overflow: hidden; margin-top: 6px; }
.conf-bar-fill { height: 6px; border-radius: 9999px; }

/* ── Eval cards ── */
.eval-card {
    background: #fff; border: 1px solid #e5e7eb; border-radius: 12px;
    padding: 1rem 1.25rem; margin-bottom: 8px;
    display: flex; align-items: center; gap: 1rem;
}
.eval-card.pass { border-left: 4px solid #10b981; }
.eval-card.fail { border-left: 4px solid #ef4444; }

/* ── Confusion row ── */
.conf-row {
    display: flex; align-items: center; gap: 12px;
    padding: 8px 12px; border-radius: 8px; margin-bottom: 4px; font-size: 0.82rem;
}
.conf-row.match   { background: #f0fdf4; }
.conf-row.nomatch { background: #fef2f2; }
.conf-row-icon { font-size: 0.9rem; flex-shrink: 0; width: 20px; }
.conf-row-truth   { flex: 1; font-weight: 600; color: #374151; }
.conf-row-predict { flex: 1; color: #374151; }
.conf-row-conf    { width: 52px; text-align: right; color: #9ca3af; font-size: 0.75rem; }

/* ── Code / monospace ── */
code {
    font-family: 'JetBrains Mono', monospace;
    background: #f1f5f9; color: #334155;
    padding: 2px 6px; border-radius: 4px; font-size: 0.82em;
}

/* ── Streamlit overrides ── */
.stButton > button {
    border-radius: 10px; font-weight: 700; font-size: 0.88rem;
    transition: all 0.2s; letter-spacing: 0.01em;
}
[data-testid="stMetric"] { background: #fff; border: 1px solid #e5e7eb; border-radius: 12px; padding: 1rem; }
[data-testid="stMetricValue"] { font-size: 1.8rem !important; font-weight: 800 !important; }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
results_path = Path("data/results/batch_results.json")

with st.sidebar:
    # Logo
    st.markdown("""
    <div class="air-logo">
        <div class="air-logo-icon">🛡</div>
        <div class="air-logo-text">
            <div class="air-logo-name">AIR</div>
            <div class="air-logo-sub">Autonomous Intrusion Responder</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # System status
    st.markdown('<div class="nav-label">SYSTEM STATUS</div>', unsafe_allow_html=True)
    try:
        import httpx
        r = httpx.get("http://127.0.0.1:8000/health", timeout=1.5)
        api_ok = r.status_code == 200
    except Exception:
        api_ok = False

    dot_class = "green" if api_ok else "red"
    status_text = "API Online" if api_ok else "API Offline"
    st.markdown(f'<div style="padding:8px 10px; background:rgba(255,255,255,0.04); border:1px solid #334155; border-radius:8px; font-size:0.8rem; display:flex; align-items:center;"><span class="status-dot {dot_class}"></span><span style="color:#e2e8f0 !important;">{status_text}</span></div>', unsafe_allow_html=True)

    st.markdown('<div class="nav-label" style="margin-top:1.2rem;">NAVIGATION</div>', unsafe_allow_html=True)
    st.page_link("dashboard.py",           label="🏠  Overview")
    st.page_link("pages/1_Live_Analysis.py",        label="⚡  Live Analysis")
    st.page_link("pages/2_Incident_Dashboard.py",   label="📊  Incident Dashboard")
    st.page_link("pages/3_Eval_Results.py",         label="🧪  Eval Results")

    # Pipeline diagram
    st.markdown('<div class="nav-label" style="margin-top:1.2rem;">AGENT PIPELINE</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="pipeline-wrap">
        <div class="p-node">
            <div class="p-node-dot" style="background:#3b82f6;"></div>
            <div class="p-node-text">Triage Agent</div>
        </div>
        <div class="p-connector"></div>
        <div class="p-node">
            <div class="p-node-dot" style="background:#f59e0b;"></div>
            <div class="p-node-text">Policy Router</div>
        </div>
        <div style="display:flex; gap:8px; padding-left:4px; margin:4px 0;">
            <div style="display:flex; flex-direction:column; align-items:center; gap:2px;">
                <div style="width:1px; height:12px; background:#334155;"></div>
                <div class="p-node" style="margin:0; padding:5px 8px;">
                    <div class="p-node-dot" style="background:#10b981;"></div>
                    <div class="p-node-text" style="font-size:0.72rem;">Response Agent</div>
                </div>
            </div>
            <div style="display:flex; flex-direction:column; align-items:center; gap:2px; margin-left:auto;">
                <div style="width:1px; height:12px; background:#334155;"></div>
                <div class="p-node" style="margin:0; padding:5px 8px;">
                    <div class="p-node-dot" style="background:#8b5cf6;"></div>
                    <div class="p-node-text" style="font-size:0.72rem;">Human Review</div>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Dataset stats
    if results_path.exists():
        try:
            d = json.loads(results_path.read_text())
            st.markdown(f"""
            <div style="margin-top:1rem; padding:10px 12px; background:rgba(16,185,129,0.08); border:1px solid rgba(16,185,129,0.2); border-radius:8px;">
                <div style="font-size:0.62rem; font-weight:700; color:#10b981 !important; letter-spacing:0.1em; text-transform:uppercase; margin-bottom:6px;">DATASET LOADED</div>
                <div style="font-size:1.3rem; font-weight:800; color:#f1f5f9 !important;">{d.get('accuracy_pct',0)}%</div>
                <div style="font-size:0.7rem; color:#64748b !important;">Accuracy · {d.get('total',0)} events</div>
            </div>
            """, unsafe_allow_html=True)
        except Exception:
            pass

    st.markdown('<div style="margin-top:auto; padding-top:2rem; font-size:0.65rem; color:#475569 !important;">v1.0.0 · LangGraph + Groq · CICIDS 2017</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# HOME PAGE
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="sec-label" style="margin-top:0;">OVERVIEW</div>', unsafe_allow_html=True)
st.markdown("""
<div class="page-header">
    <h1>Autonomous Intrusion Responder</h1>
    <p>A multi-agent AI security pipeline — analyzes raw network logs, classifies threats, and generates containment playbooks in real time.</p>
</div>
""", unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)
cards = [
    ("⚡", "Live Analysis", "Paste a raw log or pick a CICIDS event. Watch the full agent pipeline execute in real time.", "pages/1_Live_Analysis.py", "green"),
    ("📊", "Incident Dashboard", "Attack distributions, agent routing decisions, severity breakdown, and full incident history.", "pages/2_Incident_Dashboard.py", "blue"),
    ("🧪", "Eval Results", "Accuracy against CICIDS ground truth + 8 behavioral eval cases testing agent judgment.", "pages/3_Eval_Results.py", "amber"),
]
for col, (icon, title, desc, link, accent) in zip([c1, c2, c3], cards):
    with col:
        st.markdown(f"""
        <div class="card card-accent-{accent}" style="height:100%;">
            <div style="font-size:1.5rem; margin-bottom:0.5rem;">{icon}</div>
            <div style="font-size:1rem; font-weight:700; color:#111827; margin-bottom:6px;">{title}</div>
            <div style="font-size:0.82rem; color:#6b7280; line-height:1.5; margin-bottom:0.75rem;">{desc}</div>
        </div>
        """, unsafe_allow_html=True)
        st.page_link(link, label=f"→ Open {title}")

st.markdown('<div class="sec-label">WHY THIS IS AN AGENT, NOT A CLASSIFIER</div>', unsafe_allow_html=True)
st.markdown("""
<div class="card" style="display:grid; grid-template-columns:1fr 1fr; gap:1rem;">
    <div>
        <div style="font-size:0.78rem; font-weight:700; color:#dc2626; text-transform:uppercase; letter-spacing:0.05em; margin-bottom:0.5rem;">❌ A Classifier</div>
        <div style="font-size:0.84rem; color:#6b7280; line-height:1.6;">Takes input → returns a label. One step. Deterministic. No branching logic, no confidence thresholds, no follow-up actions.</div>
    </div>
    <div>
        <div style="font-size:0.78rem; font-weight:700; color:#10b981; text-transform:uppercase; letter-spacing:0.05em; margin-bottom:0.5rem;">✅ This System</div>
        <div style="font-size:0.84rem; color:#374151; line-height:1.6;">Triage Agent classifies → Policy Router <em>decides</em> the next step → Response Agent generates a playbook OR the event is flagged for human review. Different events take different paths.</div>
    </div>
</div>
""", unsafe_allow_html=True)
