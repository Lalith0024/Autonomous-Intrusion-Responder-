# 🛡️ AIR: Autonomous Intrusion Responder

A production-ready, AI-driven cybersecurity agent that provides real-time threat detection, automated triage, and active incident response for server infrastructure.

[![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python&logoColor=white)]()
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?logo=fastapi&logoColor=white)]()
[![LangChain](https://img.shields.io/badge/LangChain-Agents-1C3C3C?logo=langchain&logoColor=white)]()
[![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B?logo=streamlit&logoColor=white)]()
[![Redis](https://img.shields.io/badge/Redis-Queue-DC382D?logo=redis&logoColor=white)]()

---

## 📋 Table of Contents
- [Overview](#-overview)
- [Key Features](#-key-features)
- [System Architecture](#-system-architecture)
- [Tech Stack](#️-tech-stack)
- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [Benchmarking](#-benchmarking)
- [Project Structure](#-project-structure)
- [Troubleshooting](#-troubleshooting)
- [Future Enhancements](#-future-enhancements)
- [Acknowledgments](#-acknowledgments)

---

## 🎯 Overview
**AIR (Autonomous Intrusion Responder)** is not just an analytics dashboard; it is an active defense mechanism. Moving beyond static, rule-based firewalls, AIR utilizes Large Language Models (LLMs) to natively understand context, reason through multi-stage attacks, and autonomously mitigate threats in real-time. 

### Why This Project?
✅ **AI-Driven Reasoning:** Replaces rigid regex rules with dynamic, context-aware threat triage (via LLaMA-3.3-70B).
✅ **Zero-Trust Enforcement:** Automatically generates and executes bash/firewall commands (e.g., `iptables`) to block malicious IPs dynamically.
✅ **High-Speed Ingestion:** Asynchronous FastAPI backend coupled with Redis queues ensures high-throughput, non-blocking log ingestion.
✅ **Long-Term Memory:** Integrates a FAISS Vector Database to remember past attacks and adapt to recurring threats.
✅ **Production-Ready UI:** Features a sleek, glassmorphism-styled Streamlit dashboard with native active-state navigation.

---

## ✨ Key Features

### Core Capabilities
🛡️ **Multi-Agent Defense System**
- **Triage Agent:** Analyzes raw logs (Nginx, SSH) and categorizes payloads (SQLi, XSS, DDoS).
- **Response Agent:** Formulates mitigation strategies and issues active system blocks.
- **Memory Context:** Embeds previous attack data to establish behavioral baselines.

🚀 **Performance & Concurrency**
- **Redis Task Queuing:** Fully decouples log ingestion from AI processing to prevent API bottlenecks.
- **Asynchronous Execution:** Built on FastAPI to handle thousands of concurrent web requests.
- **Sub-Second Latencies:** Optimized prompt chains achieve response times averaging ~3.4s for full reasoning loops.

🎨 **Command Center Dashboard**
- **Live Analysis:** Watch the AI process and reason through incoming logs in real-time.
- **Incident History:** Filter, search, and export data on historical threats.
- **Benchmarking UI:** Track the agent's accuracy against the CICIDS-2017 ground truth dataset.
- **Premium Design:** Curated color palettes, modern typography (`Outfit`, `Inter`), and gradient borders.

---

## 🏗️ System Architecture

### The Workflow:
1. **Ingestion:** Live servers pipe logs to the `/analyze` endpoint via a fast bash one-liner.
2. **Queuing:** FastAPI pushes the payload to a Redis queue instantly.
3. **Reasoning:** The background worker pulls the log, queries the FAISS memory vector store, and triggers the Triage Agent.
4. **Action:** If the payload is malicious, the Response Agent fires, adding the IP to the blocklist.
5. **Visualization:** The Streamlit frontend dynamically polls and visualizes the exact reasoning steps.

---

## 🛠️ Tech Stack

| Component | Technology | Role |
| :--- | :--- | :--- |
| **Language** | Python (3.10+) | Core ecosystem |
| **AI / Orchestration** | LangChain & Groq | LLaMA-3.3 integration and agent loops |
| **Backend API** | FastAPI & Uvicorn | High-speed, async log ingestion |
| **Queueing** | Redis & RQ | Background task management |
| **Memory Storage** | FAISS | Vector database for attack history |
| **Frontend UI** | Streamlit (v1.58+) | Real-time `st.navigation` dashboard |

---

## 📦 Installation

### Prerequisites
- Python 3.10+
- Redis Server (must be running in the background)
- Internet connection (for Groq API access)

### Step-by-Step Setup
1. **Clone Project**
   ```bash
   git clone https://github.com/Lalith0024/Autonomous-Intrusion-Responder-.git
   cd Autonomous-Intrusion-Responder-
   ```
2. **Create Environment**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```
4. **Environment Variables**
   Create a `.env` file in the root directory:
   ```env
   GROQ_API_KEY=your_api_key_here
   REDIS_URL=redis://localhost:6379/0
   ```

---

## 🚀 Quick Start

To run the full stack locally, you need three terminal windows:

**1. Start Redis (If not already running as a service)**
```bash
redis-server
```

**2. Start the Backend & Worker**
```bash
source .venv/bin/activate
python run.py
```

**3. Launch the Dashboard**
```bash
source .venv/bin/activate
streamlit run src/streamlit_app/dashboard.py
```
*Navigate to `http://localhost:8501` to view the Cyber Command Center.*

---

## 🧪 Benchmarking

AIR comes with a rigorous evaluation engine built-in to prove its reliability against real-world data.

*   **CICIDS-2017 Dataset:** Automatically parses and evaluates accuracy against ground-truth network logs.
*   **Adversarial Suite:** 50+ custom red-team payloads (SQLi evasion, Slowloris, Ping of Death) to test edge-case reasoning.
*   **Run Evaluations:** 
    ```bash
    python src/data/batch_runner.py
    python -m src.evals.evaluation_engine
    ```

---

## 📁 Project Structure

```text
Autonomous-Intrusion-Responder-/
├── src/
│   ├── agents/          # Triage & Response LangChain logic
│   ├── api/             # FastAPI routing and endpoints
│   ├── core/            # Config, telemetry, and tracing
│   ├── evals/           # Adversarial benchmarking engine
│   ├── graph/           # Threat intelligence workflow logic
│   ├── memory/          # FAISS vector store integration
│   ├── queue/           # Redis worker initialization
│   ├── tools/           # Custom bash/firewall execution tools
│   └── streamlit_app/   # Premium glassmorphism UI
├── data/                # Datasets & benchmark results
├── .env.example         # Environment templates
└── requirements.txt     # Python dependencies
```

---

## 🐛 Troubleshooting

❌ **"Cannot connect to API — is FastAPI running?"**
> Ensure `python run.py` is running and that Redis is actively accepting connections on port 6379.

❌ **"Streamlit UI is showing 0s in Performance Mode"**
> You must run the benchmarking scripts (`batch_runner.py` and `evaluation_engine.py`) to generate the local JSON result files.

❌ **"Groq Rate Limit Exceeded"**
> The Evaluation Engine runs incredibly fast. If you hit rate limits, add a slight `time.sleep(2)` inside the batch runner loops.

---

## 🔮 Future Enhancements
- [ ] Direct IP-Tables integration script for Linux production servers.
- [ ] Multi-tenant support for monitoring multiple servers simultaneously.
- [ ] Exportable PDF incident reporting for compliance audits.

---

## 🙏 Acknowledgments
- **CICIDS-2017** for providing the ground-truth network analysis dataset.
- **LangChain** for robust agentic workflows.
- **Groq** for providing ultra-low latency LLaMA-3.3 inference.

Built with ❤️ by [Lalithendra Kasula](https://github.com/Lalith0024)
