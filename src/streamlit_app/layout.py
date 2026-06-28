"""Global Design System — Premium Light SOC Dashboard.

This module controls the visual identity of the Streamlit application.
The design has been adjusted to a professional light theme driven by config.toml,
with custom CSS limited to specific UI components (cards, badges, timelines).

Design Language:
    - Main Content & Sidebar: Native Light Theme (handled via config.toml)
    - Cards: Clean white surfaces with subtle borders and shadows.
    - Typography: Inter for UI, JetBrains Mono for logs.
    - Muted, professional accent colors.
"""

import streamlit as st


def inject_ui():
    """Inject the global design system into the Streamlit page."""
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600&display=swap');

    /* ── Global Tweaks ────────────────────────────────────── */
    html, body, .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    #MainMenu, footer { visibility: hidden; }
    header { background: transparent !important; }
    [data-testid="stSidebarNav"] { display: none !important; }
    
    /* ── Dark Sidebar ── */
    [data-testid="stSidebar"] {
        background-color: #0f172a !important;
        border-right: 1px solid #1e293b;
    }
    .block-container { padding: 3rem 5rem; max-width: 1450px; }

    /* ── Logo (Simplified) ────────────────────────────────── */
    .logo-container {
        padding: 1.5rem 0 2.5rem;
        border-bottom: 1px solid #1e293b;
        margin-bottom: 2rem;
    }
    .logo-title {
        font-size: 2.25rem;
        font-weight: 900;
        color: #f8fafc;
        letter-spacing: -0.04em;
        line-height: 1;
    }
    .logo-subtitle {
        font-size: 0.65rem;
        font-weight: 700;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin-top: 0.6rem;
    }
    .logo-version {
        font-size: 0.6rem;
        color: #475569;
        font-family: 'JetBrains Mono', monospace;
        margin-top: 0.5rem;
    }

    /* ── Status Indicator (Clean Dark) ────────────────────── */
    .status-container {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 1rem;
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 12px;
        margin-bottom: 2.5rem;
    }
    .dot-green {
        width: 8px; height: 8px; border-radius: 50%; background: #22c55e;
        box-shadow: 0 0 12px rgba(34, 197, 94, 0.5);
    }
    .dot-red {
        width: 8px; height: 8px; border-radius: 50%; background: #ef4444;
        box-shadow: 0 0 8px rgba(239, 68, 68, 0.4);
    }
    .status-text {
        font-size: 0.75rem; font-weight: 700; color: #f8fafc;
    }
    @keyframes pulse-dot {
        0%, 100% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.6; transform: scale(0.9); }
    }

    /* ── Nav Section ──────────────────────────────────────── */
    .nav-header {
        font-size: 0.65rem; font-weight: 800; color: #475569;
        text-transform: uppercase; letter-spacing: 0.15em; margin-bottom: 1rem;
        padding-left: 0.5rem;
    }
    
    section[data-testid="stSidebar"] .stPageLink {
        padding: 0.6rem 0.85rem;
        border-radius: 10px;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
        margin-bottom: 4px;
    }
    section[data-testid="stSidebar"] .stPageLink:hover {
        background-color: #1e293b;
        transform: translateX(4px);
    }
    section[data-testid="stSidebar"] .stPageLink span {
        font-weight: 600 !important;
        color: #cbd5e1 !important;
        font-size: 0.85rem !important;
    }

    /* ── Premium Light Cards ─────────────────────────────── */
    .ui-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05), 0 10px 15px -5px rgba(0, 0, 0, 0.05);
        margin-bottom: 1.25rem;
        transition: all 0.3s ease;
    }
    .ui-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 20px 25px -5px rgba(0, 0, 0, 0.04);
        border-color: #cbd5e1;
    }
    .ui-card-title {
        font-size: 0.85rem; font-weight: 700; color: #64748b;
        text-transform: uppercase; letter-spacing: 0.04em; margin-bottom: 0.75rem;
    }
    .ui-card-value {
        font-size: 2.25rem; font-weight: 800; color: #0f172a; line-height: 1;
    }
    .ui-card-desc {
        font-size: 0.9rem; color: #64748b; margin-top: 0.75rem; line-height: 1.6;
    }

    /* ── Accent Borders ──────────────────────────────────── */
    .border-left-green  { border-left: 4px solid #10b981; }
    .border-left-red    { border-left: 4px solid #ef4444; }
    .border-left-amber  { border-left: 4px solid #f59e0b; }
    .border-left-blue   { border-left: 4px solid #3b82f6; }
    .border-left-indigo { border-left: 4px solid #6366f1; }
    .border-left-slate  { border-left: 4px solid #64748b; }

    /* ── Professional Badges ────────────────────────────── */
    .badge {
        display: inline-flex; align-items: center; justify-content: center;
        padding: 0.4rem 0.8rem; border-radius: 9999px;
        font-size: 0.7rem; font-weight: 800; text-transform: uppercase;
        letter-spacing: 0.075em;
    }
    .badge-critical { background: #fee2e2; color: #991b1b; }
    .badge-high     { background: #ffedd5; color: #9a3412; }
    .badge-medium   { background: #fef3c7; color: #92400e; }
    .badge-low      { background: #dcfce7; color: #166534; }
    .badge-info     { background: #e0e7ff; color: #3730a3; }
    .badge-tool     { background: #ecfeff; color: #155e75; border: 1px solid #cffafe; }
    .badge-blocked  { background: #fef2f2; color: #b91c1c; border: 1px solid #fecaca; }
    .badge-match    { background: #dcfce7; color: #166534; border: 1px solid #bbf7d0; }
    .badge-nomatch  { background: #fef2f2; color: #991b1b; border: 1px solid #fecaca; }

    /* ── Trace Timeline (Light) ──────────────────────────── */
    .trace-item {
        position: relative; padding: 0 0 1.75rem 2.5rem;
        border-left: 2px solid #e2e8f0;
        margin-left: 1rem;
    }
    .trace-item::before {
        content: ''; position: absolute;
        width: 14px; height: 14px;
        background: #cbd5e1; border-radius: 50%;
        left: -8px; top: 2px;
        border: 3px solid #f8fafc;
        transition: all 0.3s ease;
    }
    .trace-item.done::before { background: #10b981; }
    .trace-item.active::before { background: #f59e0b; animation: pulse-dot 2s ease-in-out infinite; }
    .trace-title { font-weight: 700; font-size: 0.95rem; color: #1e293b; margin-bottom: 0.35rem; }
    .trace-content { font-size: 0.85rem; color: #64748b; line-height: 1.6; }
    .trace-time { font-size: 0.75rem; color: #94a3b8; font-family: 'JetBrains Mono', monospace; margin-top: 0.4rem; }

    /* ── Tool Call Display ────────────────────────────────── */
    .tool-call {
        background: #f1f5f9;
        border: 1px solid #e2e8f0;
        border-radius: 8px; padding: 1rem;
        margin: 0.75rem 0; font-family: 'JetBrains Mono', monospace; font-size: 0.8rem;
    }
    .tool-name { color: #0f172a; font-weight: 700; }
    .tool-result { color: #475569; margin-top: 0.4rem; }

    /* ── Playbook Steps ──────────────────────────────────── */
    .playbook-step {
        display: flex; gap: 1.25rem; padding: 1.25rem 0;
        border-bottom: 1px solid #f1f5f9;
    }
    .playbook-step:last-child { border-bottom: none; }
    .playbook-num {
        background: #4f46e5; color: #ffffff;
        width: 32px; height: 32px; border-radius: 10px;
        display: flex; align-items: center; justify-content: center;
        font-size: 0.9rem; font-weight: 800; flex-shrink: 0;
    }
    .playbook-text { font-size: 0.95rem; color: #334155; line-height: 1.7; font-weight: 500; }

    /* ── Section Headers ─────────────────────────────────── */
    .section-header {
        font-size: 1.25rem; font-weight: 800; color: #0f172a;
        margin: 2.5rem 0 1.25rem; padding-bottom: 0.75rem;
        border-bottom: 2px solid #f1f5f9;
        letter-spacing: -0.02em;
    }

    /* ── Page Titles ──────────────────────────────────────── */
    .page-title {
        font-size: 2.5rem; font-weight: 900; color: #0f172a;
        letter-spacing: -0.05em; margin-bottom: 0.5rem;
        line-height: 1;
    }
    .page-subtitle {
        font-size: 1rem; color: #64748b; margin-bottom: 3rem; line-height: 1.7;
        font-weight: 500; max-width: 800px;
    }

    /* ── Professional Alerts ─────────────────────────────── */
    .alert {
        padding: 1rem 1.25rem; border-radius: 12px; font-size: 0.95rem; font-weight: 600;
        margin-bottom: 1.5rem;
        display: flex; align-items: center; gap: 12px;
    }
    .alert-info  { background: #eff6ff; color: #1e40af; border: 1px solid #dbeafe; }
    .alert-amber { background: #fffbeb; color: #92400e; border: 1px solid #fef3c7; }
    .alert-red   { background: #fef2f2; color: #991b1b; border: 1px solid #fee2e2; }
    .alert-green { background: #f0fdf4; color: #166534; border: 1px solid #dcfce7; }

    /* ── Terminal Style (Muted) ──────────────────────────── */
    .terminal-header {
        background: #1e293b; border: 1px solid #334155;
        border-bottom: none; border-radius: 12px 12px 0 0;
        padding: 0.75rem 1.25rem; display: flex; align-items: center; gap: 8px;
    }
    .terminal-dot { width: 12px; height: 12px; border-radius: 50%; }
    .terminal-dot.red { background: #ef4444; }
    .terminal-dot.yellow { background: #f59e0b; }
    .terminal-dot.green { background: #10b981; }

    /* ── Monospace ─────────────────────────────────────────── */
    .mono { font-family: 'JetBrains Mono', monospace; font-size: 0.85em; font-weight: 500; }

    /* ── Custom UI Element Overrides ─────────────────────── */
    [data-testid="stMetricLabel"] { font-weight: 700 !important; text-transform: uppercase; letter-spacing: 0.05em; color: #64748b !important; }
    [data-testid="stMetricValue"] { font-size: 2rem !important; font-weight: 900 !important; color: #0f172a !important; }
    
    .stButton > button {
        background: #0f172a !important;
        color: #ffffff !important; border: none !important;
        border-radius: 10px !important; font-weight: 700 !important;
        padding: 0.75rem 2rem !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1) !important;
    }
    .stButton > button:hover {
        background: #1e293b !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1) !important;
    }
    
    div[data-testid="stExpander"] {
        background: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 12px !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05) !important;
    }
    
    [data-testid="stDataFrame"] {
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        overflow: hidden;
    }
    </style>
    """, unsafe_allow_html=True)

    # ── Sidebar ──
    with st.sidebar:
        st.markdown('''
            <div class="logo-container">
                <div class="logo-title">AIR</div>
                <div class="logo-subtitle">Security Analysis Agent</div>
                <div class="logo-version">v2.1.0 — STABLE</div>
            </div>
        ''', unsafe_allow_html=True)

        # API Status
        try:
            import httpx
            import os
            api_base = os.getenv("API_BASE", "http://127.0.0.1:8000")
            r = httpx.get(f"{api_base}/health", timeout=1.0)
            health = r.json() if (r.status_code == 200) else {}
            api_ok = (r.status_code == 200)
        except Exception:
            api_ok = False
            health = {}

        dot_cls = "dot-green" if api_ok else "dot-red"
        status_text = "Analysis Engine Online" if api_ok else "Engine Starting..."

        st.markdown(f'''
            <div class="status-container">
                <div class="{dot_cls}"></div>
                <div class="status-text">{status_text}</div>
            </div>
        ''', unsafe_allow_html=True)

        # Component Status
        if api_ok and health.get("components"):
            components = health["components"]
            comp_html = '<div style="margin-bottom: 3rem; padding: 0 0.5rem;">'
            for comp, status in components.items():
                is_ok = status in ("healthy", "connected", "enabled", "true")
                color = "#22c55e" if is_ok else "#475569"
                comp_html += f'''
                <div style="display:flex; justify-content:space-between; padding:0.5rem 0; border-bottom:1px solid #1e293b;">
                    <span style="color:#64748b; font-size:0.6rem; font-weight:700; text-transform:uppercase;">{comp}</span>
                    <span style="color:{color}; font-size:0.6rem; font-weight:800;">{str(status).upper()}</span>
                </div>'''
            comp_html += '</div>'
            st.markdown(comp_html, unsafe_allow_html=True)

        st.markdown('<div class="nav-header">Navigation</div>', unsafe_allow_html=True)
        # Robust navigation paths relative to src/streamlit_app
        st.page_link("dashboard.py", label="Overview")
        st.page_link("pages/0_About.py", label="About AIR")
        st.page_link("pages/1_Live_Analysis.py", label="Live Analysis")
        st.page_link("pages/2_Incident_Dashboard.py", label="Incident History")
        st.page_link("pages/3_Eval_Results.py", label="Performance")

        st.markdown('<div class="nav-header" style="margin-top: 4rem;">System Data</div>', unsafe_allow_html=True)
        st.markdown('''
            <div style="font-size: 0.6rem; color: #475569; line-height: 2.2; font-family: 'JetBrains Mono', monospace; padding-left: 0.5rem;">
                ENV: PRODUCTION<br>
                CORE: LLAMA-3.3-70B<br>
                STORAGE: LOCAL FAISS<br>
                SERVICE: ANALYTICS ID-24
            </div>
        ''', unsafe_allow_html=True)


def get_severity_badge(sev: str) -> str:
    """Return an HTML badge for a severity level."""
    mapping = {
        "critical": "badge-critical",
        "high": "badge-high",
        "medium": "badge-medium",
        "low": "badge-low",
        "info": "badge-info",
    }
    cls = mapping.get(sev.lower(), "badge-info")
    return f'<span class="badge {cls}">{sev.upper()}</span>'


def get_severity_accent(sev: str) -> str:
    """Return a CSS class for the severity accent border."""
    mapping = {
        "critical": "border-left-red",
        "high": "border-left-red",
        "medium": "border-left-amber",
        "low": "border-left-green",
        "info": "border-left-blue",
    }
    return mapping.get(sev.lower(), "border-left-slate")
