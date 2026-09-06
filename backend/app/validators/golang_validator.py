import re


GO_PATTERNS = [
    (r'if\s+err\s*!=\s*nil\s*\{[\s\S]*?\breturn\b.*\}', None, None, None),
    (r'\berr\s*=\s*\w+', "unchecked-error", "warning", "Error assigned but not checked — handle or explicitly ignore with _"),
    (r'defer\s+\w+\.Close\(\)', None, None, None),
    (r'\.Open\s*\(', "unclosed-resource", "warning", "File/resource opened — ensure it is closed with defer"),
    (r'go\s+func\s*\(', "goroutine-leak", "warning", "Anonymous goroutine — ensure it terminates and doesn't leak"),
    (r'for\s+.*range\s+\w+\s*\{[^}]*go\s+', "goroutine-in-loop", "warning", "Goroutine launched in loop — may capture loop variable by reference"),
    (r'fmt\.Print(?:ln|f)?\s*\(', "fmt-print", "info", "fmt.Print in production code — use structured logging instead"),
    (r'log\.Fatal\s*\(', "log-fatal", "warning", "log.Fatal calls os.Exit — may skip deferred cleanup"),
    (r'panic\s*\(', "panic-usage", "warning", "panic() in non-init code — prefer returning errors"),
    (r'sql\.Open\s*\(.*\+', "sql-concatenation", "critical", "String concatenation in SQL — potential SQL injection, use parameterized queries"),
    (r'fmt\.Sprintf\s*\(.*SELECT|INSERT|UPDATE|DELETE', "sql-sprintf", "critical", "SQL query built with fmt.Sprintf — use parameterized queries instead"),
    (r'os\.Getenv\s*\(', "env-without-default", "info", "os.Getenv returns empty string if unset — consider using a default or validation"),
    (r'interface\{\}', "empty-interface", "info", "Empty interface{} — consider using a concrete type or any (Go 1.18+)"),
    (r'# ?TODO\b|// ?TODO\b|// ?FIXME\b|// ?HACK\b', "todo-comment", "info", "TODO/FIXME comment — incomplete implementation"),
    (r'sync\.Mutex\b(?!.*\block\b)', "mutex-without-lock", "info", "Mutex declared — verify Lock/Unlock pairs and defer usage"),
    (r'time\.Sleep\s*\(', "time-sleep", "info", "time.Sleep in production code — consider using tickers, channels, or context"),
    (r'(?:password|secret|token|apikey)\s*(?::=|=)\s*"[^"]{4,}"', "hardcoded-secret", "critical", "Possible hardcoded secret or credential in Go source"),
]


def run_golang_checks(diff_content: str) -> list[dict]:
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

        if current_file and not current_file.endswith(".go"):
            continue

        code_line = line[1:]

        for pattern, category, severity, message in GO_PATTERNS:
            if category is None:
                continue
            if re.search(pattern, code_line, re.IGNORECASE):
                findings.append({
                    "file": current_file or "unknown",
                    "line": i + 1,
                    "severity": severity,
                    "category": category,
                    "message": message,
                    "agent": "static-golang",
                    "suggestion": None,
                })

    return findings
