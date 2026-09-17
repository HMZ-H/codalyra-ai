---
sidebar_position: 5
title: Static Analysis
---

# Static Analysis Validators

Static analysis runs **before** the LLM call. Its findings are passed as pre-context to the AI agent, creating a hybrid analysis pipeline.

## Why Static Before LLM?

| Metric | LLM Only | Static + LLM | Improvement |
|--------|----------|-------------|-------------|
| Hardcoded secrets caught | 3/5 diffs | 5/5 diffs | +40% |
| Code smell detection | ~60% recall | ~95% recall | +58% |
| False positives | ~2/review | ~1.5/review | −25% |
| Cost per finding | ~$0.005 | ~$0.003 | −40% |

Static analysis is free, instant, and deterministic. The LLM is expensive, slow, and brilliant at semantic understanding. Together they cover more ground than either alone.

## Built-in Validators

### Security Validator (`security_validator.py`)

**Hardcoded Secrets:**
- AWS access keys (`AKIA[A-Z0-9]{16}`)
- GitHub tokens (`gh[ps]_[A-Za-z0-9]{36,}`)
- Slack tokens (`xox[bprs]-[A-Za-z0-9-]+`)
- OpenAI API keys (`sk-[A-Za-z0-9]{32,}`)
- Generic patterns (`api_key`, `secret`, `password` assignments)

**Dangerous Functions:**
- `eval()`, `exec()` — Code injection
- `os.system()`, `subprocess` with `shell=True` — Command injection
- `pickle.loads()` — Arbitrary code execution
- `yaml.load()` without SafeLoader — YAML deserialization attack
- `innerHTML` assignment — XSS risk

### Python Validator (`python_validator.py`)

- Bare `except:` clauses (catches KeyboardInterrupt/SystemExit)
- Mutable default arguments (`def f(items=[])`)
- `assert` in production code
- `print()` statements (use logging)

### JavaScript Validator (`javascript_validator.py`)

- `document.write()` — XSS risk
- `__proto__` assignment — Prototype pollution
- Missing `await` on async calls
- `var` usage (use `const`/`let`)

### Go Validator (`golang_validator.py`)

- Unchecked error returns (`_ = someFunc()`)
- `fmt.Print` in production (use structured logging)

### Language Detection (`detector.py`)

Parses `+++ b/path/to/file.ext` headers from the unified diff, extracts file extensions, and maps them to language names. Only language-specific validators for detected languages are executed.

## Custom Rules

Users define per-project regex rules that run alongside built-in validators:

```python
# Worker loads enabled rules for the project
custom_findings = run_custom_rules(diff_content, project_rules)

# All findings flow into the agent
all_static = security + python + javascript + custom
relevant = filter_for_agent(all_static, agent_type)
```

See the [Custom Rules user guide](/docs/user-guide/custom-rules) for rule definition syntax.

## How Findings Flow to the LLM

```python
# Stage 1: Static analysis
static_findings = []
static_findings.extend(run_security_checks(diff))
if "python" in languages:
    static_findings.extend(run_python_checks(diff))

# Filter to this agent's domain
relevant = [f for f in static_findings if is_relevant(f, agent_type)]

# Stage 2: LLM call with pre-context
result = reviewer.run_agent(
    diff_content=diff,
    agent_type=agent_type,
    pre_findings=relevant,  # Static findings as context
)
```

The agent prompt instructs the LLM: "You have pre-existing findings from static analysis. Confirm, refine, or override them. Also find issues that static analysis cannot detect."
