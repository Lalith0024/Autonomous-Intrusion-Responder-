import json
from pathlib import Path
import streamlit as st
import sys

# Fix import path for UI module
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from src.streamlit_app.layout import inject_ui

st.set_page_config(page_title="AIR - Evaluation", layout="wide", initial_sidebar_state="expanded")
inject_ui()

BATCH_PATH = Path("data/results/batch_results.json")
EVAL_PATH  = Path("data/results/eval_results.json")

@st.cache_data
def _load(p: Path) -> dict:
    return json.loads(p.read_text())

st.markdown('<div class="page-title">Evaluation Metrics</div>', unsafe_allow_html=True)
st.markdown('<div class="page-subtitle">Ground truth accuracy on historically curated network datasets coupled with active behavioral judgment scenarios.</div>', unsafe_allow_html=True)

# ── Dataset Evaluation ──
st.markdown('<div class="section-header">Empirical Dataset Evaluation &mdash; CICIDS 2017</div>', unsafe_allow_html=True)

if not BATCH_PATH.exists():
    st.markdown("""
    <div class="alert alert-amber" style="max-width: 600px;">
        <strong>Dataset execution pending:</strong><br><br>
        <code class="mono">python src/data/batch_runner.py</code>
    </div>""", unsafe_allow_html=True)
else:
    batch   = _load(BATCH_PATH)
    results = batch.get("results", [])
    total   = batch.get("total", len(results))
    correct = batch.get("correct", 0)
    wrong   = total - correct
    acc     = batch.get("accuracy_pct", 0.0)
    lat     = batch.get("avg_latency_s", 0.0)

    m1, m2, m3, m4 = st.columns(4)
    m1.markdown(f'<div class="ui-card border-left-blue"><div class="ui-card-title">Overall Accuracy</div><div class="ui-card-value text-blue">{acc}%</div></div>', unsafe_allow_html=True)
    m2.markdown(f'<div class="ui-card border-left-green"><div class="ui-card-title">Correct Inferences</div><div class="ui-card-value text-green">{correct}</div></div>', unsafe_allow_html=True)
    m3.markdown(f'<div class="ui-card border-left-red"><div class="ui-card-title">Misclassifications</div><div class="ui-card-value text-red">{wrong}</div></div>', unsafe_allow_html=True)
    m4.markdown(f'<div class="ui-card border-left-slate"><div class="ui-card-title">Mean Latency</div><div class="ui-card-value">{lat}s</div></div>', unsafe_allow_html=True)

    st.markdown('<div class="ui-card-title" style="margin-top:2rem;">Ground Truth Matrix</div>', unsafe_allow_html=True)
    st.markdown('<div style="font-size:0.8rem; color:#64748b; margin-bottom:1rem;">Match validity is determined strictly against the labeled CICIDS payload.</div>', unsafe_allow_html=True)

    with st.container():
        st.markdown('<div class="ui-card" style="padding:1rem;">', unsafe_allow_html=True)
        for r in results:
            gt   = r.get("ground_truth", "?").replace("_", " ").title()
            pred = r["incident_report"].get("attack_type", "?").replace("_", " ").title()
            conf = r["incident_report"].get("confidence_score", 0)
            match = r.get("match", False)
            
            badge_class = "badge-match" if match else "badge-nomatch"
            badge_text = "VALID" if match else "INVALID"

            st.markdown(f"""
            <div style="display:flex; align-items:center; gap:1.5rem; padding:0.75rem 0; border-bottom:1px solid #f1f5f9;">
                <div style="width:100px;"><span class="badge {badge_class}">{badge_text}</span></div>
                <div style="flex:1;"><span style="font-size:0.75rem; color:#64748b; text-transform:uppercase; letter-spacing:0.05em; display:block; margin-bottom:0.25rem;">Expected</span><span style="font-size:0.9rem; font-weight:600; color:#0f172a;">{gt}</span></div>
                <div style="flex:1;"><span style="font-size:0.75rem; color:#64748b; text-transform:uppercase; letter-spacing:0.05em; display:block; margin-bottom:0.25rem;">Inferred</span><span style="font-size:0.9rem; font-weight:600; color:#0f172a;">{pred}</span></div>
                <div style="width:100px; text-align:right;"><span style="font-size:0.75rem; color:#64748b; text-transform:uppercase; letter-spacing:0.05em; display:block; margin-bottom:0.25rem;">Confidence</span><span style="font-size:0.9rem; font-weight:700; color:#334155;">{conf:.0%}</span></div>
            </div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)


# ── Behavioral Evaluation ──
st.markdown('<div class="section-header">Behavioral Reasoning Suites</div>', unsafe_allow_html=True)

if not EVAL_PATH.exists():
    st.markdown("""
    <div class="alert alert-amber" style="max-width: 600px;">
        <strong>Evaluation execution pending:</strong><br><br>
        <code class="mono">python tests/test_evals.py</code>
    </div>""", unsafe_allow_html=True)
else:
    evals   = _load(EVAL_PATH)
    cases   = evals.get("cases", [])
    e_total = evals.get("total", len(cases))
    e_pass  = evals.get("correct", 0)
    e_fail  = e_total - e_pass
    e_lat   = evals.get("avg_latency_s", 0.0)

    e1, e2, e3 = st.columns(3)
    e1.markdown(f'<div class="ui-card border-left-green"><div class="ui-card-title">Test Matrix Passed</div><div class="ui-card-value text-green">{e_pass}/{e_total}</div></div>', unsafe_allow_html=True)
    e2.markdown(f'<div class="ui-card border-left-red"><div class="ui-card-title">Test Matrix Failed</div><div class="ui-card-value text-red">{e_fail}</div></div>', unsafe_allow_html=True)
    e3.markdown(f'<div class="ui-card border-left-slate"><div class="ui-card-title">Execution Latency</div><div class="ui-card-value text-slate">{e_lat}s</div></div>', unsafe_allow_html=True)

    if e_fail == 0:
        st.markdown('<div class="alert alert-info" style="margin-bottom: 2rem;"><strong>Matrix Complete</strong> &mdash; Agent reasoning operates uniformly against all expected boundaries.</div>', unsafe_allow_html=True)

    st.markdown('<div class="ui-card-title">Execution Trace Logs</div>', unsafe_allow_html=True)
    
    for case in cases:
        passed  = case.get("passed", False)
        accent_cls = "border-left-green" if passed else "border-left-red"
        status_txt = "PASS" if passed else "FAIL"
        status_col = "#22c55e" if passed else "#ef4444"
        
        name    = case.get("name", "")
        exp_at  = case.get("expected_attack_type", "").replace("_", " ").title()
        got_at  = case.get("actual_attack_type", "").replace("_", " ").title()
        conf    = case.get("confidence", 0)
        snippet = case.get("log_snippet", "")

        st.markdown(f"""
        <div class="ui-card {accent_cls}" style="margin-bottom:1rem; padding:1.25rem;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1rem;">
                <div style="font-size:1.1rem; font-weight:800; color:#0f172a;">{name}</div>
                <div style="font-size:0.85rem; font-weight:800; color:{status_col}; border:1px solid {status_col}; padding:0.25rem 0.75rem; border-radius:4px;">{status_txt}</div>
            </div>
            
            <div class="mono" style="background:#f8fafc; padding:0.75rem; border-radius:6px; border:1px solid #e2e8f0; color:#475569; margin-bottom:1.5rem;">{snippet}</div>
            
            <div style="display:flex; gap:3rem;">
                <div>
                    <div style="font-size:0.75rem; color:#64748b; text-transform:uppercase; letter-spacing:0.05em; margin-bottom:0.25rem;">Expected Designation</div>
                    <div style="font-size:0.95rem; font-weight:600; color:#0f172a;">{exp_at}</div>
                </div>
                <div>
                    <div style="font-size:0.75rem; color:#64748b; text-transform:uppercase; letter-spacing:0.05em; margin-bottom:0.25rem;">Inferred Designation</div>
                    <div style="font-size:0.95rem; font-weight:600; color:{status_col};">{got_at}</div>
                </div>
                <div>
                    <div style="font-size:0.75rem; color:#64748b; text-transform:uppercase; letter-spacing:0.05em; margin-bottom:0.25rem;">Confidence Metric</div>
                    <div style="font-size:0.95rem; font-weight:700; color:#334155;">{conf:.0%}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
