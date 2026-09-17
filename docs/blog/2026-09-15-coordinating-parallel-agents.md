---
slug: coordinating-parallel-agents
title: How I Coordinated 6 Parallel AI Agents Without Race Conditions
authors: [hamza]
tags: [ai, celery, architecture]
---

The hardest problem in Codalyra-AI wasn't the AI — it was the orchestration.

Every code review dispatches 6 independent Celery tasks: 4 specialist agents (logic, security, performance, quality), 1 synthesis agent, and 1 baseline agent. The specialists run in parallel, but the synthesis agent **must wait for all 4 specialists to finish** before it can merge their findings.

<!--truncate-->

## The Problem

This sounds simple until you think about what can go wrong:

- What if two specialists finish at the same millisecond and both try to trigger synthesis?
- What if one specialist fails — does synthesis wait forever?
- What if the worker crashes after updating the database but before dispatching the next task?

## The Naive Approach (and Why It Breaks)

My first attempt was a simple callback: each specialist, upon completing, checks if all 4 are done and triggers synthesis:

```python
# BROKEN: race condition
def on_specialist_complete(review_id):
    runs = db.query(Run).filter_by(review_id=review_id).all()
    completed = [r for r in runs if r.status == "completed"]
    if len(completed) == 4:  # Two workers can both see 4 here
        trigger_synthesis(review_id)
```

If two specialists complete within the same database transaction window, both see 4 completed runs and both dispatch synthesis. Now you have **two synthesis tasks** fighting over the same review.

## The Solution: Idempotent Check-Then-Act

The fix was a dedicated Celery task — `check_and_trigger_synthesis` — that every specialist chains to upon completion. The key insight: even if the task runs multiple times, the idempotency guard ensures synthesis fires exactly once.

```python
@celery.task
def check_and_trigger_synthesis(review_id):
    specialist_runs = db.query(Run).filter(
        Run.task_id == task.id,
        Run.agent_type.in_(["logic", "security", "performance", "quality"])
    ).all()

    if any(r.status == "running" for r in specialist_runs):
        return  # Not all done yet

    synthesis_run = db.query(Run).filter_by(
        task_id=task.id, agent_type="synthesis"
    ).first()

    if synthesis_run.status != "pending":
        return  # Already triggered — idempotency guard

    synthesis_run.status = "running"
    db.commit()
    run_synthesis_review.delay(synthesis_run.id, review_id)
```

## Why This Works

1. **Idempotency**: The `status != "pending"` check means double-execution is harmless. First call flips to "running"; second sees it's already running and exits.

2. **Failure tolerance**: The check runs in a `finally` block, so even failed specialists trigger it. The check counts "running" runs, not "completed", so it waits for all to finish regardless of outcome.

3. **No distributed locks**: I considered Redis locks (SETNX), but the database state is the source of truth and the idempotency check makes double-execution harmless.

## The Baseline Runs Independently

The 6th task — the baseline single-pass review — runs completely independently. It doesn't participate in the synthesis trigger and doesn't wait for anything. Its result is compared to the multi-agent result in the report, serving as a control.

## Lesson Learned

The hardest part of multi-agent systems isn't the agents — it's the coordination. Get the orchestration wrong and you have duplicate work, missed triggers, or corrupted state. Get it right and the agents are just functions with fancy prompts.
