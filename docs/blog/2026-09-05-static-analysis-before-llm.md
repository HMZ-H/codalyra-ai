---
slug: static-analysis-before-llm
title: Why Static Analysis Before LLM Calls Is the Biggest Accuracy Win
authors: [hamza]
tags: [static-analysis, ai, architecture]
---

The cheapest improvement was also the most impactful. Running regex before the LLM improved finding recall from ~60% to ~95%.

<!--truncate-->

## The Observation

After building the 4-agent pipeline, I ran it against test diffs with known vulnerabilities. The security agent caught SQL injection consistently, but **missed hardcoded API keys in 2 out of 5 diffs**. The logic agent missed bare `except` clauses that any linter would flag. The performance agent sometimes hallucinated N+1 queries that didn't exist.

LLMs are brilliant at semantic understanding but unreliable at pattern matching. A regex will catch `AKIA[A-Z0-9]{16}` (AWS access key) 100% of the time. An LLM will catch it 80% of the time but also explain *why* it's dangerous.

## The Two-Stage Architecture

Run static validators first, then pass their findings to the LLM as pre-context:

```python
# Stage 1: Static analysis (deterministic, free, instant)
static_findings = []
static_findings.extend(run_security_checks(diff))
if "python" in languages:
    static_findings.extend(run_python_checks(diff))

# Filter to this agent's domain
relevant = [f for f in static_findings if is_relevant(f, agent_type)]

# Stage 2: LLM call with pre-context
result = reviewer.run_agent(
    diff_content=diff,
    pre_findings=relevant,  # This is the key
)
```

The agent prompt says: "You have pre-existing findings from static analysis. Confirm, refine, or override them. Also find issues that static analysis cannot detect."

## The Collaboration

This creates a partnership between regex and AI:

- **Regex catches** `AKIA[A-Z0-9]{16}` → LLM confirms and adds: "This key is passed to a function that logs to stdout — double exposure risk"
- **Regex flags** `except:` as bare except → LLM adds: "This catches KeyboardInterrupt, making the process unkillable"
- **Regex misses** a TOCTOU race condition → LLM catches it because it understands control flow

## The Numbers

| Metric | LLM Only | Static + LLM | Improvement |
|--------|----------|-------------|-------------|
| Hardcoded secrets | 3/5 diffs | 5/5 diffs | +40% |
| Code smell recall | ~60% | ~95% | +58% |
| False positives | ~2/review | ~1.5/review | −25% |
| Cost per finding | ~$0.005 | ~$0.003 | −40% |

The cost reduction is counterintuitive: by giving the LLM pre-findings, it spends fewer tokens rediscovering what regex already found and focuses on semantic issues. Shorter, more focused prompts produce more precise responses.

## Custom Rules Extend the Pattern

Users can define per-project regex rules that flow into the same pipeline:

```json
{
  "name": "no-console-error",
  "pattern": "console\\.error\\(",
  "severity": "warning",
  "message": "Use the structured logger instead"
}
```

Custom rule matches become findings with `agent="custom-rules"` that the LLM can confirm or refine, just like built-in static findings.

## Takeaway

Don't ask the LLM to do what regex can do better. Use static analysis for pattern matching (free, instant, deterministic). Use the LLM for semantic understanding (expensive, slow, brilliant). Wire them together so each amplifies the other.
