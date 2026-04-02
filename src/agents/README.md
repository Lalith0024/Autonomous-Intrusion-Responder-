# src/agents/

Each agent is a self-contained LLM call with a specific role, system prompt, and structured output schema. Agents do not call each other — the graph orchestrates them.

Unlike a utility function, an agent:
- Has a clearly defined **goal** (triage this event / generate a playbook for this incident)
- Operates with a **persona** (SOC analyst / senior incident responder)
- Returns a **strictly typed**, validated output via Pydantic

## Agents

**`triage_agent.py`**
Reads a raw log event and returns: attack type, severity level, confidence score (0–1), recommended action, reasoning, and indicators of compromise. This is LLM call #1 in the pipeline.

**`response_agent.py`**
Takes the triage output for a High/Critical incident and generates a step-by-step containment playbook. Only called when severity and confidence both meet the threshold. This is LLM call #2.

Both agents support Groq (Llama-3.3-70b) as primary and OpenAI (GPT-4o-mini) as fallback — switching is done via environment variables, not code changes.
