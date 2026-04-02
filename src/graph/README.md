# src/graph/

LangGraph manages state across multiple agent calls. Each node in the graph is a function that reads from and writes to a shared `GraphState` dict. Nodes never call each other — they only modify state and return it.

The **conditional edge** in `severity_router` is what makes this a decision-making system, not a pipeline. After the triage node runs, the router inspects the result and chooses one of three paths:

```
triage_node
     ↓
severity_router (conditional edge)
  ↙         ↓          ↘
response_  human_      END
agent      review_     (triage
           node        sufficient)
```

| Condition | Route |
|-----------|-------|
| `confidence < 0.7` | → `human_review_node` |
| `confidence ≥ 0.7` AND severity `high/critical` | → `response_agent` |
| `confidence ≥ 0.7` AND severity `low/medium` | → `END` |

The `graph_path` field in every `IncidentReport` records exactly which nodes were visited — making the decision transparent and auditable.
