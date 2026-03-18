# Autonomous Intrusion Responder

Network Security AI Agent built with Python, LangChain, LangGraph, and FastAPI to automatically triage network log events.

## Architecture

```text
+----------------+      +-------------+      +----------------+
|                |      |             |      |                |
|  Raw Log Event +----->+ FastAPI App +----->+  LangGraph     |
|                |      |             |      |                |
+----------------+      +------+------+      +-------+--------+
                               ^                     |
                               |                     v
                        +------+------+      +-------+--------+
                        |             |      |                |
                        |  Report Out |<-----+ LangChain LLM  |
                        |             |      | (Triage Agent) |
                        +-------------+      +----------------+
```

## Quick Start

```bash
git clone https://github.com/YOUR_USERNAME/autonomous-intrusion-responder.git
cd autonomous-intrusion-responder
cp .env.example .env          # Add your OPENAI_API_KEY
pip install -r requirements.txt
python run.py
```

## Demo Request

```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "timestamp": "2026-03-18T22:00:00Z",
    "source_ip": "45.33.32.156",
    "destination_ip": "192.168.1.10",
    "destination_port": 22,
    "protocol": "TCP",
    "event_type": "failed_login",
    "raw_log": "Mar 18 22:00:01 server sshd[1234]: Failed password for root from 45.33.32.156 port 54832 ssh2"
  }'
```

## Feature Roadmap
- ✅ Feature 1: Log ingestion and triage validation API
- ⏳ Feature 2: Parallel forensics and threat intelligence nodes
- ⏳ Feature 3: Webhook alerting to real network defenses
- ⏳ Feature 4: Interactive dashboard
