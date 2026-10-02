---
sidebar_position: 2
title: Review Pipeline
---

# Review Pipeline

The review pipeline is the core of Codalyra-AI. This page explains what happens from the moment a diff is submitted to the final scored report.

## Pipeline Steps

### Step 1: Review Creation

```
POST /api/v1/reviews/
```

The API endpoint receives a diff and project ID. The `ReviewService` creates:

- 1 **Review** record (status: `pending`)
- 1 **Task** record (links review to runs)
- 6 **Run** records (one per agent: logic, security, performance, quality, synthesis, baseline)

### Step 2: Task Dispatch

The service dispatches 5 Celery tasks immediately:

```python
# 4 specialists run in parallel
for agent_type in ["logic", "security", "performance", "quality"]:
    run_specialist_review.delay(run_id, review_id, agent_type)

# Baseline runs independently
run_baseline_review.delay(baseline_run_id, review_id)
```

The synthesis task is **not** dispatched here — it's triggered after all specialists complete.

### Step 3: Static Analysis (Per Specialist)

Before each LLM call, the worker runs static validators:

1. **Security validator** — Checks for hardcoded secrets (AWS keys, API tokens) and dangerous functions (`eval()`, `os.system()`, `pickle.loads()`)
2. **Language validators** — Python (bare excepts, mutable defaults), JavaScript (prototype pollution, innerHTML), Go (unchecked errors)
3. **Custom rules** — User-defined regex patterns for this project

Only findings relevant to the specialist's domain are passed along.

### Step 4: LLM Agent Call

Each specialist receives:
- The full diff
- Relevant static findings as pre-context
- A domain-specific system prompt

The LLM returns structured JSON with findings (file, line, category, severity, message, suggestion).

### Step 5: Synthesis Trigger

Each specialist, upon completion (success or failure), chains a `check_and_trigger_synthesis` task:

```python
def check_and_trigger_synthesis(review_id):
    specialist_runs = get_specialist_runs(review_id)
    
    if any(run.status == "running" for run in specialist_runs):
        return  # Not all done yet
    
    if synthesis_run.status != "pending":
        return  # Already triggered (idempotency guard)
    
    synthesis_run.status = "running"
    db.commit()
    run_synthesis_review.delay(synthesis_run.id, review_id)
```

The idempotency guard prevents double-triggering if two specialists complete simultaneously.

### Step 6: Synthesis

The synthesis agent receives all specialist findings (not the raw diff). It:

1. Deduplicates overlapping findings
2. Resolves severity conflicts between agents
3. Prioritizes by impact
4. Produces a unified summary and final score

### Step 7: Completion

After synthesis:

1. Review status → `completed`
2. Final score, summary, and findings are stored
3. Baseline comparison is computed
4. Notifications fire (Slack/Discord)
5. WebSocket pushes status update to the frontend

## State Machine

```
Review:  pending → running → completed
                          → failed

Run:     pending → running → completed
                          → failed
```

## Error Handling

| Failure | Behavior |
|---------|----------|
| Specialist LLM call fails | Run status → `failed`, synthesis still triggers with available results |
| JSON parse error | Retries up to 3× with exponential backoff |
| All retries exhausted | Run completes with empty findings |
| Synthesis fails | Review status → `failed`, partial results are still stored |
| Baseline fails | Baseline fields are null, multi-agent results unaffected |

## Execution Trace

Every step is recorded as a **Trajectory** entry:

```python
trajectory = Trajectory(
    run_id=run.id,
    step_type="llm_call",
    input_data={"prompt_tokens": len(prompt)},
    output_data={"findings_count": len(findings)},
    duration_ms=elapsed,
)
```

This enables debugging and performance analysis of individual agent runs.
