"""Page 2: Incident Dashboard — batch CICIDS analysis results."""

import json
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

RESULTS_PATH = Path("data/results/batch_results.json")

SEV_COLORS    = {"critical": "#ef4444", "high": "#f97316", "medium": "#f59e0b", "low": "#10b981", "info": "#3b82f6"}
ATTACK_COLORS = {"brute_force": "#ef4444", "denial_of_service": "#f97316", "sql_injection": "#f59e0b",
                 "port_scan": "#a78bfa", "unknown": "#6b7280", "normal_traffic": "#10b981"}
SEV_PILL_MAP  = {"critical": "pill-critical", "high": "pill-high", "medium": "pill-medium", "low": "pill-low", "info": "pill-info"}
SEV_ORDER     = ["critical", "high", "medium", "low", "info"]
SEV_DOT       = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢", "info": "🔵"}


@st.cache_data
def load_batch(path: Path) -> dict:
    return json.loads(path.read_text())


def _pill(sev: str) -> str:
    cls = SEV_PILL_MAP.get(sev.lower(), "pill-info")
    dot = SEV_DOT.get(sev.lower(), "⚪")
    return f'<span class="pill {cls}">{dot} {sev.upper()}</span>'


def _path_label(path: list[str]) -> str:
    names = {"triage_node": "Triage", "severity_router": "Router",
             "response_agent": "Response", "human_review_node": "Human Review"}
    return " → ".join(names.get(n, n.title()) for n in path)


# ── Guard ─────────────────────────────────────────────────────────────────────
st.markdown('<div class="sec-label" style="margin-top:0;">INCIDENT DASHBOARD</div>', unsafe_allow_html=True)

if not RESULTS_PATH.exists():
    st.markdown('<div class="page-header"><h1>Incident Dashboard</h1></div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="card card-accent-amber" style="max-width:560px;">
        <div style="font-size:1rem; font-weight:700; color:#b45309; margin-bottom:8px;">⚠ No batch data found</div>
        <div style="font-size:0.84rem; color:#6b7280; line-height:1.65;">
            Run the batch analyzer to populate this dashboard:<br><br>
            <code>python src/data/batch_runner.py</code><br><br>
            Make sure the API is running first: <code>python run.py</code>
        </div>
    </div>""", unsafe_allow_html=True)
    st.stop()

data     = load_batch(RESULTS_PATH)
results  = data.get("results", [])
reports  = [r["incident_report"] for r in results]
n        = len(results)
run_at   = data.get("run_at", "")[:10]

st.markdown(f'<div class="page-header"><h1>Incident Dashboard</h1><p>{n} real network events analyzed from the CICIDS dataset · {run_at}</p></div>', unsafe_allow_html=True)

# ── Row 1: Metrics ─────────────────────────────────────────────────────────────
sevs     = [r.get("severity", "info") for r in reports]
threats  = sum(1 for s in sevs if s in ("critical", "high", "medium"))
reviews  = sum(1 for r in reports if r.get("needs_human_review"))
avg_conf = sum(r.get("confidence_score", 0) for r in reports) / n if n else 0
acc      = data.get("accuracy_pct", 0)

st.markdown('<div class="sec-label">SUMMARY METRICS</div>', unsafe_allow_html=True)
m1, m2, m3, m4 = st.columns(4)
for col, val, lbl, color in [
    (m1, str(n),          "Total Events",          "metric-blue"),
    (m2, str(threats),    "Threats Detected",      "metric-red"),
    (m3, str(reviews),    "Flagged for Review",    "metric-amber"),
    (m4, f"{avg_conf:.0%}", "Avg Confidence",      "metric-green"),
]:
    with col:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">{lbl}</div>
            <div class="metric-val {color}">{val}</div>
        </div>""", unsafe_allow_html=True)

# ── Row 2: Charts ─────────────────────────────────────────────────────────────
st.markdown('<div class="sec-label">DISTRIBUTIONS</div>', unsafe_allow_html=True)
chart_l, chart_r = st.columns(2)

# Attack type horizontal bar
attack_counts: dict[str, int] = {}
for r in reports:
    k = r.get("attack_type", "unknown")
    attack_counts[k] = attack_counts.get(k, 0) + 1

with chart_l:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div style="font-size:0.85rem; font-weight:700; color:#111827; margin-bottom:0.75rem;">Attack Type Distribution</div>', unsafe_allow_html=True)
    if attack_counts:
        labels = [k.replace("_", " ").title() for k in attack_counts]
        values = list(attack_counts.values())
        clrs   = [ATTACK_COLORS.get(k, "#6b7280") for k in attack_counts]
        fig = go.Figure(go.Bar(
            x=values, y=labels, orientation="h",
            marker=dict(color=clrs, line=dict(width=0)),
            text=[f"{v}" for v in values],
            textposition="outside",
            textfont=dict(size=11, color="#374151"),
        ))
        fig.update_layout(
            height=260, margin=dict(l=0, r=30, t=5, b=5),
            paper_bgcolor="white", plot_bgcolor="white",
            xaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
            yaxis=dict(tickfont=dict(size=11, color="#374151")),
            showlegend=False,
        )
        st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# Severity donut
sev_counts: dict[str, int] = {}
for s in sevs:
    sev_counts[s] = sev_counts.get(s, 0) + 1

with chart_r:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div style="font-size:0.85rem; font-weight:700; color:#111827; margin-bottom:0.75rem;">Severity Breakdown</div>', unsafe_allow_html=True)
    if sev_counts:
        ordered_labels = [k.title() for k in SEV_ORDER if k in sev_counts]
        ordered_vals   = [sev_counts[k] for k in SEV_ORDER if k in sev_counts]
        ordered_clrs   = [SEV_COLORS.get(k, "#6b7280") for k in SEV_ORDER if k in sev_counts]
        fig2 = go.Figure(go.Pie(
            labels=ordered_labels, values=ordered_vals, hole=0.6,
            marker=dict(colors=ordered_clrs, line=dict(color="#ffffff", width=2)),
            textinfo="label+percent", textfont=dict(size=11),
            pull=[0.04 if k in ("critical", "high") else 0 for k in SEV_ORDER if k in sev_counts],
        ))
        fig2.add_annotation(text=f"<b>{n}</b><br><span style='font-size:10px'>events</span>",
                            x=0.5, y=0.5, showarrow=False, font=dict(size=14, color="#111827"))
        fig2.update_layout(
            height=260, margin=dict(l=0, r=0, t=5, b=5),
            paper_bgcolor="white", showlegend=False,
        )
        st.plotly_chart(fig2, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ── Row 3: Agent Routing ──────────────────────────────────────────────────────
st.markdown('<div class="sec-label">MULTI-AGENT ROUTING — how the pipeline decided</div>', unsafe_allow_html=True)

path_counts: dict[str, int] = {}
for r in reports:
    lbl = _path_label(r.get("graph_path", []))
    path_counts[lbl] = path_counts.get(lbl, 0) + 1

path_colors = {"Triage → Router → Response": "#10b981",
               "Triage → Router":            "#3b82f6",
               "Triage → Router → Human Review": "#8b5cf6"}

st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown('<div style="font-size:0.84rem; color:#6b7280; margin-bottom:0.75rem;">This breakdown proves the system is an agent — different threat profiles trigger different decision paths through the graph.</div>', unsafe_allow_html=True)

sorted_paths = sorted(path_counts.items(), key=lambda x: -x[1])
for path_label, count in sorted_paths:
    pct = count / n
    color = "#10b981" if "Response" in path_label else "#8b5cf6" if "Human" in path_label else "#3b82f6"
    st.markdown(f"""
    <div style="display:flex; align-items:center; gap:12px; margin-bottom:10px;">
        <div style="width:180px; font-size:0.78rem; color:#374151; font-weight:600; flex-shrink:0;">{path_label}</div>
        <div style="flex:1; height:10px; background:#f3f4f6; border-radius:9999px; overflow:hidden;">
            <div style="height:10px; width:{pct*100}%; background:{color}; border-radius:9999px;"></div>
        </div>
        <div style="font-size:0.8rem; font-weight:700; color:{color}; width:60px; text-align:right;">{count} events</div>
    </div>""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ── Row 4: Incident Table ─────────────────────────────────────────────────────
st.markdown('<div class="sec-label">INCIDENT HISTORY</div>', unsafe_allow_html=True)

rows = []
for i, r in enumerate(results):
    rep = r["incident_report"]
    sev = rep.get("severity", "info")
    rows.append({
        "idx": i,
        " ": SEV_DOT.get(sev, "⚪"),
        "Attack Type": rep.get("attack_type", "?").replace("_", " ").title(),
        "Severity": sev.title(),
        "Confidence": round(rep.get("confidence_score", 0), 2),
        "Source IP": rep.get("source_ip", "?"),
        "Path": _path_label(rep.get("graph_path", [])),
        "Action": rep.get("recommended_action", "?").replace("_", " ").title(),
        "Latency": f"{r.get('latency_s', 0):.1f}s",
    })

df = pd.DataFrame(rows).drop(columns=["idx"])

with st.container(border=True):
    sel = st.dataframe(
        df, use_container_width=True, height=330,
        on_select="rerun", selection_mode="single-row",
        column_config={
            "Confidence": st.column_config.ProgressColumn("Confidence", min_value=0, max_value=1, format="%.0f%%"),
            " ": st.column_config.TextColumn(" ", width="small"),
        }
    )
    sel_rows = sel.selection.rows if hasattr(sel, "selection") and sel.selection else []
    if sel_rows:
        idx = sel_rows[0]
        rep = results[idx]["incident_report"]
        sev = rep.get("severity", "info")
        accent = "red" if sev in ("critical","high") else "amber" if sev == "medium" else "green"

        with st.expander(f"📋 Full Report — {rep.get('attack_type','?').replace('_',' ').title()} from {rep.get('source_ip','')}", expanded=True):
            e1, e2, e3, e4 = st.columns(4)
            with e1: st.metric("Severity", sev.title())
            with e2: st.metric("Confidence", f"{rep.get('confidence_score',0):.0%}")
            with e3: st.metric("Human Review", "Yes" if rep.get("needs_human_review") else "No")
            with e4: st.metric("Event ID", rep.get("event_id","")[:8] + "...")

            st.markdown(f'<div class="reasoning" style="margin-top:0.5rem;">{rep.get("reasoning","")}</div>', unsafe_allow_html=True)

            if rep.get("response_plan"):
                plan = rep["response_plan"]
                st.markdown('<div class="sec-label">RESPONSE STEPS</div>', unsafe_allow_html=True)
                for j, step in enumerate(plan.get("response_steps", []), 1):
                    st.markdown(f"""
                    <div class="playbook-step">
                        <div class="step-num">{j}</div>
                        <div class="step-txt">{step}</div>
                    </div>""", unsafe_allow_html=True)
