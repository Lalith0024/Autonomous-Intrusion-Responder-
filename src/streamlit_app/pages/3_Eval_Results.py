"""AIR V2 — Benchmarking & Evaluation.

V1 comparison, behavioral reasoning suite, and V2 red-team adversarial metrics.
High-contrast light-mode report for compliance and auditing.
"""

import json
from pathlib import Path
import streamlit as st

from src.core.config import settings
from src.streamlit_app.layout import inject_ui

st.set_page_config(page_title="AIR — Benchmarking", layout="wide", initial_sidebar_state="expanded")
inject_ui()

BATCH_PATH = Path(settings.BATCH_RESULTS_PATH)
EVAL_PATH  = Path(settings.EVAL_RESULTS_PATH)
EVAL_V2_PATH = Path(settings.EVAL_RESULTS_PATH).with_name("eval_results_v2.json")

LIGHT_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#475569", family="Inter"),
    showlegend=False,
)

@st.cache_data
def _load_json(p: Path) -> dict:
    return json.loads(p.read_text())

st.markdown('<div class="page-title">🧪 Benchmarking</div>', unsafe_allow_html=True)
st.markdown('<div class="page-subtitle">Rigorous testing against ground-truth datasets and adversarial payloads. Quantitative metrics for model reliability and defensive reasoning.</div>', unsafe_allow_html=True)

# ── Dataset Evaluation ──
st.markdown('<div class="section-header">Ground Truth Accuracy — CICIDS 2017</div>', unsafe_allow_html=True)

if not BATCH_PATH.exists():
    st.markdown('''<div class="alert alert-amber"><strong>PENDING:</strong> Run <code class="mono">python src/data/batch_runner.py</code> to generate metrics.</div>''', unsafe_allow_html=True)
else:
    batch = _load_json(BATCH_PATH)
    results = batch.get("results", [])
    acc = batch.get("accuracy_pct", 0.0)
    lat = batch.get("avg_latency_s", 0.0)

    m1, m2, m3 = st.columns(3)
    m1.markdown(f'<div class="ui-card border-left-blue"><div class="ui-card-title">Detection Accuracy</div><div class="ui-card-value" style="color:#2563eb;">{acc}%</div></div>', unsafe_allow_html=True)
    m2.markdown(f'<div class="ui-card border-left-green"><div class="ui-card-title">Correct Patterns</div><div class="ui-card-value" style="color:#16a34a;">{batch.get("correct", 0)}</div></div>', unsafe_allow_html=True)
    m3.markdown(f'<div class="ui-card border-left-slate"><div class="ui-card-title">Mean Latency</div><div class="ui-card-value" style="color:#475569;">{lat}s</div></div>', unsafe_allow_html=True)

    st.markdown('<div class="ui-card-title" style="margin-top:2rem;">Ground Truth Classification Matrix</div>', unsafe_allow_html=True)
    st.markdown('<div class="ui-card" style="padding:1rem;">', unsafe_allow_html=True)
    for r in results[:20]: # Limit for performance
        gt = r.get("ground_truth", "?").title()
        pred = r["incident_report"].get("attack_type", "?").title()
        match = r.get("match", False)
        col = "#16a34a" if match else "#dc2626"
        st.markdown(f'''
        <div style="display:flex; align-items:center; gap:1.5rem; padding:0.75rem 0; border-bottom:1px solid #f1f5f9;">
            <div style="flex:1;"><span style="font-size:0.65rem; color:#94a3b8; font-weight:800; text-transform:uppercase;">Expected</span><br><b style="color:#1e293b; font-size:0.9rem;">{gt}</b></div>
            <div style="flex:1;"><span style="font-size:0.65rem; color:#94a3b8; font-weight:800; text-transform:uppercase;">Inferred</span><br><b style="color:{col}; font-size:0.9rem;">{pred}</b></div>
            <div style="width:100px; text-align:right;"><span style="font-size:0.6rem; font-weight:800; color:{col}; background:#f1f5f9; padding:0.25rem 0.5rem; border-radius:4px;">{"MATCH" if match else "MISMATCH"}</span></div>
        </div>''', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ── Behavioral Reasoning ──
st.markdown('<div class="section-header">Behavioral Reasoning Suite</div>', unsafe_allow_html=True)

if not EVAL_PATH.exists():
    st.markdown('''<div class="alert alert-amber"><strong>PENDING:</strong> Behavioral suite not yet executed.</div>''', unsafe_allow_html=True)
else:
    evals = _load_json(EVAL_PATH)
    cases = evals.get("cases", [])
    
    e1, e2 = st.columns(2)
    e1.markdown(f'<div class="ui-card border-left-green"><div class="ui-card-title">Reasoning Pass Rate</div><div class="ui-card-value" style="color:#16a34a;">{evals.get("correct", 0)}/{evals.get("total", len(cases))}</div></div>', unsafe_allow_html=True)
    e2.markdown(f'<div class="ui-card border-left-blue"><div class="ui-card-title">Avg Confidence</div><div class="ui-card-value" style="color:#2563eb;">{(sum(c.get("confidence",0) for c in cases)/len(cases) if cases else 0):.0%}</div></div>', unsafe_allow_html=True)

    for case in cases:
        passed = case.get("passed", False)
        col = "#16a34a" if passed else "#dc2626"
        st.markdown(f'''
        <div class="ui-card" style="border-left: 4px solid {col};">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1rem;">
                <div style="font-weight:800; font-size:1rem; color:#1e293b;">{case.get("name","")}</div>
                <span class="badge" style="background:{col}20; color:{col};">{ "PASS" if passed else "FAIL" }</span>
            </div>
            <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:8px; padding:0.85rem; font-family:JetBrains Mono,monospace; color:#475569; font-size:0.75rem; margin-bottom:1rem;">
                {case.get("log_snippet","")}
            </div>
            <div style="display:flex; gap:3rem;">
                <div><div class="ui-card-title">Expected</div><div style="font-weight:700; color:#1e293b;">{case.get("expected_attack_type","").title()}</div></div>
                <div><div class="ui-card-title">Agent Logic</div><div style="font-weight:700; color:{col};">{case.get("actual_attack_type","").title()}</div></div>
            </div>
        </div>''', unsafe_allow_html=True)

# ── Red Team ──
if EVAL_V2_PATH.exists():
    st.markdown('<div class="section-header">🛡️ V2 Red Team Adversarial Benchmarking</div>', unsafe_allow_html=True)
    v2 = _load_json(EVAL_V2_PATH)
    categories = v2.get("category_breakdown", {})

    r1, r2 = st.columns([1, 2])
    with r1:
        st.markdown(f'''
        <div class="ui-card border-left-slate">
            <div class="ui-card-title">Overall Score</div>
            <div class="ui-card-value" style="color:#0f172a;">{v2.get("accuracy_pct", 0)}%</div>
            <div class="ui-card-desc">Defeated {v2.get("correct", 0)} out of {v2.get("total", 0)} targeted attacks.</div>
        </div>''', unsafe_allow_html=True)
    
    with r2:
        st.markdown('<div class="ui-card">', unsafe_allow_html=True)
        st.markdown('<div class="ui-card-title">Category breakdown</div>', unsafe_allow_html=True)
        cat_colors = {"standard": "#2563eb", "adversarial": "#ea580c", "false_positive": "#16a34a", "multi_stage": "#7c3aed", "edge_case": "#64748b"}
        for cat, stats in sorted(categories.items()):
            acc = stats.get("accuracy_pct", 0)
            color = cat_colors.get(cat, "#475569")
            st.markdown(f'''
            <div style="margin-bottom:1rem;">
                <div style="display:flex; justify-content:space-between; font-size:0.75rem; font-weight:800; color:{color}; text-transform:uppercase; margin-bottom:0.4rem;">
                    <span>{cat}</span>
                    <span>{acc}%</span>
                </div>
                <div style="height:6px; background:#f1f5f9; border-radius:3px;">
                    <div style="width:{acc}%; height:100%; background:{color}; border-radius:3px;"></div>
                </div>
            </div>''', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
