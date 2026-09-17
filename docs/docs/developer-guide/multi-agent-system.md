---
sidebar_position: 3
title: Multi-Agent System
---

# Multi-Agent System

Codalyra uses 6 AI agents, each with a distinct role in the review pipeline.

## Agent Types

### Specialist Agents

| Agent | System Prompt Focus | Example Catches |
|-------|-------------------|-----------------|
| **Logic** | Correctness, control flow, edge cases | Off-by-one, null deref, race conditions, wrong comparisons |
| **Security** | OWASP Top 10, attack surfaces | SQL injection, XSS, command injection, hardcoded secrets |
| **Performance** | Efficiency, resource usage | N+1 queries, O(n²) loops, memory leaks, blocking I/O |
| **Quality** | Readability, maintainability | DRY violations, dead code, magic numbers, poor naming |

Each specialist runs independently and in parallel via Celery.

### Synthesis Agent

The synthesis agent does **not** see the raw diff. It receives all specialist findings and:

1. **Deduplicates** — If Logic and Security both flag the same line, it keeps the most specific finding
2. **Resolves conflicts** — If agents disagree on severity, it uses the higher severity
3. **Prioritizes** — Orders findings by impact and actionability
4. **Summarizes** — Produces a narrative summary of the code's overall quality

### Baseline Agent

A single-prompt review with no specialization and no static pre-scan. It exists purely as a control for measuring multi-agent improvement.

## Why Specialization Works

A single prompt asking an LLM to "review this code" produces broad, shallow analysis. The model tries to balance multiple concerns and misses depth in each area.

Specialist prompts tell the model: "You are a security expert. Your only job is finding vulnerabilities." This focus produces:

- **Deeper analysis** — The model devotes full attention to one domain
- **Fewer false positives** — The prompt constrains the scope
- **Better suggestions** — Domain-specific remediation advice

## Coordination

The coordination challenge: synthesis must wait for all 4 specialists but not block on them individually.

```
                    ┌─ Logic ──────┐
                    ├─ Security ───┤
    Dispatch ──────►├─ Performance ┤──► check_and_trigger ──► Synthesis
                    └─ Quality ────┘
                    
                    └─ Baseline (independent) ─────────────────►
```

### Avoiding Race Conditions

If two specialists finish at the exact same time:

1. Both chain `check_and_trigger_synthesis`
2. The first check sees all specialists done → flips synthesis to `running` → dispatches
3. The second check sees synthesis is already `running` → exits (idempotency guard)

No distributed locks needed. The database status is the source of truth.

### Failure Tolerance

The `check_and_trigger_synthesis` runs in a `finally` block, so even failed specialists trigger it. The check counts `running` runs, not `completed` runs, so it waits for all to finish regardless of outcome.

## Adding a New Agent

To add a new specialist (e.g., "accessibility"):

1. **Add the prompt** in `app/ai/prompts.py`
2. **Add the agent type** to the specialist list in `app/services/review_service.py`
3. The worker already handles any agent type — it looks up the prompt by name
4. The synthesis agent automatically incorporates findings from any specialist
5. Update the frontend's agent tab rendering

No changes needed to the coordination logic.

## Agent Configuration

Each agent can be configured per-project via the `AgentConfig` model:

```python
class AgentConfig(Base):
    project_id: uuid.UUID     # Which project
    agent_type: str           # "logic", "security", etc.
    is_enabled: bool          # Skip this agent entirely
    provider: str | None      # "gemini", "openai", "anthropic"
    model_name: str | None    # Override default model
    custom_prompt: str | None # Override the system prompt
```
