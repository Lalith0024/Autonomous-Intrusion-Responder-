import json
from pathlib import Path
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import sys

# Fix import path for UI module
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from src.streamlit_app.layout import inject_ui, get_severity_badge

st.set_page_config(page_title="AIR - Incident Dashboard", layout="wide", initial_sidebar_state="expanded")
inject_ui()

RESULTS_PATH = Path("data/results/batch_results.json")

SEV_COLORS    = {"critical": "#ef4444", "high": "#ea580c", "medium": "#f59e0b", "low": "#22c55e", "info": "#3b82f6"}
ATTACK_COLORS = {"brute_force": "#ef4444", "denial_of_service": "#ea580c", "sql_injection": "#f59e0b",
                 "port_scan": "#a855f7", "unknown": "#64748b", "normal_traffic": "#22c55e"}
SEV_ORDER     = ["critical", "high", "medium", "low", "info"]

@st.cache_data
def load_batch(path: Path) -> dict:
    return json.loads(path.read_text())

def _path_label(path: list[str]) -> str:
    names = {"triage_node": "Triage", "severity_router": "Policy Router",
             "response_agent": "Response Agent", "human_review_node": "Analyst Review"}
    return "  →  ".join(names.get(n, n.title()) for n in path)

st.markdown('<div class="page-title">Incident Dashboard</div>', unsafe_allow_html=True)
st.markdown('<div class="page-subtitle">Batch analysis overview from CICIDS 2017 dataset. Review threat density, orchestration metrics, and aggregated telemetry.</div>', unsafe_allow_html=True)

if not RESULTS_PATH.exists():
    st.markdown("""
    <div class="alert alert-amber" style="max-width: 600px;">
        <strong>No Telemetry Captured:</strong> Execute the batch command to process the network capture:<br><br>
        <code class="mono">python src/data/batch_runner.py</code>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

try:
    data     = load_batch(RESULTS_PATH)
    results  = data.get("results", [])
    reports  = [r["incident_report"] for r in results]
    total_n  = len(results)
except Exception as e:
    st.markdown(f'<div class="alert alert-red"><strong>Data Error:</strong> Unable to index batch results. {e}</div>', unsafe_allow_html=True)
    st.stop()

# ── Metrics Row ──
sevs     = [r.get("severity", "info") for r in reports]
threats  = sum(1 for s in sevs if s in ("critical", "high", "medium"))
reviews  = sum(1 for r in reports if r.get("needs_human_review"))
avg_conf = sum(r.get("confidence_score", 0) for r in reports) / total_n if total_n else 0

st.markdown('<div class="section-header" style="margin-top: 1rem;">Telemetry Summary</div>', unsafe_allow_html=True)

m1, m2, m3, m4 = st.columns(4)
m1.markdown(f'<div class="ui-card border-left-blue"><div class="ui-card-title">Processed Flows</div><div class="ui-card-value text-blue">{total_n}</div></div>', unsafe_allow_html=True)
m2.markdown(f'<div class="ui-card border-left-red"><div class="ui-card-title">Identified Threats</div><div class="ui-card-value text-red">{threats}</div></div>', unsafe_allow_html=True)
m3.markdown(f'<div class="ui-card border-left-amber"><div class="ui-card-title">Escalated for Review</div><div class="ui-card-value text-amber">{reviews}</div></div>', unsafe_allow_html=True)
m4.markdown(f'<div class="ui-card border-left-green"><div class="ui-card-title">Mean Agent Confidence</div><div class="ui-card-value text-green">{avg_conf:.0%}</div></div>', unsafe_allow_html=True)


# ── Distributions Row ──
st.markdown('<div class="section-header">Distribution Profiling</div>', unsafe_allow_html=True)
chart_l, chart_r = st.columns(2)

attack_counts: dict[str, int] = {}
for r in reports:
    k = r.get("attack_type", "unknown")
    attack_counts[k] = attack_counts.get(k, 0) + 1

with chart_l:
    st.markdown('<div class="ui-card" style="padding-bottom:0;">', unsafe_allow_html=True)
    st.markdown('<div class="ui-card-title">Signature Frequency Map</div>', unsafe_allow_html=True)
    if attack_counts:
        labels = [k.replace("_", " ").title() for k in attack_counts]
        values = list(attack_counts.values())
        clrs   = [ATTACK_COLORS.get(k, "#64748b") for k in attack_counts]
        fig = go.Figure(go.Bar(
            x=values, y=labels, orientation="h",
            marker=dict(color=clrs, line=dict(width=0)),
            text=[f"{v}" for v in values], textposition="outside",
            textfont=dict(size=12, color="#0f172a", family="Inter")
        ))
        fig.update_layout(
            height=260, margin=dict(l=0, r=40, t=10, b=10),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
            yaxis=dict(tickfont=dict(size=12, color="#334155", family="Inter")),
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

sev_counts: dict[str, int] = {}
for s in sevs:
    sev_counts[s] = sev_counts.get(s, 0) + 1

with chart_r:
    st.markdown('<div class="ui-card" style="padding-bottom:0;">', unsafe_allow_html=True)
    st.markdown('<div class="ui-card-title">Severity Segmentation</div>', unsafe_allow_html=True)
    if sev_counts:
        o_lbls = [k.title() for k in SEV_ORDER if k in sev_counts]
        o_vals = [sev_counts[k] for k in SEV_ORDER if k in sev_counts]
        o_clrs = [SEV_COLORS.get(k, "#64748b") for k in SEV_ORDER if k in sev_counts]
        fig2 = go.Figure(go.Pie(
            labels=o_lbls, values=o_vals, hole=0.6,
            marker=dict(colors=o_clrs, line=dict(color="#ffffff", width=2)),
            textinfo="label+percent", textfont=dict(size=11, family="Inter"),
            pull=[0.05 if k in ("critical", "high") else 0 for k in SEV_ORDER if k in sev_counts],
        ))
        fig2.add_annotation(text=f"<span style='font-size:24px; font-weight:800; color:#0f172a;'>{total_n}</span><br><span style='font-size:12px; color:#64748b;'>Flows</span>",
                            x=0.5, y=0.5, showarrow=False)
        fig2.update_layout(
            height=260, margin=dict(l=0, r=0, t=10, b=10),
            paper_bgcolor="rgba(0,0,0,0)", showlegend=False
        )
        st.plotly_chart(fig2, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)


# ── Routing Path ──
st.markdown('<div class="section-header">LangGraph Routing Matrices</div>', unsafe_allow_html=True)
st.markdown('<div class="ui-card-desc" style="margin-top:-1rem; margin-bottom:1.5rem;">Observed execution pathways. Dynamic routing serves as empirical proof of agent-based autonomy over linear classification.</div>', unsafe_allow_html=True)

path_counts: dict[str, int] = {}
for r in reports:
    lbl = _path_label(r.get("graph_path", []))
    path_counts[lbl] = path_counts.get(lbl, 0) + 1

st.markdown('<div class="ui-card">', unsafe_allow_html=True)
sorted_paths = sorted(path_counts.items(), key=lambda x: -x[1])
for label, count in sorted_paths:
    pct = count / total_n
    color = "#22c55e" if "Response" in label else "#a855f7" if "Review" in label else "#3b82f6"
    
    st.markdown(f"""
    <div style="display:flex; align-items:center; gap:16px; margin-bottom:12px;">
        <div style="width:240px; font-size:0.85rem; font-weight:600; color:#334155;">{label}</div>
        <div style="flex:1; height:8px; background:#f1f5f9; border-radius:9999px;">
            <div style="height:8px; width:{pct*100}%; background:{color}; border-radius:9999px;"></div>
        </div>
        <div style="font-size:0.85rem; font-weight:800; color:{color}; width:80px; text-align:right;">{count} occurrences</div>
    </div>
    """, unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)


# ── Incident Table ──
st.markdown('<div class="section-header">Incident Registry</div>', unsafe_allow_html=True)

rows = []
for i, r in enumerate(results):
    rep = r["incident_report"]
    rows.append({
        "Idx": i,
        "Classification": rep.get("attack_type", "?").replace("_", " ").title(),
        "Severity": rep.get("severity", "info").title(),
        "Agent Confidence": float(round(rep.get("confidence_score", 0), 2)),
        "Source Address": rep.get("source_ip", "?"),
        "Target Action": rep.get("recommended_action", "?").replace("_", " ").title(),
    })

df = pd.DataFrame(rows).drop(columns=["Idx"])

with st.container():
    sel = st.dataframe(
        df, use_container_width=True, height=400,
        on_select="rerun", selection_mode="single-row",
        column_config={
            "Agent Confidence": st.column_config.ProgressColumn("Agent Confidence", min_value=0.0, max_value=1.0, format="%.2f"),
        }
    )

    if hasattr(sel, "selection") and sel.selection and sel.selection.rows:
        idx = sel.selection.rows[0]
        rep = results[idx]["incident_report"]
        sev = rep.get("severity", "info")
        
        st.markdown('<div class="section-header" style="margin-top: 2rem;">Registry Inspection</div>', unsafe_allow_html=True)
        st.markdown(f'''
        <div class="ui-card">
            <div style="display:flex; align-items:center; gap:1rem; margin-bottom:1rem; border-bottom:1px solid #e2e8f0; padding-bottom:1rem;">
                <div style="font-size:1.25rem; font-weight:800; color:#0f172a;">{rep.get('attack_type','?').replace('_',' ').title()}</div>
                <div style="font-size:0.85rem; padding:0.25rem 0.5rem; background:#f1f5f9; border-radius:4px; font-weight:600;">{rep.get('source_ip','')}</div>
                <div style="margin-left:auto;">{get_severity_badge(sev)}</div>
            </div>
            
            <div style="display:flex; gap:2rem; margin-bottom:1.5rem;">
                <div><div class="ui-card-title">Confidence</div><div style="font-weight:700; font-size:1.1rem; color:#0f172a;">{rep.get('confidence_score',0):.0%}</div></div>
                <div><div class="ui-card-title">Intervention</div><div style="font-weight:700; font-size:1.1rem; color:#0f172a;">{'Required' if rep.get('needs_human_review') else 'Suppressed'}</div></div>
                <div><div class="ui-card-title">Event Identifier</div><div style="font-weight:500; font-size:1rem; color:#475569; font-family:'JetBrains Mono',monospace;">{rep.get('event_id','')}</div></div>
            </div>
            
            <div class="ui-card-title">Orchestrator Reasoning Matrix</div>
            <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:6px; padding:1.25rem; font-size:0.9rem; line-height:1.6; color:#334155;">
                {rep.get('reasoning','')}
            </div>
        </div>
        ''', unsafe_allow_html=True)
