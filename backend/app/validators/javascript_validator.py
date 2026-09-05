import re


JS_TS_PATTERNS = [
    (r'\beval\s*\(', "dangerous-eval", "critical", "Use of eval() — potential code injection vulnerability"),
    (r'\.innerHTML\s*=', "xss-innerHTML", "critical", "Direct innerHTML assignment — potential XSS if user input is unsanitized"),
    (r'document\.write\s*\(', "xss-document-write", "critical", "document.write() — potential XSS and blocks page rendering"),
    (r'dangerouslySetInnerHTML', "xss-dangerouslySetInnerHTML", "warning", "dangerouslySetInnerHTML — ensure input is sanitized"),
    (r'\bnew\s+Function\s*\(', "dangerous-new-function", "critical", "new Function() — equivalent to eval, potential code injection"),
    (r'console\.\s*(?:log|warn|error|debug|info)\s*\(', "console-log", "info", "console statement in production code — remove or use a logger"),
    (r'\bvar\s+', "var-usage", "warning", "Use of var — prefer const or let for block scoping"),
    (r'==(?!=)', "loose-equality", "warning", "Loose equality (==) — use strict equality (===) to avoid type coercion"),
    (r'!=(?!=)', "loose-inequality", "warning", "Loose inequality (!=) — use strict inequality (!==)"),
    (r'\.prototype\s*\.', "prototype-pollution", "warning", "Prototype modification — risk of prototype pollution"),
    (r'(?:import|require)\s*\(.*\+', "dynamic-import", "warning", "Dynamic import with concatenation — potential path injection"),
    (r'\bany\b(?:\s*[;,\)\]\}]|\s*$)', "typescript-any", "info", "TypeScript 'any' type — defeats type safety"),
    (r'@ts-ignore', "ts-ignore", "info", "@ts-ignore — suppresses TypeScript errors, may hide real issues"),
    (r'@ts-nocheck', "ts-nocheck", "warning", "@ts-nocheck — disables type checking for entire file"),
    (r'(?:setTimeout|setInterval)\s*\(\s*["\']', "string-timeout", "warning", "String argument to setTimeout/setInterval — acts like eval"),
    (r'# ?TODO\b|# ?FIXME\b|// ?TODO\b|// ?FIXME\b', "todo-comment", "info", "TODO/FIXME comment — incomplete implementation"),
    (r'(?:async\s+)?function\s+\w+\s*\([^)]*\)\s*\{[^}]*(?:await|\.then)\b', "missing-async", "info", "Possible missing async keyword on function using await/then"),
]


def run_javascript_checks(diff_content: str) -> list[dict]:
    findings = []
    lines = diff_content.split("\n")
    current_file = None

    js_extensions = (".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs")

    for i, line in enumerate(lines):
        if line.startswith("+++ b/"):
            current_file = line[6:]
            continue
        elif line.startswith("+++ "):
            current_file = line[4:]
            continue

        if not line.startswith("+") or line.startswith("+++"):
            continue

        if current_file and not current_file.endswith(js_extensions):
            continue

        code_line = line[1:]

        for pattern, category, severity, message in JS_TS_PATTERNS:
            if re.search(pattern, code_line):
                findings.append({
                    "file": current_file or "unknown",
                    "line": i + 1,
                    "severity": severity,
                    "category": category,
                    "message": message,
                    "agent": "static-javascript",
                    "suggestion": None,
                })

    return findings
