"""AIR V2 — Overview Dashboard.

Shows system health, key metrics, architecture overview, and recent activity.
Clean light-mode interface for a professional SOC experience.
"""

import streamlit as st
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from src.core.config import settings

st.set_page_config(page_title="AIR — Cyber Command", layout="wide", initial_sidebar_state="expanded")

from src.streamlit_app.layout import inject_ui
inject_ui()

pg = st.navigation([
    st.Page("dashboard_content.py", title="Overview", icon="🏠"),
    st.Page("pages/0_About.py", title="About AIR", icon="ℹ️"),
    st.Page("pages/1_Live_Analysis.py", title="Live Analysis", icon="⚡"),
    st.Page("pages/2_Incident_Dashboard.py", title="Incident History", icon="📊"),
    st.Page("pages/3_Eval_Results.py", title="Performance", icon="📈"),
])
pg.run()

BLOCKED_PATH = Path(settings.BLOCKED_IPS_PATH)

# ── Main Content ──
st.markdown('''
<div class="page-title">General Overview</div>
<div class="page-subtitle">A high-level view of system activity and security performance. The AI agent automatically handles threat detection and active response, ensuring zero-trust enforcement in real time.</div>
''', unsafe_allow_html=True)

# ── Load Available Data ──
batch_data = None
if BATCH_PATH.exists():
    try:
        batch_data = json.loads(BATCH_PATH.read_text())
    except Exception:
        pass

blocked_count = 0
if BLOCKED_PATH.exists():
    try:
        blocked = json.loads(BLOCKED_PATH.read_text())
        blocked_count = len(blocked)
    except Exception:
        pass

if not batch_data:
    st.markdown('<div class="alert alert-amber"><strong>No Activity Data:</strong> Run the batch evaluations to populate this dashboard.</div>', unsafe_allow_html=True)
    total_events = 0
    accuracy = 0
    avg_lat = 0
else:
    total_events = batch_data.get("total", 0)
    accuracy = batch_data.get("accuracy_pct", 0)
    avg_lat = batch_data.get("avg_latency_s", 0)

# ── Main Cards ──
m1, m2, m3 = st.columns(3)

with m1:
    st.markdown(f'''
    <div class="ui-card border-left-blue">
        <div class="ui-card-title">Real-time Analysis</div>
        <div class="ui-card-value">{total_events}</div>
        <div style="font-size:0.9rem; color:#64748b; margin-top:1rem;">Total security logs processed by the system.</div>
    </div>''', unsafe_allow_html=True)

with m2:
    st.markdown(f'''
    <div class="ui-card border-left-green">
        <div class="ui-card-title">System Accuracy</div>
        <div class="ui-card-value">{accuracy}%</div>
        <div style="font-size:0.9rem; color:#64748b; margin-top:1rem;">Correct decisions vs. known security benchmarks.</div>
    </div>''', unsafe_allow_html=True)

with m3:
    st.markdown(f'''
    <div class="ui-card border-left-amber">
        <div class="ui-card-title">Performance</div>
        <div class="ui-card-value">{avg_lat}s</div>
        <div style="font-size:0.9rem; color:#64748b; margin-top:1rem;">Average time to complete a security check.</div>
    </div>''', unsafe_allow_html=True)


# ── Comparison Section ──
st.markdown('<div class="section-header">Traditional Method vs. AI Agent</div>', unsafe_allow_html=True)

c4, c5 = st.columns(2)

with c4:
    st.markdown("""
    <div class="ui-card border-left-slate">
        <div class="ui-card-title">Basic Classifier</div>
        <div style="font-size:0.9rem; line-height:1.8; color:#334155;">
            Follows a fixed set of rules to label data.<br>
            Cannot search for new info or verify threats.<br>
            Does not have memory of previous events.<br>
            Only provides labels, not actions.
        </div>
    </div>
    """, unsafe_allow_html=True)

with c5:
    st.markdown("""
    <div class="ui-card border-left-blue">
        <div class="ui-card-title">AI Security Agent</div>
        <div style="font-size:0.9rem; line-height:1.8; color:#334155;">
            <strong>Proactive Investigation:</strong> Looks up IPs and ports.<br>
            <strong>Memory Context:</strong> Remembers similar past attacks.<br>
            <strong>Decision Logic:</strong> Reasons through the steps to take.<br>
            <strong>Immediate Action:</strong> Stops threats as they happen.
        </div>
    </div>
    """, unsafe_allow_html=True)


# ── Recent Activity (Muted Professional Style) ──
if batch_data and batch_data.get("results"):
    st.markdown('<div class="section-header">Registry activity</div>', unsafe_allow_html=True)

    for r in batch_data["results"][-5:]:
        rep = r.get("incident_report", {})
        sev = rep.get("severity", "info")
        attack = rep.get("attack_type", "?").replace("_", " ").title()
        conf = rep.get("confidence_score", 0)
        ip = rep.get("source_ip", "?")

        sev_colors = {"critical": "#ef4444", "high": "#f97316", "medium": "#f59e0b", "low": "#10b981", "info": "#3b82f6"}
        color = sev_colors.get(sev, "#64748b")

        st.markdown(f'''
        <div style="display:flex; align-items:center; gap:1.25rem; padding:1rem 0; border-bottom:1px solid #f1f5f9;">
            <div style="width:10px; height:10px; border-radius:50%; background:{color}; flex-shrink:0;"></div>
            <div style="flex:1; font-size:0.9rem; font-weight:700; color:#1e293b;">{attack}</div>
            <div style="font-size:0.8rem; color:#64748b; font-family:'JetBrains Mono',monospace; background: #f8fafc; padding: 0.2rem 0.5rem; border-radius: 4px; border: 1px solid #e2e8f0;">{ip}</div>
            <div style="font-size:0.85rem; font-weight:800; color:{color};">{conf:.0%}</div>
        </div>
        ''', unsafe_allow_html=True)
