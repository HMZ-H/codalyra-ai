import re
import logging

logger = logging.getLogger(__name__)


def run_custom_rules(diff_content: str, rules: list[dict]) -> list[dict]:
    findings = []
    lines = diff_content.split("\n")
    current_file = None

    for line_num, line in enumerate(lines, 1):
        if line.startswith("diff --git"):
            parts = line.split(" b/")
            current_file = parts[-1] if len(parts) > 1 else None
            continue

        if not line.startswith("+") or line.startswith("+++"):
            continue

        code_line = line[1:]

        for rule in rules:
            if not rule.get("is_enabled", True):
                continue

            file_pattern = rule.get("file_pattern")
            if file_pattern and current_file:
                try:
                    if not re.search(file_pattern, current_file):
                        continue
                except re.error:
                    continue

            try:
                if re.search(rule["pattern"], code_line):
                    findings.append({
                        "file": current_file or "unknown",
                        "line": line_num,
                        "severity": rule.get("severity", "warning"),
                        "category": rule.get("category", "custom-rule"),
                        "message": rule.get("message", f"Custom rule '{rule.get('name', '')}' matched"),
                        "suggestion": rule.get("suggestion"),
                        "agent": "custom-rules",
                    })
            except re.error:
                logger.warning(f"Invalid regex in custom rule '{rule.get('name')}': {rule['pattern']}")

    return findings
