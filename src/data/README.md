# src/data/

This module connects real-world network intrusion data to the agent pipeline.

## cicids_parser.py

Converts rows from the network intrusion dataset into `LogEvent`-compatible dicts. This is the bridge between a real-world CSV/DataFrame and the agent pipeline.

It handles:
- Stripping leading spaces from column names (common dataset issue)
- Mapping dataset label strings (`SSH-Patator`, `DoS Hulk`, etc.) to our `AttackType` enum values
- Building a readable `raw_log` string from numeric flow features
- Balanced sampling across attack types so the batch dataset is representative

## batch_runner.py

Sends a sample of dataset events through the live FastAPI `/analyze` endpoint, records the agent's output vs the ground truth label, and saves results to `data/results/batch_results.json`.

This file is what powers the Incident Dashboard and Eval Results pages.

**Run it with:**
```bash
python src/data/batch_runner.py
```
(FastAPI server must be running: `python run.py`)
