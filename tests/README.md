# tests/

## Unit Tests

**`test_schemas.py`** — validates that Pydantic models accept valid inputs and reject invalid ones. Fast, no LLM calls, runs in CI.

**`test_analyze_endpoint.py`** — validates that the FastAPI `/analyze` endpoint returns the correct HTTP status codes. No LLM calls (tests invalid inputs only).

## Behavioral Evals

**`test_evals.py`** — this is not a unit test. It tests the **LLM's judgment** across 8 hand-crafted attack scenarios with known expected outputs. Each case checks whether the agent correctly identifies the attack type and severity.

This is called **behavioral evaluation** — testing model reliability, not code logic. It is the same concept used by production AI teams to validate model updates before deployment.

Run it with:
```bash
python tests/test_evals.py
```

Results are saved to `data/results/eval_results.json` for the dashboard.
