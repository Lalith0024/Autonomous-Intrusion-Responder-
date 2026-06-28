"""AIR V2 — Incident Dashboard.

Batch analysis telemetry with professional light-mode visualizations.
Clean data grids and threat distribution charts.
"""

import json
from pathlib import Path
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src.core.config import settings
from src.streamlit_app.layout import get_severity_badge

RESULTS_PATH = Path(settings.BATCH_RESULTS_PATH)
BLOCKED_PATH = Path(settings.BLOCKED_IPS_PATH)

# Professional Curved Palette
SEV_COLORS    = {"critical": "#dc2626", "high": "#ea580c", "medium": "#d97706", "low": "#16a34a", "info": "#2563eb"}
ATTACK_COLORS = {
    "brute_force": "#e11d48", "denial_of_service": "#f97316", "sql_injection": "#d97706",
    "port_scan": "#7c3aed", "unknown": "#64748b", "normal_traffic": "#10b981",
    "cross_site_scripting": "#0891b2", "command_injection": "#db2777"
}
SEV_ORDER     = ["critical", "high", "medium", "low", "info"]

LIGHT_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#475569", family="Inter", size=11),
    margin=dict(l=0, r=40, t=20, b=20),
    showlegend=False,
)

@st.cache_data
def load_batch(path: Path) -> dict:
    return json.loads(path.read_text())

def _path_label(path: list[str]) -> str:
    names = {"investigation_node": "Checking Data", "triage_node": "Thinking", "severity_router": "Determining Risk",
             "response_agent": "Taking Action", "human_review_node": "Specialist Review", "memory_persist_node": "Saving Info"}
    return " → ".join(names.get(n, n.title()) for n in path)


st.markdown('<div class="page-title">📊 Threat Intelligence</div>', unsafe_allow_html=True)
st.markdown('<div class="page-subtitle">Aggregated telemetry from processed network flows. Observe system performance, routing patterns, and detection density.</div>', unsafe_allow_html=True)

if not RESULTS_PATH.exists():
    st.markdown('''<div class="alert alert-amber"><strong>NO DATA:</strong> Archive currently empty.</div>''', unsafe_allow_html=True)
    st.stop()

try:
    data = load_batch(RESULTS_PATH)
    results = data.get("results", [])
    reports = [r["incident_report"] for r in results]
    total_n = len(results)
except Exception as e:
    st.error(f"Archive load failed: {e}")
    st.stop()

# ── Metrics ──
sevs = [r.get("severity", "info") for r in reports]
threats = sum(1 for s in sevs if s in ("critical", "high", "medium"))
reviews = sum(1 for r in reports if r.get("needs_human_review"))
avg_conf = sum(r.get("confidence_score", 0) for r in reports) / total_n if total_n else 0

m1, m2, m3, m4 = st.columns(4)
m1.markdown(f'<div class="ui-card border-left-blue"><div class="ui-card-title">Archived Flows</div><div class="ui-card-value" style="color:#1e293b;">{total_n}</div></div>', unsafe_allow_html=True)
m2.markdown(f'<div class="ui-card border-left-red"><div class="ui-card-title">Threat Density</div><div class="ui-card-value" style="color:#dc2626;">{threats}</div></div>', unsafe_allow_html=True)
m3.markdown(f'<div class="ui-card border-left-amber"><div class="ui-card-title">Escalations</div><div class="ui-card-value" style="color:#d97706;">{reviews}</div></div>', unsafe_allow_html=True)
m4.markdown(f'<div class="ui-card border-left-green"><div class="ui-card-title">Mean Confidence</div><div class="ui-card-value" style="color:#16a34a;">{avg_conf:.0%}</div></div>', unsafe_allow_html=True)

# ── Distribution ──
st.markdown('<div class="section-header">Distribution Profiling</div>', unsafe_allow_html=True)
chart_l, chart_r = st.columns(2)

attack_counts = {}
for r in reports:
    k = r.get("attack_type", "unknown")
    attack_counts[k] = attack_counts.get(k, 0) + 1

with chart_l:
    st.markdown('<div class="ui-card">', unsafe_allow_html=True)
    st.markdown('<div class="ui-card-title">Signature Frequency</div>', unsafe_allow_html=True)
    if attack_counts:
        keys = sorted(attack_counts.keys(), key=lambda x: -attack_counts[x])
        labels = [k.replace("_", " ").title() for k in keys]
        values = [attack_counts[k] for k in keys]
        clrs = [ATTACK_COLORS.get(k, "#64748b") for k in keys]
        fig = go.Figure(go.Bar(
            x=values, y=labels, orientation="h",
            marker=dict(color=clrs, line=dict(width=0)),
            text=[f"{v}" for v in values], textposition="auto",
            textfont=dict(size=11, color="white", font="Inter"),
        ))
        fig.update_layout(height=280, xaxis=dict(showgrid=False, zeroline=False), yaxis=dict(autorange="reversed"), **LIGHT_LAYOUT)
        st.plotly_chart(fig, )
    st.markdown('</div>', unsafe_allow_html=True)

sev_counts = {}
for s in sevs:
    sev_counts[s] = sev_counts.get(s, 0) + 1

with chart_r:
    st.markdown('<div class="ui-card">', unsafe_allow_html=True)
    st.markdown('<div class="ui-card-title">Severity Density</div>', unsafe_allow_html=True)
    if sev_counts:
        o_lbls = [k.title() for k in SEV_ORDER if k in sev_counts]
        o_vals = [sev_counts[k] for k in SEV_ORDER if k in sev_counts]
        o_clrs = [SEV_COLORS.get(k, "#64748b") for k in SEV_ORDER if k in sev_counts]
        fig2 = go.Figure(go.Pie(
            labels=o_lbls, values=o_vals, hole=0.7,
            marker=dict(colors=o_clrs, line=dict(color="#ffffff", width=2)),
            textinfo="none",
        ))
        fig2.add_annotation(text=f"Total<br><b style='font-size:24px; color:#1e293b;'>{total_n}</b>", x=0.5, y=0.5, showarrow=False)
        fig2.update_layout(height=280, **LIGHT_LAYOUT)
        st.plotly_chart(fig2, )
    st.markdown('</div>', unsafe_allow_html=True)

# ── Blocked ──
if BLOCKED_PATH.exists():
    try:
        blocked = json.loads(BLOCKED_PATH.read_text())
        if blocked:
            st.markdown('<div class="section-header">🔒 Active Containment List</div>', unsafe_allow_html=True)
            st.markdown('<div class="ui-card">', unsafe_allow_html=True)
            for entry in blocked:
                st.markdown(f'''
                <div style="display:flex; align-items:center; gap:2rem; padding:1rem 0; border-bottom:1px solid #f1f5f9;">
                    <div style="font-family:JetBrains Mono,monospace; font-size:0.9rem; color:#dc2626; font-weight:800; width:150px;">{entry.get("ip_address","?")}</div>
                    <div style="flex:1; font-size:0.85rem; color:#475569; font-weight:500;">{entry.get("reason","?")}</div>
                    <span class="badge badge-blocked">CONTAINED</span>
                </div>''', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
    except Exception:
        pass

# ── Logic History ──
st.markdown('<div class="section-header">Decision Flow History</div>', unsafe_allow_html=True)
path_counts = {}
for r in reports:
    lbl = _path_label(r.get("graph_path", []))
    path_counts[lbl] = path_counts.get(lbl, 0) + 1

st.markdown('<div class="ui-card">', unsafe_allow_html=True)
for label, count in sorted(path_counts.items(), key=lambda x: -x[1]):
    pct = count / total_n
    st.markdown(f'''
    <div style="margin-bottom:1.25rem;">
        <div style="display:flex; justify-content:space-between; font-size:0.8rem; font-weight:700; color:#475569; margin-bottom:0.5rem;">
            <span>{label}</span>
            <span>{count} flows ({pct:.0%})</span>
        </div>
        <div style="height:8px; background:#f1f5f9; border-radius:4px; overflow:hidden;">
            <div style="width:{pct*100}%; height:100%; background:#4f46e5;"></div>
        </div>
    </div>''', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# ── Table ──
st.markdown('<div class="section-header">Incident Registry</div>', unsafe_allow_html=True)
table_data = []
for i, result in enumerate(results):
    rep = result["incident_report"]
    table_data.append({
        "Idx": i,
        "Threat": rep.get("attack_type", "?").replace("_", " ").title(),
        "Severity": rep.get("severity", "info").upper(),
        "Confidence": rep.get("confidence_score", 0),
        "Source": rep.get("source_ip", "?"),
        "Status": "CONTAINED" if rep.get("blocked") else "MONITORED"
    })

df = pd.DataFrame(table_data).drop(columns=["Idx"])
sel = st.dataframe(df, height=350, on_select="rerun", selection_mode="single-row")

if hasattr(sel, "selection") and sel.selection.rows:
    idx = sel.selection.rows[0]
    rep = results[idx]["incident_report"]
    st.markdown('<div class="section-header">Inspection Detail</div>', unsafe_allow_html=True)
    st.markdown(f'''
    <div class="ui-card border-left-blue">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1.5rem; border-bottom:1px solid #f1f5f9; padding-bottom:1rem;">
            <div style="font-size:1.25rem; font-weight:900; color:#1e293b;">{rep.get("attack_type","?").replace("_"," ").title()}</div>
            {get_severity_badge(rep.get("severity", "info"))}
        </div>
        <div style="font-size:0.9rem; color:#475569; line-height:1.8; margin-bottom:1.5rem;">
            <strong style="color:#0f172a;">Analyst Post-Mortem:</strong><br>{rep.get("reasoning","No context available.")}
        </div>
        <div style="display:flex; gap:2rem;">
            <div><div class="ui-card-title">Source IP</div><div style="font-weight:800; font-family:JetBrains Mono,monospace;">{rep.get("source_ip","?") or "?"}</div></div>
            <div><div class="ui-card-title">Confidence</div><div style="font-weight:800; color:#4f46e5;">{rep.get("confidence_score",0):.0%}</div></div>
            <div><div class="ui-card-title">Action</div><div style="font-weight:800; color:#16a34a;">{rep.get("recommended_action","?").title()}</div></div>
        </div>
    </div>''', unsafe_allow_html=True)
