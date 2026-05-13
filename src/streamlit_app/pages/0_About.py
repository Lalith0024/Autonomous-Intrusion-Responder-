import streamlit as st
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from src.streamlit_app.layout import inject_ui

st.set_page_config(page_title="AIR — About", layout="wide", initial_sidebar_state="expanded")
inject_ui()

# ── Main Content ──
st.markdown('<div class="page-title">About Autonomous Intrusion Responder (AIR)</div>', unsafe_allow_html=True)
st.markdown('<div class="page-subtitle">An end-to-end, multi-agent AI pipeline for network security, threat classification, and automated response. This project reimagines the modern Security Operations Center (SOC) by introducing fully autonomous, intelligent agents.</div>', unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs(["🚀 Project Overview", "🧠 Agentic Architecture", "🛤️ LangGraph Workflow", "📊 Data Ecosystem"])

with tab1:
    st.markdown('<div class="section-header">The Paradigm Shift in SOC Operations</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('''
        <div class="ui-card border-left-slate">
            <div class="ui-card-title">Traditional Security Operations</div>
            <div style="font-size:0.95rem; line-height:1.8; color:#334155;">
                <ul style="margin-bottom: 0;">
                    <li style="margin-bottom: 0.5rem;"><strong>Reactive:</strong> Rule-based systems trigger massive alert fatigue.</li>
                    <li style="margin-bottom: 0.5rem;"><strong>Manual Triage:</strong> Analysts spend hours investigating IPs and cross-referencing threat feeds.</li>
                    <li style="margin-bottom: 0.5rem;"><strong>Siloed Tools:</strong> Dashboards, threat intel, and firewalls are disjointed.</li>
                    <li><strong>Stateless:</strong> Each alert is treated in isolation without historical context.</li>
                </ul>
            </div>
        </div>
        ''', unsafe_allow_html=True)
    with c2:
        st.markdown('''
        <div class="ui-card border-left-blue">
            <div class="ui-card-title">AIR Security Agent</div>
            <div style="font-size:0.95rem; line-height:1.8; color:#334155;">
                <ul style="margin-bottom: 0;">
                    <li style="margin-bottom: 0.5rem;"><strong>Proactive:</strong> Automatically investigates IPs, scans ports, and queries threat intel.</li>
                    <li style="margin-bottom: 0.5rem;"><strong>Intelligent Triage:</strong> LLMs analyze the complete context to classify threats.</li>
                    <li style="margin-bottom: 0.5rem;"><strong>Automated Response:</strong> High-confidence threats trigger autonomous playbook generation and IP blocking.</li>
                    <li><strong>Vector Memory:</strong> FAISS-backed memory recalls similar past attacks for cross-event correlation.</li>
                </ul>
            </div>
        </div>
        ''', unsafe_allow_html=True)

with tab2:
    st.markdown('<div class="section-header">The Agentic AI View</div>', unsafe_allow_html=True)
    st.markdown('<div style="font-size:1.05rem; color:#475569; margin-bottom: 2rem; max-width: 900px;">AIR relies on specialized LLM-powered agents that operate within a structured workflow. They don\'t just generate text; they make decisions and execute tools to defend the network autonomously.</div>', unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('''
        <div class="ui-card border-left-amber" style="height: 100%;">
            <div class="ui-card-title">🧠 Triage Agent</div>
            <div style="font-size:0.95rem; line-height:1.8; color:#334155; margin-bottom: 1.5rem;">
                <strong>Role:</strong> First responder. Classifies incoming raw log events into structured incident reports.<br><br>
                <strong>Context Injected:</strong> 
                <ul style="margin-top: 0.5rem; margin-bottom: 1rem;">
                    <li>Raw network flow logs (CICIDS)</li>
                    <li>GeoIP & Abuse IP data</li>
                    <li>Active port scan results</li>
                    <li>Historical matches from Vector Memory</li>
                </ul>
                <strong>Output:</strong> Attack Type, Severity, Confidence Score, and Indicators.
            </div>
            <span class="badge badge-tool">LLaMA 3.3 70B</span>
        </div>
        ''', unsafe_allow_html=True)

    with c2:
        st.markdown('''
        <div class="ui-card border-left-red" style="height: 100%;">
            <div class="ui-card-title">⚔️ Response Agent</div>
            <div style="font-size:0.95rem; line-height:1.8; color:#334155; margin-bottom: 1.5rem;">
                <strong>Role:</strong> Mitigation expert. Generates step-by-step containment playbooks and executes defense actions.<br><br>
                <strong>Trigger:</strong> Only invoked if the Triage Agent yields a High/Critical severity with High Confidence (≥ 70%).<br><br>
                <strong>Capabilities:</strong> 
                <ul style="margin-top: 0.5rem; margin-bottom: 1rem;">
                    <li>Drafts actionable SOC playbooks.</li>
                    <li>Invokes the <span style="font-family: monospace; background: #fee2e2; padding: 2px 4px; border-radius: 4px; color: #991b1b;">block_ip()</span> tool autonomously.</li>
                    <li>Determines if Tier 2 human escalation is required.</li>
                </ul>
            </div>
            <span class="badge badge-tool">LLaMA 3.3 70B</span>
        </div>
        ''', unsafe_allow_html=True)

with tab3:
    st.markdown('<div class="section-header">LangGraph State Machine Architecture</div>', unsafe_allow_html=True)
    st.markdown('<div style="font-size:1.05rem; color:#475569; margin-bottom: 2rem; max-width: 900px;">The system\'s control flow is managed by <strong>LangGraph</strong>, ensuring predictable, auditable, and stateful multi-agent execution. Nodes never call each other directly—they only modify state and return it.</div>', unsafe_allow_html=True)
    
    st.markdown('''
    <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; padding: 2rem; margin-top: 1rem; max-width: 1000px;">
        <div style="display: flex; flex-direction: column; gap: 1rem;">
            
            <div class="trace-item done">
                <div class="trace-title">1. Investigation Node 🔍</div>
                <div class="trace-content">Runs security tools (IP lookup, threat intel, port scans) and queries vector memory for historical context. Gathers all necessary intelligence before engaging the LLM.</div>
            </div>
            
            <div class="trace-item done">
                <div class="trace-title">2. Triage Node (Agent) 🧠</div>
                <div class="trace-content">Analyzes the enriched log data alongside historical patterns, outputting a structured incident classification via Pydantic schemas.</div>
            </div>

            <div class="trace-item active">
                <div class="trace-title">3. Severity Router (Decision Point) 🔀</div>
                <div class="trace-content" style="background: #ffffff; padding: 1.2rem; border: 1px solid #e2e8f0; border-radius: 8px; margin-top: 0.8rem; line-height: 2;">
                    <strong>If Confidence < 70%:</strong> &nbsp;→&nbsp; <span class="badge badge-medium">Human Review Node</span><br>
                    <strong>If High/Critical & Confidence ≥ 70%:</strong> &nbsp;→&nbsp; <span class="badge badge-critical">Response Agent Node</span><br>
                    <strong>If Low/Medium & Confidence ≥ 70%:</strong> &nbsp;→&nbsp; <span class="badge badge-low">End Triage</span>
                </div>
            </div>

            <div class="trace-item done" style="border-left: 2px solid transparent; padding-bottom: 0;">
                <div class="trace-title">4. Memory Persist Node 💾</div>
                <div class="trace-content">Saves the finalized incident, reasoning, and execution traces into FAISS vector memory for future recall.</div>
            </div>

        </div>
    </div>
    ''', unsafe_allow_html=True)

with tab4:
    st.markdown('<div class="section-header">Data & Observability Ecosystem</div>', unsafe_allow_html=True)
    st.markdown('<div style="font-size:1.05rem; color:#475569; margin-bottom: 2rem; max-width: 900px;">AIR leverages a modern data stack to handle high-throughput network events, stateful incident memory, and complete execution transparency.</div>', unsafe_allow_html=True)
    
    st.markdown('''
    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem;">
        <div class="ui-card border-left-indigo">
            <div class="ui-card-title">📡 Network Feed (CICIDS-2017)</div>
            <div class="ui-card-desc">
                Raw network flow data is ingested automatically. The <code>cicids_parser</code> translates raw numeric flows into readable AI logs, enabling the agent to understand patterns without complex tabular embedding.
            </div>
        </div>
        
        <div class="ui-card border-left-green">
            <div class="ui-card-title">💾 Vector Memory (FAISS)</div>
            <div class="ui-card-desc">
                Provides the AI with "experience". Every processed incident is embedded using <code>all-MiniLM-L6-v2</code>. When new logs arrive, similar past attacks are injected as context to detect persistent threats over time.
            </div>
        </div>

        <div class="ui-card border-left-red">
            <div class="ui-card-title">⚡ Async Queue (Redis)</div>
            <div class="ui-card-desc">
                High-throughput log ingestion. The FastAPI server acts as a producer, pushing logs to a Redis List. Background workers pop logs, process them via LangGraph, and store results asynchronously, preventing API timeouts.
            </div>
        </div>

        <div class="ui-card border-left-slate">
            <div class="ui-card-title">🔎 Execution Tracing</div>
            <div class="ui-card-desc">
                Complete observability. <code>TraceCollector</code> logs exactly which nodes were visited, how long each step took, what tools were called (with their raw outputs), and the router's decision rationale for full auditability.
            </div>
        </div>
    </div>
    ''', unsafe_allow_html=True)
