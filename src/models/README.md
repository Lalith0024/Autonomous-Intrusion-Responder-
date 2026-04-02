# src/models/

All Pydantic schemas live here. Pydantic ensures the LLM's output always matches the expected structure — if the LLM returns garbage or an unexpected field value, Pydantic rejects it before it reaches the API. This is how we prevent hallucinations from breaking the pipeline.

| Schema | Purpose |
|--------|---------|
| `LogEvent` | Incoming request — raw log + metadata |
| `AttackType` | Enum of classifiable attack categories |
| `SeverityLevel` | Enum of severity tiers (low → critical) |
| `RecommendedAction` | Enum of possible mitigations |
| `ResponsePlan` | Structured output from the response agent — steps, impact, escalation flag |
| `IncidentReport` | Full pipeline output — all triage fields + optional response plan + graph path |
