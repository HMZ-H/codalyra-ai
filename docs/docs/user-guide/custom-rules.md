---
sidebar_position: 5
title: Custom Rules
---

# Custom Rules

Define per-project regex rules to catch patterns specific to your codebase.

## Creating a Rule

Navigate to your project → **Custom Rules** → **Add Rule** and fill in:

| Field | Required | Description |
|-------|----------|-------------|
| **Name** | Yes | Short identifier (e.g., `no-console-error`) |
| **Pattern** | Yes | Regex pattern to match (e.g., `console\.error\(`) |
| **Severity** | Yes | `critical`, `warning`, or `info` |
| **Category** | Yes | Grouping label (e.g., `logging`, `security`) |
| **Message** | Yes | What to tell the developer when matched |
| **File Pattern** | No | Only check files matching this regex (e.g., `\.(ts|js)$`) |
| **Suggestion** | No | How to fix the match |

## Example Rules

### No console.error in production code

```json
{
  "name": "no-console-error",
  "pattern": "console\\.error\\(",
  "severity": "warning",
  "category": "logging",
  "message": "Use the structured logger instead of console.error",
  "file_pattern": "\\.(ts|js)$",
  "suggestion": "Replace with logger.error()"
}
```

### No hardcoded TODO in merged code

```json
{
  "name": "no-todo-comments",
  "pattern": "//\\s*TODO",
  "severity": "info",
  "category": "quality",
  "message": "TODO comment should be converted to an issue before merging"
}
```

### No direct database queries in route handlers

```json
{
  "name": "no-db-in-routes",
  "pattern": "db\\.query\\(|db\\.execute\\(",
  "severity": "warning",
  "category": "architecture",
  "message": "Use repository/service layer instead of direct DB queries in routes",
  "file_pattern": "api/"
}
```

## How Rules Execute

1. During a review, the worker loads all enabled rules for the project
2. Each added line in the diff (lines starting with `+`) is checked
3. If the file matches `file_pattern` (or no file pattern is set), the regex runs
4. Matches generate findings with `agent="custom-rules"`
5. These findings are passed to the LLM agents as pre-context alongside static analysis
6. The LLM can confirm, refine, or override custom rule findings

## Managing Rules

- **Enable/Disable** — Toggle a rule without deleting it
- **Edit** — Modify any field of an existing rule
- **Delete** — Permanently remove a rule
- **Test** — Paste a code snippet to preview what the rule catches

Rules are scoped to a single project. To share rules across projects, create them in each project individually.
