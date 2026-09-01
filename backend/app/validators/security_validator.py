import re


SECRET_PATTERNS = [
    (r'(?:api[_-]?key|apikey)\s*[=:]\s*["\'][A-Za-z0-9_\-]{16,}["\']', "hardcoded-api-key", "Possible hardcoded API key"),
    (r'(?:secret|token|password|passwd|pwd)\s*[=:]\s*["\'][^"\']{8,}["\']', "hardcoded-secret", "Possible hardcoded secret or password"),
    (r'AKIA[0-9A-Z]{16}', "aws-access-key", "AWS Access Key ID detected"),
    (r'ghp_[A-Za-z0-9]{36}', "github-token", "GitHub personal access token detected"),
    (r'sk-[A-Za-z0-9]{32,}', "openai-key", "OpenAI API key detected"),
    (r'xox[bpors]-[A-Za-z0-9\-]{10,}', "slack-token", "Slack token detected"),
]

DANGEROUS_CALLS = [
    (r'\beval\s*\(', "dangerous-eval", "Use of eval() — potential code injection"),
    (r'\bexec\s*\(', "dangerous-exec", "Use of exec() — potential code injection"),
    (r'os\.system\s*\(', "command-injection", "Use of os.system() — use subprocess with shell=False instead"),
    (r'subprocess\.(?:call|run|Popen)\s*\([^)]*shell\s*=\s*True', "shell-injection", "subprocess with shell=True — potential command injection"),
    (r'pickle\.loads?\s*\(', "insecure-deserialization", "Use of pickle — insecure deserialization risk"),
    (r'yaml\.load\s*\([^)]*(?!Loader)', "insecure-yaml", "yaml.load without SafeLoader — insecure deserialization"),
    (r'dangerouslySetInnerHTML', "xss-risk", "dangerouslySetInnerHTML — potential XSS if user input is unsanitized"),
]


def run_security_checks(diff_content: str) -> list[dict]:
    findings = []
    lines = diff_content.split("\n")
    current_file = None

    for i, line in enumerate(lines):
        if line.startswith("diff --git") or line.startswith("--- ") or line.startswith("+++ "):
            if line.startswith("+++ b/"):
                current_file = line[6:]
            elif line.startswith("+++ "):
                current_file = line[4:]
            continue

        if not line.startswith("+") or line.startswith("+++"):
            continue

        code_line = line[1:]

        for pattern, category, message in SECRET_PATTERNS + DANGEROUS_CALLS:
            if re.search(pattern, code_line, re.IGNORECASE):
                findings.append({
                    "file": current_file or "unknown",
                    "line": i + 1,
                    "severity": "critical",
                    "category": category,
                    "message": message,
                    "agent": "static-security",
                    "suggestion": None,
                })

    return findings
