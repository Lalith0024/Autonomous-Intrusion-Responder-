"""Page 3: Eval Results — CICIDS accuracy + behavioral eval suite results."""

import json
from pathlib import Path

import pandas as pd
import streamlit as st

BATCH_PATH = Path("data/results/batch_results.json")
EVAL_PATH = Path("data/results/eval_results.json")


@st.cache_data
def load_json(path: Path) -> dict:
    return json.loads(path.read_text())


st.markdown('<div class="section-label" style="margin-top:0;">EVALUATION</div>', unsafe_allow_html=True)
st.markdown("# Eval Results")

# ══════════════════════════════════════════════════════════════════════════════
# Section A — CICIDS Dataset Accuracy
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("## Dataset Evaluation — CICIDS 2017")
st.markdown('<p style="color:#6b7280; margin-bottom:1rem;">Ground truth labels vs agent classifications on real network data</p>', unsafe_allow_html=True)

if not BATCH_PATH.exists():
    with st.container(border=True):
        st.markdown("""
        <div style="padding:1rem;">
            <div style="font-weight:600; color:#1a1a1a; margin-bottom:0.4rem;">No dataset results yet</div>
            <div style="color:#6b7280; font-size:0.88rem;">
                Run the batch analyzer to generate this report:<br>
                <code>python src/data/batch_runner.py</code><br><br>
                Make sure FastAPI is running: <code>python run.py</code>
            </div>
        </div>""", unsafe_allow_html=True)
else:
    batch = load_json(BATCH_PATH)
    results = batch.get("results", [])
    total = batch.get("total", len(results))
    correct = batch.get("correct", 0)
    accuracy = batch.get("accuracy_pct", 0.0)
    avg_lat = batch.get("avg_latency_s", 0.0)

    # Top metrics
    m1, m2, m3, m4 = st.columns(4)
    for col, val, lbl in [
        (m1, f"{accuracy}%", "Overall Accuracy"),
        (m2, str(correct), "Correct"),
        (m3, str(total - correct), "Incorrect"),
        (m4, f"{avg_lat}s", "Avg Latency"),
    ]:
        with col:
            with st.container(border=True):
                st.markdown(f'<div class="stat-val">{val}</div><div class="stat-lbl">{lbl}</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-label">CONFUSION BREAKDOWN</div>', unsafe_allow_html=True)

    rows = []
    for r in results:
        rows.append({
            "Ground Truth": r.get("ground_truth", "?").replace("_", " ").title(),
            "Agent Predicted": r["incident_report"].get("attack_type", "?").replace("_", " ").title(),
            "Match": r.get("match", False),
            "Confidence": r["incident_report"].get("confidence_score", 0),
        })

    df = pd.DataFrame(rows)

    with st.container(border=True):
        for _, row in df.iterrows():
            match = row["Match"]
            bg = "#f0fdf4" if match else "#fef2f2"
            icon = "✓" if match else "✗"
            icon_color = "#16a34a" if match else "#dc2626"

            st.markdown(f"""
            <div style="display:flex; align-items:center; gap:16px; padding:8px 12px; 
                        background:{bg}; border-radius:6px; margin-bottom:4px; font-size:0.85rem;">
                <span style="color:{icon_color}; font-weight:700; width:16px;">{icon}</span>
                <span style="flex:1; color:#374151;">Expected: <b>{row['Ground Truth']}</b></span>
                <span style="flex:1; color:#374151;">Got: <b>{row['Agent Predicted']}</b></span>
                <span style="width:80px; color:#6b7280;">{row['Confidence']:.0%}</span>
            </div>""", unsafe_allow_html=True)

    st.markdown("""
    <div style="margin-top:1rem; padding:10px 14px; background:#f8f9fa; border:1px solid #e5e7eb; border-radius:8px;">
        <div style="font-size:0.8rem; color:#6b7280; line-height:1.6;">
            Accuracy measures whether the agent's attack_type matched the dataset's ground truth label.
            Mismatches may reflect ambiguous log entries or overlapping attack signatures — not necessarily model failures.
        </div>
    </div>""", unsafe_allow_html=True)

st.divider()

# ══════════════════════════════════════════════════════════════════════════════
# Section B — Behavioral Evals
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("## Behavioral Evals — Agent Judgment Tests")
st.markdown('<p style="color:#6b7280; margin-bottom:1rem;">8 hand-crafted test cases validating agent reasoning across attack types</p>', unsafe_allow_html=True)

if not EVAL_PATH.exists():
    with st.container(border=True):
        st.markdown("""
        <div style="padding:1rem;">
            <div style="font-weight:600; color:#1a1a1a; margin-bottom:0.4rem;">Eval results not found</div>
            <div style="color:#6b7280; font-size:0.88rem;">
                Run the eval suite to generate results:<br>
                <code>python tests/test_evals.py</code>
            </div>
        </div>""", unsafe_allow_html=True)
else:
    evals = load_json(EVAL_PATH)
    cases = evals.get("cases", [])
    e_total = evals.get("total", len(cases))
    e_correct = evals.get("correct", 0)
    e_acc = evals.get("accuracy_pct", 0.0)
    e_conf = evals.get("avg_confidence", 0.0)
    e_lat = evals.get("avg_latency_s", 0.0)

    e1, e2, e3 = st.columns(3)
    for col, val, lbl in [
        (e1, f"{e_correct}/{e_total}", "Passed"),
        (e2, f"{e_conf:.0%}", "Avg Confidence"),
        (e3, f"{e_lat:.1f}s", "Avg Latency"),
    ]:
        with col:
            with st.container(border=True):
                st.markdown(f'<div class="stat-val">{val}</div><div class="stat-lbl">{lbl}</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-label">CASE RESULTS</div>', unsafe_allow_html=True)

    for case in cases:
        passed = case.get("passed", False)
        bg = "#f0fdf4" if passed else "#fef2f2"
        border_color = "#bbf7d0" if passed else "#fecaca"
        icon = "✓" if passed else "✗"
        icon_color = "#16a34a" if passed else "#dc2626"

        with st.container(border=True):
            c1, c2, c3, c4 = st.columns([3, 2, 2, 1])
            with c1:
                st.markdown(f'<div style="font-weight:600; color:#1a1a1a; font-size:0.88rem;">{case["name"]}</div>', unsafe_allow_html=True)
                st.markdown(f'<div style="font-size:0.75rem; color:#9ca3af; font-family:monospace; margin-top:2px;">{case.get("log_snippet","")}</div>', unsafe_allow_html=True)
            with c2:
                st.markdown(f'<div class="stat-lbl">Expected</div><div style="font-size:0.85rem; font-weight:600;">{case.get("expected_attack_type","").replace("_"," ").title()}</div>', unsafe_allow_html=True)
            with c3:
                actual = case.get("actual_attack_type", "").replace("_", " ").title()
                color = "#16a34a" if passed else "#dc2626"
                st.markdown(f'<div class="stat-lbl">Got</div><div style="font-size:0.85rem; font-weight:600; color:{color};">{actual}</div>', unsafe_allow_html=True)
            with c4:
                st.markdown(f'<div style="font-size:1.2rem; font-weight:700; color:{icon_color}; text-align:center; margin-top:0.5rem;">{icon}</div>', unsafe_allow_html=True)
