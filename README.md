# Autonomous Intrusion Responder (AIR)

A multi-agent AI pipeline that analyzes raw network logs in real time, classifies threats, and generates containment playbooks — built on LangGraph + Groq.

---

## This vs a Classifier

A classifier takes an input and returns a label. That is one step, one model, one output.

AIR does something different. It **reasons**, **decides**, and **acts**:

1. A **Triage Agent** (LLM #1) reads the raw log and classifies the threat — but also returns a confidence score.
2. A **Policy Router** (conditional edge) reads that confidence score and severity, then decides which path to take next. This is a decision, not a prediction.
3. If the threat is High/Critical with high confidence → a **Response Agent** (LLM #2) writes a step-by-step containment playbook.
4. If confidence is low → a **Human Review Node** flags it for an analyst instead of guessing.

The graph path is different for every event. That routing behavior — confidence-based guardrails, multi-step playbooks, conditional branching — is what makes this an agent system, not a classifier.

---

## Architecture

```
LogEvent → FastAPI → LangGraph StateGraph
                          ↓
                     Triage Agent (LLM #1)
                          ↓
                     Policy Router (conditional edge)
                    ↙              ↘
          Response Agent      Human Review Node
           (LLM #2)           (guardrail flag)
                    ↘              ↙
                     IncidentReport
                          ↓
                  Streamlit Dashboard
```

---

## Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/Lalith0024/Autonomous-Intrusion-Responder-.git
cd autonomous-intrusion-responder

# 2. Set up environment
cp .env.example .env
# Add your GROQ_API_KEY to .env

# 3. Install dependencies
pip install -r requirements.txt

# 4. Start the API
python run.py

# 5. Start the dashboard (new terminal)
streamlit run dashboard.py
```

---

## Dataset

This project supports the Network Intrusion dataset from Kaggle for batch evaluation.

The dataset is auto-downloaded via `kagglehub`. Run the batch analyzer:

```bash
python src/data/batch_runner.py
```

This analyzes 50 real network events, compares the agent's output to ground truth labels, and saves results to `data/results/batch_results.json` — which powers the Incident Dashboard.

---

## Tech Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| API Layer | FastAPI | Exposes the `/analyze` endpoint |
| Orchestration | LangGraph | Manages multi-agent state and routing |
| LLM | Groq (Llama-3.3-70b) | Fast, free inference for both agents |
| Schemas | Pydantic | Enforces structured output from LLMs |
| Dashboard | Streamlit | Multi-page UI for live analysis and evals |
| Dataset | kagglehub | Auto-downloads network intrusion data |

---

## Project Structure

```
src/          Application logic — agents, graph, API, models, data
data/         Dataset inputs and batch analysis results
tests/        Unit tests + behavioral eval suite
pages/        Streamlit multipage dashboard pages
dashboard.py  Dashboard entry point
run.py        FastAPI server launcher
```
