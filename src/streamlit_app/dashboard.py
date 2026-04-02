import streamlit as st
import sys
from pathlib import Path

# Fix import path for UI module
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from src.streamlit_app.layout import inject_ui

st.set_page_config(
    page_title="AIR",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Apply global design system
inject_ui()

st.markdown('<div class="page-title">Overview</div>', unsafe_allow_html=True)
st.markdown('<div class="page-subtitle">A multi-agent AI security pipeline. Analyzes raw network logs, classifies threats, and generates containment playbooks in real time.</div>', unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)

with c1:
    st.markdown("""
    <div class="ui-card border-left-blue" style="height: 100%;">
        <div class="ui-card-title">Live Analysis</div>
        <div class="ui-card-value">Real-time</div>
        <div class="ui-card-desc">Paste a raw log or pick a dataset event. Watch the pipeline execute inference and reasoning immediately.</div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown("""
    <div class="ui-card border-left-green" style="height: 100%;">
        <div class="ui-card-title">Dashboard</div>
        <div class="ui-card-value">Batch</div>
        <div class="ui-card-desc">Attack distributions, agent routing decisions, severity breakdown, and incident history on network data.</div>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown("""
    <div class="ui-card border-left-amber" style="height: 100%;">
        <div class="ui-card-title">Eval Results</div>
        <div class="ui-card-value">Metrics</div>
        <div class="ui-card-desc">Accuracy on CICIDS ground truth labels, and behavioral eval scenarios validating model judgment.</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown('<div class="section-header">Agent vs Classifier</div>', unsafe_allow_html=True)

c4, c5 = st.columns(2)

with c4:
    st.markdown("""
    <div class="ui-card border-left-red">
        <div class="ui-card-title">Predictive Classifier</div>
        <div class="ui-card-desc" style="font-size: 0.95rem; line-height: 1.6; color: #334155;">
            Takes an input sequence and returns a categorical label. Operations are deterministic. There is no branching logic, no confidence thresholds, and no subsequent agentic actions taken based on reasoning.
        </div>
    </div>
    """, unsafe_allow_html=True)

with c5:
    st.markdown("""
    <div class="ui-card border-left-green">
        <div class="ui-card-title">AIR System</div>
        <div class="ui-card-desc" style="font-size: 0.95rem; line-height: 1.6; color: #334155;">
            A Triage Agent classifies the event and infers a confidence score. A Policy Router inspects this state and dynamically dictates execution flow. If thresholds are met, a distinct Response Agent formulates a playbook. Edge cases are routed back for Human Review.
        </div>
    </div>
    """, unsafe_allow_html=True)
