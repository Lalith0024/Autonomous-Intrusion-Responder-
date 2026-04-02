# data/

Real input data and analysis results. This folder is intentionally not committed to Git (except for `.gitkeep` placeholders).

## cicids/

Place the network intrusion CSV here. The dataset is auto-downloaded via `kagglehub` when you run `src/data/batch_runner.py` — no manual download needed.

## results/

Stores batch analysis output and eval results:

| File | Created by | Read by |
|------|-----------|---------|
| `batch_results.json` | `src/data/batch_runner.py` | Incident Dashboard, Eval Results pages |
| `eval_results.json` | `tests/test_evals.py` | Eval Results page |

Both files are generated on first run and cached — the dashboard reads from them without making additional LLM calls.
