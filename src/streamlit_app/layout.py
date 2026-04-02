import streamlit as st
import json
from pathlib import Path

def inject_ui():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

    /* Global Typography & Colors */
    html, body, .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        background-color: #f8fafc;
        color: #0f172a;
    }

    /* Hide Streamlit components */
    #MainMenu, footer, header { visibility: hidden; }
    [data-testid="stSidebarNav"] { display: none !important; }
    .block-container { padding: 3rem 4rem; max-width: 1400px; }

    /* Sidebar Background */
    section[data-testid="stSidebar"] {
        background: #0f172a !important;
        border-right: 1px solid #1e293b;
        min-width: 280px !important;
    }
    
    section[data-testid="stSidebar"] * { color: #94a3b8; }
    
    /* Logo styling */
    .logo-container {
        padding: 1.5rem 0 2rem;
        border-bottom: 1px solid #1e293b;
        margin-bottom: 1.5rem;
    }
    .logo-title {
        font-size: 1.75rem;
        font-weight: 800;
        color: #f8fafc !important;
        letter-spacing: -0.03em;
        line-height: 1.1;
    }
    .logo-subtitle {
        font-size: 0.75rem;
        font-weight: 500;
        color: #64748b !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-top: 0.25rem;
    }

    /* Status dot */
    .status-container {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 0.75rem 1rem;
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid #1e293b;
        border-radius: 6px;
        margin-bottom: 2rem;
    }
    .dot-green {
        width: 10px; height: 10px; border-radius: 50%; background-color: #22c55e;
        box-shadow: 0 0 8px #22c55e;
    }
    .dot-red {
        width: 10px; height: 10px; border-radius: 50%; background-color: #ef4444;
        box-shadow: 0 0 8px #ef4444;
    }
    .status-text {
        font-size: 0.85rem; font-weight: 600; color: #e2e8f0 !important;
    }

    /* Nav section */
    .nav-header {
        font-size: 0.7rem; font-weight: 700; color: #475569 !important;
        text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 0.75rem;
    }

    /* Cards */
    .ui-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);
        margin-bottom: 1.5rem;
    }
    .ui-card-title {
        font-size: 0.85rem; font-weight: 600; color: #64748b;
        text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.75rem;
    }
    .ui-card-value {
        font-size: 2rem; font-weight: 800; color: #0f172a; line-height: 1.2;
    }
    .ui-card-desc {
        font-size: 0.85rem; color: #64748b; margin-top: 0.5rem; line-height: 1.5;
    }
    
    /* Accents */
    .border-left-green { border-left: 4px solid #22c55e; }
    .border-left-red { border-left: 4px solid #ef4444; }
    .border-left-amber { border-left: 4px solid #f59e0b; }
    .border-left-blue { border-left: 4px solid #3b82f6; }
    .border-left-slate { border-left: 4px solid #475569; }

    /* Custom Badge */
    .badge {
        display: inline-flex; align-items: center; justify-content: center;
        padding: 0.35rem 0.85rem; border-radius: 6px;
        font-size: 0.75rem; font-weight: 700; text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .badge-critical { background: #fef2f2; color: #b91c1c; border: 1px solid #fecaca; }
    .badge-high { background: #fff7ed; color: #c2410c; border: 1px solid #fed7aa; }
    .badge-medium { background: #fffbeb; color: #b45309; border: 1px solid #fde68a; }
    .badge-low { background: #f0fdf4; color: #15803d; border: 1px solid #bbf7d0; }
    .badge-info { background: #f8fafc; color: #475569; border: 1px solid #e2e8f0; }

    /* Trace Timeline */
    .trace-item {
        position: relative;
        padding: 0 0 1.5rem 2rem;
        border-left: 2px solid #e2e8f0;
        margin-left: 1rem;
    }
    .trace-item::before {
        content: '';
        position: absolute;
        width: 14px; height: 14px;
        background: #94a3b8;
        border-radius: 50%;
        left: -8px; top: 0;
        border: 2px solid #f8fafc;
    }
    .trace-item.done::before { background: #22c55e; }
    .trace-title { font-weight: 700; font-size: 0.95rem; color: #0f172a; margin-bottom: 0.25rem; }
    .trace-content { font-size: 0.85rem; color: #475569; line-height: 1.5; }
    
    /* Playbook */
    .playbook-step {
        display: flex; gap: 1rem; padding: 1.25rem 0;
        border-bottom: 1px solid #f1f5f9;
    }
    .playbook-step:last-child { border-bottom: none; }
    .playbook-num {
        background: #f1f5f9; color: #3b82f6; width: 28px; height: 28px;
        border-radius: 6px; display: flex; align-items: center; justify-content: center;
        font-size: 0.85rem; font-weight: 700; flex-shrink: 0;
    }
    .playbook-text { font-size: 0.9rem; color: #334155; line-height: 1.6; }

    /* Section Headers */
    .section-header {
        font-size: 1.25rem; font-weight: 700; color: #0f172a;
        margin: 2.5rem 0 1.5rem; padding-bottom: 0.5rem;
        border-bottom: 1px solid #e2e8f0;
    }

    /* Page Titles */
    .page-title {
        font-size: 2.25rem; font-weight: 800; color: #0f172a;
        letter-spacing: -0.03em; margin-bottom: 0.5rem;
    }
    .page-subtitle {
        font-size: 1rem; color: #64748b; margin-bottom: 2rem;
    }
    
    /* Alert Banners */
    .alert {
        padding: 1rem 1.25rem; border-radius: 8px; font-size: 0.9rem; font-weight: 500;
        margin-bottom: 1.5rem;
    }
    .alert-info { background: #eff6ff; color: #1e3a8a; border: 1px solid #bfdbfe; }
    .alert-amber { background: #fffbeb; color: #92400e; border: 1px solid #fde68a; }
    .alert-red { background: #fef2f2; color: #991b1b; border: 1px solid #fecaca; }
    
    /* Monospace Text */
    .mono { font-family: 'JetBrains Mono', monospace; font-size: 0.85em; }

    /* Streamlit overrides */
    [data-testid="stMetricValue"] { font-size: 2rem !important; font-weight: 800 !important; }
    .stButton > button { font-weight: 600; border-radius: 8px; }
    </style>
    """, unsafe_allow_html=True)

    with st.sidebar:
        st.markdown('''
            <div class="logo-container">
                <div class="logo-title">AIR</div>
                <div class="logo-subtitle">Autonomous Intrusion Responder</div>
            </div>
        ''', unsafe_allow_html=True)

        try:
            import httpx
            import os
            api_base = os.getenv("API_BASE", "http://127.0.0.1:8000")
            r = httpx.get(f"{api_base}/health", timeout=1.0)
            api_ok = (r.status_code == 200)
        except Exception:
            api_ok = False
        
        dot_cls = "dot-green" if api_ok else "dot-red"
        status_text = "API Online" if api_ok else "API Offline"

        st.markdown(f'''
            <div class="status-container">
                <div class="{dot_cls}"></div>
                <div class="status-text">{status_text}</div>
            </div>
        ''', unsafe_allow_html=True)

        st.markdown('<div class="nav-header">Navigation</div>', unsafe_allow_html=True)
        st.page_link("src/streamlit_app/dashboard.py", label="Overview")
        st.page_link("src/streamlit_app/pages/1_Live_Analysis.py", label="Live Analysis")
        st.page_link("src/streamlit_app/pages/2_Incident_Dashboard.py", label="Incident Dashboard")
        st.page_link("src/streamlit_app/pages/3_Eval_Results.py", label="Eval Results")

        st.markdown('<div class="nav-header" style="margin-top: 3rem;">System Info</div>', unsafe_allow_html=True)
        st.markdown('<div style="font-size: 0.75rem; color: #64748b; line-height: 1.6;">Version: v1.1.0<br>Model: Groq LLaMA 3.3<br>Orchestrator: LangGraph</div>', unsafe_allow_html=True)

def get_severity_badge(sev):
    mapping = {
        "critical": "badge-critical",
        "high": "badge-high",
        "medium": "badge-medium",
        "low": "badge-low",
        "info": "badge-info"
    }
    cls = mapping.get(sev.lower(), "badge-info")
    return f'<span class="badge {cls}">{sev.upper()}</span>'

def get_severity_accent(sev):
    mapping = {
        "critical": "border-left-red",
        "high": "border-left-red",
        "medium": "border-left-amber",
        "low": "border-left-green",
        "info": "border-left-blue"
    }
    return mapping.get(sev.lower(), "border-left-slate")
