"""Page 2: Incident Dashboard — batch analysis results from CICIDS dataset."""

import json
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

RESULTS_PATH = Path("data/results/batch_results.json")

SEV_COLORS = {
    "critical": "#dc2626",
    "high": "#dc2626",
    "medium": "#d97706",
    "low": "#16a34a",
    "info": "#2563eb",
}

ATTACK_COLORS = {
    "brute_force": "#dc2626",
    "denial_of_service": "#dc2626",
    "sql_injection": "#d97706",
    "port_scan": "#d97706",
    "unknown": "#6b7280",
    "normal_traffic": "#16a34a",
}


@st.cache_data
def load_results(path: Path) -> dict:
    return json.loads(path.read_text())


def _sev_pill(sev: str) -> str:
    cls_map = {"critical": "sev-critical", "high": "sev-high", "medium": "sev-medium", "low": "sev-low"}
    cls = cls_map.get(sev.lower(), "sev-info")
    return f'<span class="{cls}">{sev.upper()}</span>'


def _path_label(path: list[str]) -> str:
    return " → ".join(n.replace("_", " ").title() for n in path)


# ── Main ──────────────────────────────────────────────────────────────────────

st.markdown('<div class="section-label" style="margin-top:0;">INCIDENT DASHBOARD</div>', unsafe_allow_html=True)

if not RESULTS_PATH.exists():
    st.markdown("# Incident Dashboard")
    st.markdown("""
    <div style="margin-top:2rem; padding:1.5rem; background:#f8f9fa; border:1px solid #e5e7eb; border-radius:10px;">
        <div style="font-weight:600; color:#1a1a1a; margin-bottom:0.5rem;">No batch data found</div>
        <div style="color:#6b7280; font-size:0.9rem;">
            Run the batch analyzer to populate this dashboard:<br><br>
            <code>python src/data/batch_runner.py</code><br><br>
            Make sure the FastAPI server is running first: <code>python run.py</code>
        </div>
    </div>""", unsafe_allow_html=True)
    st.stop()

data = load_results(RESULTS_PATH)
results = data.get("results", [])
n = len(results)

st.markdown(f"# Incident Dashboard")
st.markdown(f'<p style="color:#6b7280; margin-bottom:1.5rem;">Analysis of {n} real network events from the CICIDS 2017 dataset</p>', unsafe_allow_html=True)

# ── Row 1: Summary Metrics ─────────────────────────────────────────────────────
reports = [r["incident_report"] for r in results]
sevs = [rep.get("severity", "info") for rep in reports]
threats = sum(1 for s in sevs if s in ("high", "critical", "medium"))
human_review = sum(1 for rep in reports if rep.get("needs_human_review", False))
avg_conf = sum(rep.get("confidence_score", 0) for rep in reports) / n if n else 0

st.markdown('<div class="section-label">SUMMARY</div>', unsafe_allow_html=True)
m1, m2, m3, m4 = st.columns(4)
for col, val, lbl in [
    (m1, str(n), "Total Events"),
    (m2, str(threats), "Threats Detected"),
    (m3, str(human_review), "Human Review Flagged"),
    (m4, f"{avg_conf:.0%}", "Avg Confidence"),
]:
    with col:
        with st.container(border=True):
            st.markdown(f'<div class="stat-val">{val}</div><div class="stat-lbl">{lbl}</div>', unsafe_allow_html=True)

# ── Row 2: Charts ─────────────────────────────────────────────────────────────
st.markdown('<div class="section-label">DISTRIBUTION</div>', unsafe_allow_html=True)
chart_l, chart_r = st.columns(2)

# Attack type bar chart
attack_counts: dict[str, int] = {}
for rep in reports:
    at = rep.get("attack_type", "unknown").replace("_", " ").title()
    attack_counts[at] = attack_counts.get(at, 0) + 1

with chart_l:
    with st.container(border=True):
        st.markdown("**Attack Type Distribution**")
        if attack_counts:
            labels = list(attack_counts.keys())
            values = list(attack_counts.values())
            colors = [ATTACK_COLORS.get(k.lower().replace(" ", "_"), "#6b7280") for k in labels]
            fig = go.Figure(go.Bar(
                x=values, y=labels,
                orientation="h",
                marker_color=colors,
                text=values,
                textposition="outside",
            ))
            fig.update_layout(
                height=280,
                margin=dict(l=0, r=20, t=10, b=10),
                paper_bgcolor="white", plot_bgcolor="white",
                xaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
                yaxis=dict(tickfont=dict(size=11)),
                showlegend=False,
            )
            st.plotly_chart(fig, use_container_width=True)

# Severity donut
sev_counts: dict[str, int] = {}
for s in sevs:
    sev_counts[s] = sev_counts.get(s, 0) + 1

with chart_r:
    with st.container(border=True):
        st.markdown("**Severity Breakdown**")
        if sev_counts:
            ordered = ["critical", "high", "medium", "low", "info"]
            labels = [k.title() for k in ordered if k in sev_counts]
            vals = [sev_counts[k] for k in ordered if k in sev_counts]
            clrs = [SEV_COLORS.get(k, "#6b7280") for k in ordered if k in sev_counts]
            fig2 = go.Figure(go.Pie(
                labels=labels, values=vals,
                hole=0.55,
                marker_colors=clrs,
                textinfo="label+percent",
                textfont=dict(size=11),
            ))
            fig2.update_layout(
                height=280,
                margin=dict(l=0, r=0, t=10, b=10),
                paper_bgcolor="white",
                showlegend=False,
            )
            st.plotly_chart(fig2, use_container_width=True)

# ── Row 3: Agent Path Distribution ────────────────────────────────────────────
st.markdown('<div class="section-label">MULTI-AGENT ROUTING — how the pipeline made decisions</div>', unsafe_allow_html=True)

path_counts: dict[str, int] = {}
for rep in reports:
    label = _path_label(rep.get("graph_path", []))
    path_counts[label] = path_counts.get(label, 0) + 1

with st.container(border=True):
    path_df = pd.DataFrame(
        [{"Execution Path": k, "Events": v, "Pct": f"{v/n*100:.0f}%"} for k, v in sorted(path_counts.items(), key=lambda x: -x[1])]
    )
    if not path_df.empty:
        fig3 = px.bar(
            path_df, x="Events", y="Execution Path",
            orientation="h",
            color="Events",
            color_continuous_scale=[[0, "#dbeafe"], [1, "#2563eb"]],
            text="Events",
        )
        fig3.update_layout(
            height=max(180, len(path_df) * 55),
            margin=dict(l=0, r=20, t=10, b=10),
            paper_bgcolor="white", plot_bgcolor="white",
            xaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
            yaxis=dict(tickfont=dict(size=11)),
            coloraxis_showscale=False,
            showlegend=False,
        )
        st.plotly_chart(fig3, use_container_width=True)
    st.markdown('<div style="font-size:0.78rem; color:#6b7280; margin-top:-0.5rem;">The routing breakdown above is the clearest proof this system is an agent, not a classifier — different events take different paths through the graph.</div>', unsafe_allow_html=True)

# ── Row 4: Incident History Table ─────────────────────────────────────────────
st.markdown('<div class="section-label">INCIDENT HISTORY</div>', unsafe_allow_html=True)

rows = []
for i, r in enumerate(results):
    rep = r["incident_report"]
    rows.append({
        "idx": i,
        "Attack Type": rep.get("attack_type", "?").replace("_", " ").title(),
        "Severity": rep.get("severity", "?").title(),
        "Confidence": f"{rep.get('confidence_score', 0):.0%}",
        "Source IP": rep.get("source_ip", "?"),
        "Path": _path_label(rep.get("graph_path", [])),
        "Action": rep.get("recommended_action", "?").replace("_", " ").title(),
        "Latency": f"{r.get('latency_s', 0):.1f}s",
    })

table_df = pd.DataFrame(rows).drop(columns=["idx"])

with st.container(border=True):
    selected = st.dataframe(
        table_df,
        use_container_width=True,
        height=360,
        on_select="rerun",
        selection_mode="single-row",
        column_config={
            "Confidence": st.column_config.ProgressColumn("Confidence", min_value=0, max_value=1, format="%s"),
        }
    )

    sel_rows = selected.selection.rows if hasattr(selected, "selection") and selected.selection else []
    if sel_rows:
        idx = sel_rows[0]
        rep = results[idx]["incident_report"]
        with st.expander(f"Full report: {rep.get('attack_type','?').replace('_',' ').title()} — {rep.get('source_ip','')}", expanded=True):
            i1, i2, i3 = st.columns(3)
            with i1:
                st.metric("Severity", rep.get("severity", "?").title())
            with i2:
                st.metric("Confidence", f"{rep.get('confidence_score', 0):.0%}")
            with i3:
                st.metric("Human Review", "Yes" if rep.get("needs_human_review") else "No")
            st.markdown(f"**Reasoning:** {rep.get('reasoning', '')}")
            if rep.get("response_plan"):
                plan = rep["response_plan"]
                st.markdown("**Response Steps:**")
                for step in plan.get("response_steps", []):
                    st.markdown(f"  - {step}")
