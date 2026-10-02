---
sidebar_position: 3
title: Understanding Reports
---

# Understanding Review Reports

After a review completes, Codalyra generates a detailed report with findings from all agents.

## Report Structure

### Score

Every review produces a score from **0 to 100**:

- Start at 100
- **Critical** finding: −30 points
- **Warning** finding: −10 points
- **Info** finding: −2 points
- Minimum score: 0

A single critical vulnerability (e.g., SQL injection) drops the score to 70. This is intentional — one critical issue matters more than twenty clean functions.

### Findings

Each finding includes:

| Field | Description |
|-------|-------------|
| **File** | The file path where the issue was found |
| **Line** | The specific line number |
| **Category** | e.g., `security`, `performance`, `logic`, `quality` |
| **Severity** | `critical`, `warning`, or `info` |
| **Message** | Description of the issue |
| **Suggestion** | How to fix it |
| **Agent** | Which specialist found it |

### Agent Tabs

The report shows findings organized by agent. Click each tab to see what each specialist found:

- **Synthesis** — The merged, deduplicated, prioritized view (default)
- **Logic** — Correctness issues
- **Security** — Vulnerability findings
- **Performance** — Efficiency concerns
- **Quality** — Maintainability suggestions
- **Baseline** — Single-pass comparison

### Baseline Comparison

Every report includes a side-by-side comparison:

| Metric | Baseline | Multi-Agent |
|--------|----------|-------------|
| Score | Typically 60–80 | Typically 80–95 |
| Findings | 3–5 avg | 9–14 avg |
| Approach | Single generic prompt | 4 specialists + synthesis |

This proves the multi-agent approach catches more issues with higher precision.

## Finding Feedback

You can provide feedback on each finding:

- **Accept** — The finding is valid and useful
- **Dismiss** — The finding is not relevant here
- **False Positive** — The finding is incorrect

This feedback is tracked per-agent, building accuracy metrics over time. You can see per-agent accuracy in the Analytics dashboard.

## Auto-Fix Suggestions

For critical and warning findings, click **Auto-Fix** to generate LLM-powered code corrections. Each fix shows:

- **Original code** — The problematic snippet
- **Fixed code** — The suggested correction
- **Explanation** — Why this fix resolves the issue

Auto-fixes are suggestions only — they don't modify your repository.

## Exporting Reports

Click **Export** to download the review as a Markdown file for sharing with your team.
