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
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800;900&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

    /* ── Global Tweaks ────────────────────────────────────── */
    html, body, .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        background: linear-gradient(135deg, #fdfbfb 0%, #ebedee 100%);
        color: #1e293b;
    }

    #MainMenu, footer { visibility: hidden; }
    header { background: transparent !important; }
    [data-testid="stSidebarNav"] { display: none !important; }
    
    /* ── Dark Premium Sidebar ── */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.05);
        box-shadow: 4px 0 15px rgba(0,0,0,0.1);
    }
    .block-container { padding: 4rem 6rem; max-width: 1600px; }

    /* ── Logo ────────────────────────────────── */
    .logo-container {
        padding: 2rem 0 3rem;
        border-bottom: 1px solid rgba(255, 255, 255, 0.08);
        margin-bottom: 2rem;
        text-align: center;
    }
    .logo-title {
        font-family: 'Outfit', sans-serif;
        font-size: 3rem;
        font-weight: 900;
        background: linear-gradient(to right, #38bdf8, #818cf8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: -0.05em;
        line-height: 1.1;
    }
    .logo-subtitle {
        font-family: 'Inter', sans-serif;
        font-size: 0.75rem;
        font-weight: 700;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.15em;
        margin-top: 0.8rem;
    }
    .logo-version {
        font-size: 0.65rem;
        color: #64748b;
        font-family: 'JetBrains Mono', monospace;
        margin-top: 0.75rem;
        background: rgba(255,255,255,0.05);
        display: inline-block;
        padding: 0.2rem 0.6rem;
        border-radius: 9999px;
    }

    /* ── Status Indicator (Glassmorphism Dark) ────────────────────── */
    .status-container {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 1rem 1.5rem;
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        margin-bottom: 2.5rem;
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
    }
    .dot-green {
        width: 10px; height: 10px; border-radius: 50%; background: #22c55e;
        box-shadow: 0 0 12px rgba(34, 197, 94, 0.8);
    }
    .dot-red {
        width: 10px; height: 10px; border-radius: 50%; background: #ef4444;
        box-shadow: 0 0 12px rgba(239, 68, 68, 0.8);
    }
    .status-text {
        font-family: 'Outfit', sans-serif;
        font-size: 0.85rem; font-weight: 700; color: #f8fafc;
        letter-spacing: 0.02em;
    }
    @keyframes pulse-dot {
        0%, 100% { opacity: 1; transform: scale(1); box-shadow: 0 0 12px rgba(34, 197, 94, 0.8); }
        50% { opacity: 0.5; transform: scale(0.9); box-shadow: 0 0 4px rgba(34, 197, 94, 0.3); }
    }

    /* ── Nav Section ──────────────────────────────────────── */
    .nav-header {
        font-family: 'Inter', sans-serif;
        font-size: 0.7rem; font-weight: 800; color: #64748b;
        text-transform: uppercase; letter-spacing: 0.2em; margin-bottom: 1.5rem;
        padding-left: 0.75rem;
    }
    
    section[data-testid="stSidebar"] .stPageLink {
        padding: 0.8rem 1rem;
        border-radius: 12px;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        margin-bottom: 8px;
        border: 1px solid transparent;
    }
    section[data-testid="stSidebar"] .stPageLink:hover {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.08);
        transform: translateX(6px);
    }
    section[data-testid="stSidebar"] .stPageLink span {
        font-family: 'Outfit', sans-serif !important;
        font-weight: 600 !important;
        color: #e2e8f0 !important;
        font-size: 0.95rem !important;
        letter-spacing: 0.01em;
    }

    /* ── Premium Light Cards (Glassmorphism) ─────────────────────────────── */
    .ui-card {
        background: rgba(255, 255, 255, 0.7);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.8);
        border-radius: 20px;
        padding: 2rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 10px 15px -3px rgba(0, 0, 0, 0.02);
        margin-bottom: 1.5rem;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    }
    .ui-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.08), 0 25px 30px -5px rgba(0, 0, 0, 0.04);
        background: rgba(255, 255, 255, 0.9);
        border-color: #e2e8f0;
    }
    .ui-card-title {
        font-family: 'Outfit', sans-serif;
        font-size: 0.95rem; font-weight: 700; color: #475569;
        text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 1rem;
    }
    .ui-card-value {
        font-family: 'Outfit', sans-serif;
        font-size: 3rem; font-weight: 900; color: #0f172a; line-height: 1;
        letter-spacing: -0.03em;
    }
    .ui-card-desc {
        font-size: 0.95rem; color: #64748b; margin-top: 1rem; line-height: 1.6;
    }

    /* ── Accent Borders (Gradients) ──────────────────────────────────── */
    .border-left-green  { position: relative; overflow: hidden; }
    .border-left-green::before  { content: ''; position: absolute; left: 0; top: 0; bottom: 0; width: 6px; background: linear-gradient(to bottom, #10b981, #34d399); }
    .border-left-red    { position: relative; overflow: hidden; }
    .border-left-red::before    { content: ''; position: absolute; left: 0; top: 0; bottom: 0; width: 6px; background: linear-gradient(to bottom, #ef4444, #f87171); }
    .border-left-amber  { position: relative; overflow: hidden; }
    .border-left-amber::before  { content: ''; position: absolute; left: 0; top: 0; bottom: 0; width: 6px; background: linear-gradient(to bottom, #f59e0b, #fbbf24); }
    .border-left-blue   { position: relative; overflow: hidden; }
    .border-left-blue::before   { content: ''; position: absolute; left: 0; top: 0; bottom: 0; width: 6px; background: linear-gradient(to bottom, #3b82f6, #60a5fa); }
    .border-left-indigo { position: relative; overflow: hidden; }
    .border-left-indigo::before { content: ''; position: absolute; left: 0; top: 0; bottom: 0; width: 6px; background: linear-gradient(to bottom, #6366f1, #818cf8); }
    .border-left-slate  { position: relative; overflow: hidden; }
    .border-left-slate::before  { content: ''; position: absolute; left: 0; top: 0; bottom: 0; width: 6px; background: linear-gradient(to bottom, #64748b, #94a3b8); }

    /* ── Professional Badges ────────────────────────────── */
    .badge {
        display: inline-flex; align-items: center; justify-content: center;
        padding: 0.5rem 1rem; border-radius: 9999px;
        font-family: 'Outfit', sans-serif;
        font-size: 0.75rem; font-weight: 800; text-transform: uppercase;
        letter-spacing: 0.1em;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .badge-critical { background: linear-gradient(135deg, #fef2f2, #fee2e2); color: #991b1b; border: 1px solid #fecaca; }
    .badge-high     { background: linear-gradient(135deg, #fff7ed, #ffedd5); color: #9a3412; border: 1px solid #fed7aa; }
    .badge-medium   { background: linear-gradient(135deg, #fffbeb, #fef3c7); color: #92400e; border: 1px solid #fde68a; }
    .badge-low      { background: linear-gradient(135deg, #f0fdf4, #dcfce7); color: #166534; border: 1px solid #bbf7d0; }
    .badge-info     { background: linear-gradient(135deg, #eef2ff, #e0e7ff); color: #3730a3; border: 1px solid #c7d2fe; }
    .badge-tool     { background: linear-gradient(135deg, #f8fafc, #f1f5f9); color: #475569; border: 1px solid #e2e8f0; }
    .badge-blocked  { background: linear-gradient(135deg, #fef2f2, #fee2e2); color: #b91c1c; border: 1px solid #fecaca; }
    .badge-match    { background: linear-gradient(135deg, #f0fdf4, #dcfce7); color: #166534; border: 1px solid #bbf7d0; }
    .badge-nomatch  { background: linear-gradient(135deg, #fef2f2, #fee2e2); color: #991b1b; border: 1px solid #fecaca; }

    /* ── Trace Timeline ──────────────────────────── */
    .trace-item {
        position: relative; padding: 0 0 2rem 3rem;
        border-left: 2px solid #cbd5e1;
        margin-left: 1.5rem;
    }
    .trace-item::before {
        content: ''; position: absolute;
        width: 16px; height: 16px;
        background: #e2e8f0; border-radius: 50%;
        left: -9px; top: 4px;
        border: 3px solid #ffffff;
        box-shadow: 0 0 0 2px #cbd5e1;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    }
    .trace-item.done::before { background: #3b82f6; box-shadow: 0 0 0 2px #93c5fd; }
    .trace-item.active::before { background: #f59e0b; box-shadow: 0 0 0 2px #fcd34d; animation: pulse-dot 2s ease-in-out infinite; }
    .trace-title { font-family: 'Outfit', sans-serif; font-weight: 800; font-size: 1.1rem; color: #0f172a; margin-bottom: 0.5rem; letter-spacing: -0.01em; }
    .trace-content { font-size: 0.95rem; color: #475569; line-height: 1.7; }
    .trace-time { font-size: 0.8rem; color: #94a3b8; font-family: 'JetBrains Mono', monospace; margin-top: 0.75rem; font-weight: 600; }

    /* ── Tool Call Display ────────────────────────────────── */
    .tool-call {
        background: rgba(255,255,255,0.8);
        border: 1px solid #e2e8f0;
        border-radius: 12px; padding: 1.25rem;
        margin: 1rem 0; font-family: 'JetBrains Mono', monospace; font-size: 0.85rem;
        box-shadow: inset 0 2px 4px rgba(0,0,0,0.02);
    }
    .tool-name { color: #2563eb; font-weight: 700; margin-bottom: 0.4rem; }
    .tool-result { color: #475569; line-height: 1.5; }

    /* ── Playbook Steps ──────────────────────────────────── */
    .playbook-step {
        display: flex; gap: 1.5rem; padding: 1.5rem 0;
        border-bottom: 1px dashed #cbd5e1;
        align-items: flex-start;
    }
    .playbook-step:last-child { border-bottom: none; }
    .playbook-num {
        background: linear-gradient(135deg, #4f46e5, #6366f1); color: #ffffff;
        width: 36px; height: 36px; border-radius: 12px;
        display: flex; align-items: center; justify-content: center;
        font-family: 'Outfit', sans-serif; font-size: 1.1rem; font-weight: 900; flex-shrink: 0;
        box-shadow: 0 4px 6px rgba(79, 70, 229, 0.3);
    }
    .playbook-text { font-size: 1.05rem; color: #1e293b; line-height: 1.6; font-weight: 500; margin-top: 0.2rem; }

    /* ── Section Headers ─────────────────────────────────── */
    .section-header {
        font-family: 'Outfit', sans-serif;
        font-size: 1.75rem; font-weight: 900; color: #0f172a;
        margin: 3.5rem 0 1.5rem; padding-bottom: 1rem;
        border-bottom: 2px solid rgba(0,0,0,0.05);
        letter-spacing: -0.03em;
    }

    /* ── Page Titles ──────────────────────────────────────── */
    .page-title {
        font-family: 'Outfit', sans-serif;
        font-size: 3.5rem; font-weight: 900; color: #0f172a;
        letter-spacing: -0.06em; margin-bottom: 1rem;
        line-height: 1.1;
        background: linear-gradient(to right, #0f172a, #334155);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .page-subtitle {
        font-size: 1.15rem; color: #64748b; margin-bottom: 4rem; line-height: 1.7;
        font-weight: 500; max-width: 900px;
    }

    /* ── Professional Alerts ─────────────────────────────── */
    .alert {
        padding: 1.25rem 1.5rem; border-radius: 16px; font-size: 1rem; font-weight: 600;
        margin-bottom: 2rem;
        display: flex; align-items: center; gap: 16px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.02);
    }
    .alert-info  { background: linear-gradient(to right, #eff6ff, #ffffff); color: #1e40af; border: 1px solid #bfdbfe; border-left: 4px solid #3b82f6; }
    .alert-amber { background: linear-gradient(to right, #fffbeb, #ffffff); color: #92400e; border: 1px solid #fde68a; border-left: 4px solid #f59e0b; }
    .alert-red   { background: linear-gradient(to right, #fef2f2, #ffffff); color: #991b1b; border: 1px solid #fecaca; border-left: 4px solid #ef4444; }
    .alert-green { background: linear-gradient(to right, #f0fdf4, #ffffff); color: #166534; border: 1px solid #bbf7d0; border-left: 4px solid #22c55e; }

    /* ── Terminal Style (Modern) ──────────────────────────── */
    .terminal-header {
        background: #0f172a; border: 1px solid #1e293b;
        border-bottom: none; border-radius: 16px 16px 0 0;
        padding: 1rem 1.5rem; display: flex; align-items: center; gap: 10px;
    }
    .terminal-dot { width: 14px; height: 14px; border-radius: 50%; }
    .terminal-dot.red { background: #ef4444; }
    .terminal-dot.yellow { background: #f59e0b; }
    .terminal-dot.green { background: #10b981; }

    /* ── Monospace ─────────────────────────────────────────── */
    .mono { font-family: 'JetBrains Mono', monospace; font-size: 0.9em; font-weight: 500; }

    /* ── Custom UI Element Overrides ─────────────────────── */
    [data-testid="stMetricLabel"] { font-family: 'Outfit', sans-serif !important; font-weight: 700 !important; text-transform: uppercase; letter-spacing: 0.08em; color: #64748b !important; }
    [data-testid="stMetricValue"] { font-family: 'Outfit', sans-serif !important; font-size: 2.5rem !important; font-weight: 900 !important; color: #0f172a !important; letter-spacing: -0.03em !important; }
    
    .stButton > button {
        background: linear-gradient(135deg, #0f172a, #1e293b) !important;
        color: #ffffff !important; border: 1px solid rgba(255,255,255,0.1) !important;
        border-radius: 12px !important; font-weight: 700 !important; font-family: 'Outfit', sans-serif !important;
        padding: 0.8rem 2.5rem !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.15) !important;
        letter-spacing: 0.05em !important;
    }
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 15px 20px -5px rgba(0, 0, 0, 0.2) !important;
        border-color: rgba(255,255,255,0.2) !important;
    }
    
    div[data-testid="stExpander"] {
        background: rgba(255, 255, 255, 0.7) !important;
        backdrop-filter: blur(10px) !important;
        -webkit-backdrop-filter: blur(10px) !important;
        border: 1px solid rgba(0,0,0,0.05) !important;
        border-radius: 16px !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.02) !important;
    }
    
    [data-testid="stDataFrame"] {
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        overflow: hidden;
        box-shadow: 0 10px 15px -3px rgba(0,0,0,0.05);
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
