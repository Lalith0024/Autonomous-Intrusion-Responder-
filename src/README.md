# src/

All application logic lives here. Each subfolder has a single responsibility — agents think, graph orchestrates, api exposes, models define, data handles real inputs.

| Folder | Responsibility |
|--------|---------------|
| `agents/` | LLM agents — triage and response |
| `graph/` | LangGraph state machine definition |
| `api/` | FastAPI routes and app setup |
| `models/` | Pydantic schemas for all inputs/outputs |
| `core/` | Configuration and environment loading |
| `data/` | Dataset parser and batch runner |
