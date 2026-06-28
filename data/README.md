# 📊 AIR Data Ecosystem

This directory manages the lifecycle of network log data, threat intelligence state, and analysis results.

---

## 📂 Directory Structure

### 🛡️ `blocked_ips.json`
Acts as the **dynamic firewall state**. 
- **Purpose**: Tracks IPs blocked by the `Response Agent`.
- **Management**: Automatically updated by the `block_ip` tool. The Dashboard filters out expired entries based on `blocked_until`.

### 🧪 `cicids/` (The Feed)
- **Primary Source**: CICIDS-2017 Network Intrusion dataset.
- **Automation**: Managed via `kagglehub`. If the CSV is missing, the system auto-downloads it on the first execution of `src/data/batch_runner.py`.
- **Parser**: `src/data/cicids_parser.py` maps raw numeric flows to readable AI logs.

### 📈 `results/` (The Brain's Output)
| File | Description |
| :--- | :--- |
| `batch_results.json` | JSON snapshot of analyzed events used to populate the **Incident Dashboard**. |
| `eval_results.json` | Detailed metrics (F1 Score, Latency, Accuracy) for the AI model's performance. |

### 🧠 `vector_index/` (The Memory)
- **Engine**: FAISS (Facebook AI Similarity Search).
- **Function**: Local vector store used for **Incident Memory**. It allows the agent to recall similar past attacks for better triage.

---

## 🔄 Data Pipeline Logic

1.  **Ingest**: Raw CIDIDS records are sampled and converted to English.
2.  **Enrich**: Tool results (GeoIP, abuse scores) are appended as temporary context.
3.  **Persist**: Final `IncidentReport` objects are saved both to the `results/` JSON and the `vector_index/`.
4.  **Visualize**: Streamlit reads from these files to provide a real-time SOC view.

> [!IMPORTANT]
> To reset the system memory, simply delete the contents of `data/vector_index/` and the `results/` JSON files. The system will rebuild them on next run.
