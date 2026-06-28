# 🛡️ PROTECT YOUR SITE WITH AIR (V2 GUIDE)

The **Autonomous Intrusion Responder (AIR)** is not just a dashboard; it is a real-world defensive agent. This guide explains how to connect your production infrastructure to the AIR engine.

---

## 1. 📥 REAL-TIME LOG INGESTION
To protect a live server, you need to "pipe" your system or web logs (Apache, Nginx, SSH) to the AIR API

### Option A: Bash One-Liner (Fastest)
Run this on your server to pipe every new log entry to the AI for immediate analysis:
```bash
tail -F /var/log/nginx/access.log | while read line; do
  curl -X POST "http://your-air-ip:8000/analyze" \
       -H "Content-Type: application/json" \
       -d "{\"raw_log\": \"$line\", \"event_type\": \"nginx_access\"}"
done
```

### Option B: Redis Queue (High Scale)
If you have millions of logs, use the **Asynchronous Ingestion** endpoint.
1. Enable `REDIS_ENABLED=true` in `.env`.
2. Send logs to `/ingest` instead of `/analyze`:
```bash
curl -X POST "http://your-air-ip:8000/ingest" -d "{\"raw_log\": \"...\"}"
```
*The AI will process the queue in the background using the dedicated Worker.*

---

## 2. ⚔️ ENABLING AUTONOMOUS RESPONSE
By default, the AI only "recommends" actions. To let it actually **BLOCK** attackers:

### Step 1: Configure the Toolkit
Ensure `TOOLS_ENABLED=true` in your `.env`.

### Step 2: Provision Firewall Access
The `block_ip` tool (located in `src/tools/security_toolkit.py`) can be customized to run real system commands. Out of the box, it writes to `data/blocked_ips.json`. To make it real, update the tool to run `iptables`:
```python
# src/tools/security_toolkit.py
def block_ip(ip: str):
    # Example: Real IPTables Block
    import subprocess
    subprocess.run(["sudo", "iptables", "-A", "INPUT", "-s", ip, "-j", "DROP"])
    return "IP BLOCKED IN FIREWALL"
```

---

## 3. 🧠 HISTORICAL MEMORY (FAISS)
AIR uses **Vector Similarity Search** to remember attackers.
- If an IP attacks your site, AIR stores the signature in `data/vector_index`.
- If the same IP (or a similar attack pattern from a different IP) returns 10 days later, the AI will recall the previous incident and escalate the priority automatically.

---

## 4. 📊 OBSERVABILITY
Monitor the **Command Center** dashboard on `http://localhost:8501`.
- **Live Analyst**: Watch the reasoning trace — see *how* the agent decided to block someone.
- **Threat Intel**: View the history of all contained threats.
- **Benchmarking**: Run local red-team tests to verify the AI's accuracy before deploying it to production.

---

## 🚀 READY FOR PRODUCTION
For full production deployment, use the provided Docker Compose:
```bash
docker-compose up --build -d
```
*This starts the API, the Redis Queue, the Background Reasoning Worker, and the SOC Dashboard.*
