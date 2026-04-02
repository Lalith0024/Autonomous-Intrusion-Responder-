"""Dashboard entry point — sets page config and shared sidebar for all pages."""

import json
from pathlib import Path

import streamlit as st

st.set_page_config(
    page_title="AIR — Autonomous Intrusion Responder",
    page_icon="🛡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Global CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
* { box-sizing: border-box; }

body, .stApp {
    background-color: #f8f9fa;
    font-family: Arial, -apple-system, BlinkMacSystemFont, sans-serif;
    color: #1a1a1a;
}

section[data-testid="stSidebar"] {
    background-color: #ffffff !important;
    border-right: 1px solid #e5e7eb;
}

/* Remove default Streamlit padding */
.block-container { padding-top: 2rem; padding-bottom: 2rem; }

/* Typography */
h1 { font-size: 1.75rem; font-weight: 700; color: #1a1a1a; letter-spacing: -0.02em; margin-bottom: 0.25rem; }
h2 { font-size: 1.25rem; font-weight: 600; color: #1a1a1a; letter-spacing: -0.01em; }
h3 { font-size: 1rem; font-weight: 600; color: #1a1a1a; }
p  { color: #4a4a4a; font-size: 0.95rem; line-height: 1.6; }

/* Severity pills — reusable everywhere */
.sev-critical { display:inline-block; padding:2px 10px; border-radius:9999px; font-size:0.72rem; font-weight:600; background:#fef2f2; color:#dc2626; border:1px solid #fecaca; }
.sev-high     { display:inline-block; padding:2px 10px; border-radius:9999px; font-size:0.72rem; font-weight:600; background:#fff7ed; color:#dc2626; border:1px solid #fed7aa; }
.sev-medium   { display:inline-block; padding:2px 10px; border-radius:9999px; font-size:0.72rem; font-weight:600; background:#fffbeb; color:#d97706; border:1px solid #fde68a; }
.sev-low      { display:inline-block; padding:2px 10px; border-radius:9999px; font-size:0.72rem; font-weight:600; background:#f0fdf4; color:#16a34a; border:1px solid #bbf7d0; }
.sev-info     { display:inline-block; padding:2px 10px; border-radius:9999px; font-size:0.72rem; font-weight:600; background:#eff6ff; color:#2563eb; border:1px solid #bfdbfe; }

/* Section label */
.section-label {
    font-size: 0.7rem;
    font-weight: 600;
    color: #6b7280;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 0.5rem;
    margin-top: 1.5rem;
}

/* Trace step */
.trace-step {
    display: flex;
    align-items: flex-start;
    gap: 12px;
    padding: 10px 14px;
    background: #f8f9fa;
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    margin-bottom: 8px;
}
.trace-check { color: #16a34a; font-weight: 700; font-size: 1rem; flex-shrink: 0; margin-top: 1px; }
.trace-node  { font-weight: 600; color: #1a1a1a; font-size: 0.85rem; }
.trace-desc  { color: #6b7280; font-size: 0.8rem; margin-top: 2px; }

/* IoC tag */
.ioc-tag {
    display: inline-block;
    padding: 2px 8px;
    background: #f1f5f9;
    color: #475569;
    border-radius: 5px;
    font-size: 0.78rem;
    font-family: monospace;
    margin: 2px 3px 2px 0;
    border: 1px solid #e2e8f0;
}

/* Playbook step */
.step-row {
    display: flex;
    align-items: flex-start;
    gap: 12px;
    padding: 10px 0;
    border-bottom: 1px solid #f1f5f9;
}
.step-num {
    flex-shrink: 0;
    width: 26px;
    height: 26px;
    border-radius: 6px;
    background: #eff6ff;
    color: #2563eb;
    font-size: 0.78rem;
    font-weight: 700;
    display: flex;
    align-items: center;
    justify-content: center;
    border: 1px solid #dbeafe;
}
.step-text { color: #374151; font-size: 0.88rem; line-height: 1.5; }

/* Stat card */
.stat-card {
    background: #ffffff;
    border: 1px solid #e5e7eb;
    border-radius: 10px;
    padding: 1rem 1.25rem;
}
.stat-val  { font-size: 1.6rem; font-weight: 700; color: #1a1a1a; letter-spacing: -0.02em; }
.stat-lbl  { font-size: 0.75rem; color: #6b7280; margin-top: 2px; font-weight: 500; }

/* Human review banner */
.review-banner {
    background: #faf5ff;
    border: 1px solid #e9d5ff;
    border-radius: 8px;
    padding: 12px 16px;
    color: #7c3aed;
    font-size: 0.88rem;
}

/* Escalate banner */
.escalate-banner {
    background: #fef2f2;
    border: 1px solid #fecaca;
    border-radius: 8px;
    padding: 12px 16px;
    color: #dc2626;
    font-size: 0.88rem;
    font-weight: 600;
}

/* Impact card */
.impact-card {
    background: #f8f9fa;
    border-left: 3px solid #2563eb;
    border-radius: 0 8px 8px 0;
    padding: 10px 14px;
    color: #374151;
    font-size: 0.88rem;
}

/* Reasoning */
.reasoning-block {
    background: #f8f9fa;
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    padding: 12px 16px;
    color: #4a4a4a;
    font-size: 0.88rem;
    font-style: italic;
    line-height: 1.6;
}

/* Empty state */
.empty-state {
    text-align: center;
    padding: 3rem 2rem;
    color: #9ca3af;
}
.empty-state-title { font-size: 1rem; font-weight: 600; color: #6b7280; margin-bottom: 0.5rem; }
.empty-state-sub   { font-size: 0.85rem; }

/* Sidebar pipeline text */
.pipeline-mono {
    font-family: monospace;
    font-size: 0.78rem;
    color: #6b7280;
    line-height: 1.8;
    background: #f8f9fa;
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    padding: 10px 12px;
    margin-top: 0.5rem;
}

/* Table styling */
.eval-row-pass { background: #f0fdf4; }
.eval-row-fail { background: #fef2f2; }
</style>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="margin-bottom:1rem;">
        <div style="font-size:1.3rem; font-weight:700; color:#1a1a1a;">🛡 AIR</div>
        <div style="font-size:0.78rem; color:#6b7280; margin-top:2px;">Autonomous Intrusion Responder</div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    st.markdown('<div style="font-size:0.7rem; font-weight:600; color:#6b7280; text-transform:uppercase; letter-spacing:0.08em; margin-bottom:0.5rem;">PIPELINE</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="pipeline-mono">
    Triage Agent<br>
    &nbsp;&nbsp;&nbsp;&nbsp;↓<br>
    Policy Router<br>
    &nbsp;&nbsp;↙&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;↘<br>
    Response&nbsp;&nbsp;Human<br>
    Agent&nbsp;&nbsp;&nbsp;&nbsp;Review
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # Show analyzed event count if results exist
    results_path = Path("data/results/batch_results.json")
    if results_path.exists():
        try:
            data = json.loads(results_path.read_text())
            n = data.get("total", 0)
            acc = data.get("accuracy_pct", 0)
            st.markdown(f'<div style="font-size:0.75rem; color:#6b7280;">CICIDS 2017 · <b>{n}</b> events analyzed<br>Accuracy: <b>{acc}%</b></div>', unsafe_allow_html=True)
        except Exception:
            pass
    else:
        st.markdown('<div style="font-size:0.75rem; color:#9ca3af;">No batch data yet</div>', unsafe_allow_html=True)

    st.markdown('<div style="font-size:0.72rem; color:#9ca3af; margin-top:1rem;">v1.0.0 · LangGraph + Groq</div>', unsafe_allow_html=True)

# ── Home Page Content ─────────────────────────────────────────────────────────
st.markdown('<div class="section-label" style="margin-top:0;">OVERVIEW</div>', unsafe_allow_html=True)
st.markdown("# Autonomous Intrusion Responder")
st.markdown('<p style="color:#6b7280; margin-bottom:2rem;">A multi-agent AI pipeline for real-time network threat analysis and containment. Use the navigation on the left to get started.</p>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)
with col1:
    with st.container(border=True):
        st.markdown("**Live Analysis**")
        st.markdown('<p style="font-size:0.85rem; color:#6b7280;">Paste a raw log or select a CICIDS event and run the full agent pipeline in real time.</p>', unsafe_allow_html=True)
        st.page_link("pages/1_Live_Analysis.py", label="→ Go to Live Analysis")

with col2:
    with st.container(border=True):
        st.markdown("**Incident Dashboard**")
        st.markdown('<p style="font-size:0.85rem; color:#6b7280;">View attack distributions, agent routing decisions, and full incident history from batch analysis.</p>', unsafe_allow_html=True)
        st.page_link("pages/2_Incident_Dashboard.py", label="→ Go to Dashboard")

with col3:
    with st.container(border=True):
        st.markdown("**Eval Results**")
        st.markdown('<p style="font-size:0.85rem; color:#6b7280;">Behavioral evals across 8 attack scenarios + CICIDS accuracy against ground truth labels.</p>', unsafe_allow_html=True)
        st.page_link("pages/3_Eval_Results.py", label="→ Go to Evals")
