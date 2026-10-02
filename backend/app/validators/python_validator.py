import re

PYTHON_PATTERNS = [
    (r'except\s*:', "bare-except", "warning", "Bare except clause — catches all exceptions including SystemExit and KeyboardInterrupt"),
    (r'def\s+\w+\s*\([^)]*=\s*(\[\]|\{\}|\bset\(\))', "mutable-default", "warning", "Mutable default argument — shared across all calls"),
    (r'\bassert\b(?!.*(?:test_|_test|pytest|unittest))', "assert-in-prod", "info", "assert statement in non-test code — stripped in optimized mode"),
    (r'from\s+\w+\s+import\s+\*', "wildcard-import", "info", "Wildcard import — pollutes namespace and hides dependencies"),
    (r'# ?TODO\b|# ?FIXME\b|# ?HACK\b|# ?XXX\b', "todo-comment", "info", "TODO/FIXME comment — incomplete implementation"),
    (r'print\s*\(', "print-statement", "info", "print() in production code — use logging instead"),
]


def run_python_checks(diff_content: str) -> list[dict]:
    findings = []
    lines = diff_content.split("\n")
    current_file = None

    for i, line in enumerate(lines):
        if line.startswith("+++ b/"):
            current_file = line[6:]
            continue
        elif line.startswith("+++ "):
            current_file = line[4:]
            continue

        if not line.startswith("+") or line.startswith("+++"):
            continue

        if current_file and not current_file.endswith(".py"):
            continue

        code_line = line[1:]

        for pattern, category, severity, message in PYTHON_PATTERNS:
            if re.search(pattern, code_line):
                findings.append({
                    "file": current_file or "unknown",
                    "line": i + 1,
                    "severity": severity,
                    "category": category,
                    "message": message,
                    "agent": "static-python",
                    "suggestion": None,
                })

    return findings
