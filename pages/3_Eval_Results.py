"""Page 3: Eval Results — behavioral evals + CICIDS accuracy."""

import json
from pathlib import Path

import streamlit as st

BATCH_PATH = Path("data/results/batch_results.json")
EVAL_PATH  = Path("data/results/eval_results.json")

SEV_DOT = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢", "info": "🔵"}


@st.cache_data
def _load(p: Path) -> dict:
    return json.loads(p.read_text())


st.markdown('<div class="sec-label" style="margin-top:0;">EVAL RESULTS</div>', unsafe_allow_html=True)
st.markdown('<div class="page-header"><h1>Evaluation & Accuracy</h1><p>Ground truth accuracy on real network data + behavioral judgment tests on hand-crafted scenarios</p></div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# Section A — CICIDS Accuracy
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("---")
st.markdown("""
<div style="display:flex; align-items:center; gap:10px; margin-bottom:0.5rem;">
    <div style="width:4px; height:24px; background:#3b82f6; border-radius:2px;"></div>
    <div style="font-size:1.1rem; font-weight:700; color:#111827;">Dataset Evaluation — CICIDS 2017</div>
</div>
<p style="color:#6b7280; font-size:0.84rem; margin-bottom:1rem;">Ground truth labels vs agent classifications on {n} real network flow records</p>
""".replace("{n}", str(0)), unsafe_allow_html=True)

if not BATCH_PATH.exists():
    st.markdown("""
    <div class="card card-accent-amber">
        <div style="font-weight:700; color:#b45309; margin-bottom:6px;">⚠ No dataset results yet</div>
        <div style="font-size:0.82rem; color:#6b7280; line-height:1.6;">
            Run: <code>python src/data/batch_runner.py</code><br>
            (FastAPI must be running: <code>python run.py</code>)
        </div>
    </div>""", unsafe_allow_html=True)
else:
    batch   = _load(BATCH_PATH)
    results = batch.get("results", [])
    total   = batch.get("total", len(results))
    correct = batch.get("correct", 0)
    wrong   = total - correct
    acc     = batch.get("accuracy_pct", 0.0)
    lat     = batch.get("avg_latency_s", 0.0)

    # Top metrics with semantic colors
    m1, m2, m3, m4 = st.columns(4)
    for col, val, lbl, cls, icon in [
        (m1, f"{acc}%",   "Accuracy",        "metric-green", "🎯"),
        (m2, str(correct),"Correct",          "metric-green", "✅"),
        (m3, str(wrong),  "Incorrect",        "metric-red",   "❌"),
        (m4, f"{lat}s",   "Avg Latency",      "metric-blue",  "⏱"),
    ]:
        with col:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">{icon} {lbl}</div>
                <div class="metric-val {cls}">{val}</div>
            </div>""", unsafe_allow_html=True)

    # Accuracy bar
    st.markdown(f"""
    <div class="card" style="margin-top:1rem;">
        <div style="display:flex; justify-content:space-between; margin-bottom:8px;">
            <div style="font-size:0.82rem; font-weight:600; color:#374151;">Overall Accuracy</div>
            <div style="font-size:0.82rem; font-weight:700; color:{'#10b981' if acc>=70 else '#f59e0b' if acc>=50 else '#ef4444'};">{acc}%</div>
        </div>
        <div style="height:10px; background:#f3f4f6; border-radius:9999px; overflow:hidden;">
            <div style="height:10px; width:{acc}%; background:{'#10b981' if acc>=70 else '#f59e0b' if acc>=50 else '#ef4444'}; border-radius:9999px; transition:width 0.5s;"></div>
        </div>
        <div style="display:flex; justify-content:space-between; margin-top:6px;">
            <div style="font-size:0.7rem; color:#9ca3af;">{correct} correct out of {total}</div>
            <div style="font-size:0.7rem; color:#9ca3af;">Avg {lat}s per event</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Confusion breakdown
    st.markdown('<div class="sec-label">PREDICTION BREAKDOWN</div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="font-size:0.75rem; color:#9ca3af; margin-bottom:0.75rem;">
        🟢 Green = agent matched ground truth · 🔴 Red = mismatch (may reflect ambiguous logs, not model failure)
    </div>""", unsafe_allow_html=True)

    with st.container(border=True):
        for r in results:
            gt   = r.get("ground_truth", "?").replace("_", " ").title()
            pred = r["incident_report"].get("attack_type", "?").replace("_", " ").title()
            conf = r["incident_report"].get("confidence_score", 0)
            match = r.get("match", False)
            icon = "✅" if match else "❌"
            cls  = "conf-row match" if match else "conf-row nomatch"
            sev  = r["incident_report"].get("severity", "info")
            dot  = SEV_DOT.get(sev, "⚪")

            st.markdown(f"""
            <div class="{cls}">
                <div class="conf-row-icon">{icon}</div>
                <div class="conf-row-truth">Expected: <strong>{gt}</strong> {dot}</div>
                <div class="conf-row-predict">Got: <strong>{pred}</strong></div>
                <div class="conf-row-conf">{conf:.0%}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("""
    <div style="font-size:0.75rem; color:#9ca3af; margin-top:0.75rem; line-height:1.6;">
        Accuracy = agent's <code>attack_type</code> matched the dataset's ground truth label.
        Mismatches may reflect overlapping signatures — e.g., bot traffic resembling normal flows.
    </div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# Section B — Behavioral Evals
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("---")
st.markdown("""
<div style="display:flex; align-items:center; gap:10px; margin-bottom:0.5rem;">
    <div style="width:4px; height:24px; background:#10b981; border-radius:2px;"></div>
    <div style="font-size:1.1rem; font-weight:700; color:#111827;">Behavioral Evals — Agent Judgment Tests</div>
</div>
<p style="color:#6b7280; font-size:0.84rem; margin-bottom:1rem;">8 hand-crafted attack scenarios testing attack_type and severity classification against known expected outputs</p>
""", unsafe_allow_html=True)

if not EVAL_PATH.exists():
    st.markdown("""
    <div class="card card-accent-amber">
        <div style="font-weight:700; color:#b45309; margin-bottom:6px;">⚠ Eval results not found</div>
        <div style="font-size:0.82rem; color:#6b7280; line-height:1.6;">
            Run: <code>python tests/test_evals.py</code>
        </div>
    </div>""", unsafe_allow_html=True)
else:
    evals   = _load(EVAL_PATH)
    cases   = evals.get("cases", [])
    e_total = evals.get("total", len(cases))
    e_pass  = evals.get("correct", 0)
    e_fail  = e_total - e_pass
    e_acc   = evals.get("accuracy_pct", 0.0)
    e_conf  = evals.get("avg_confidence", 0.0)
    e_lat   = evals.get("avg_latency_s", 0.0)

    # Summary
    e1, e2, e3, e4 = st.columns(4)
    for col, val, lbl, cls, icon in [
        (e1, f"{e_pass}/{e_total}", "Passed",        "metric-green", "✅"),
        (e2, str(e_fail),           "Failed",         "metric-red",   "❌"),
        (e3, f"{e_conf:.0%}",       "Avg Confidence", "metric-blue",  "🎯"),
        (e4, f"{e_lat:.1f}s",        "Avg Latency",    "metric-amber", "⏱"),
    ]:
        with col:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">{icon} {lbl}</div>
                <div class="metric-val {cls}">{val}</div>
            </div>""", unsafe_allow_html=True)

    # Pass/fail banner
    if e_fail == 0:
        st.markdown('<div class="banner banner-green" style="margin-top:0.75rem;"><div class="banner-icon">🎉</div><div><strong>All evals passed</strong> — Agent judgment is calibrated correctly across all 8 attack types.</div></div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="banner banner-amber" style="margin-top:0.75rem;"><div class="banner-icon">⚠</div><div><strong>{e_fail} eval(s) failed</strong> — Review the cases below to understand model behavior on edge cases.</div></div>', unsafe_allow_html=True)

    st.markdown('<div class="sec-label">CASE RESULTS</div>', unsafe_allow_html=True)

    for case in cases:
        passed  = case.get("passed", False)
        cls     = "eval-card pass" if passed else "eval-card fail"
        icon    = "✅" if passed else "❌"
        name    = case.get("name", "")
        exp_at  = case.get("expected_attack_type", "").replace("_", " ").title()
        got_at  = case.get("actual_attack_type", "").replace("_", " ").title()
        exp_sev = case.get("expected_severity", "")
        got_sev = case.get("actual_severity", "")
        conf    = case.get("confidence", 0)
        lat     = case.get("latency_s", 0)
        snippet = case.get("log_snippet", "")

        got_color  = "#15803d" if passed else "#dc2626"
        got_icon   = SEV_DOT.get(got_sev, "⚪")
        exp_icon   = SEV_DOT.get(exp_sev, "⚪")

        st.markdown(f"""
        <div class="{cls}">
            <div style="flex-shrink:0; font-size:1.3rem;">{icon}</div>
            <div style="flex:1; min-width:0;">
                <div style="font-size:0.88rem; font-weight:700; color:#111827; margin-bottom:4px;">{name}</div>
                <div style="font-family:'JetBrains Mono',monospace; font-size:0.68rem; color:#9ca3af; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">{snippet}</div>
            </div>
            <div style="flex-shrink:0; text-align:right; min-width:130px;">
                <div style="font-size:0.72rem; color:#9ca3af;">Expected</div>
                <div style="font-size:0.8rem; font-weight:600; color:#374151;">{exp_at} {exp_icon}</div>
            </div>
            <div style="flex-shrink:0; text-align:right; min-width:130px;">
                <div style="font-size:0.72rem; color:#9ca3af;">Got</div>
                <div style="font-size:0.8rem; font-weight:700; color:{got_color};">{got_at} {got_icon}</div>
            </div>
            <div style="flex-shrink:0; text-align:right; min-width:80px;">
                <div style="font-size:0.72rem; color:#9ca3af;">Conf · Latency</div>
                <div style="font-size:0.78rem; color:#6b7280;">{conf:.0%} · {lat:.1f}s</div>
            </div>
        </div>""", unsafe_allow_html=True)

    st.markdown("""
    <div style="font-size:0.75rem; color:#9ca3af; margin-top:0.75rem; line-height:1.6;">
        Behavioral evals test the LLM's judgment, not code logic. A "FAIL" means the model disagreed with the
        hand-labeled expected output — this is a signal for prompt tuning, not a bug.
    </div>""", unsafe_allow_html=True)
