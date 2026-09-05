import json
import logging

from app.ai.client import LLMClient
from app.ai.providers import LLMProvider

logger = logging.getLogger(__name__)

FIX_PROMPT = """You are a senior software engineer generating code fixes for review findings.
You will receive a code diff and a list of findings (issues detected by a code review pipeline).

For each finding, generate a corrected code snippet that fixes the issue.

Respond with a JSON object:
{
  "fixes": [
    {
      "finding_index": <integer — 0-based index matching the input findings array>,
      "original_code": "<the problematic code as it appears in the diff>",
      "fixed_code": "<the corrected code>",
      "explanation": "<one-sentence explanation of what changed and why>"
    }
  ]
}

RULES:
- Only generate fixes for findings where a concrete code change is possible.
- Skip findings that are architectural suggestions, missing-feature requests, or cannot be fixed with a simple code change.
- Keep fixes minimal — change only what is necessary to address the finding.
- Preserve the original code style and indentation.
- If no findings can be fixed, return {"fixes": []}.
"""


class AutoFixer:
    def __init__(self, llm_client: LLMClient | LLMProvider):
        self.llm = llm_client

    def generate_fixes(self, diff_content: str, findings: list[dict]) -> list[dict]:
        if not findings:
            return []

        fixable = [
            f for f in findings
            if f.get("severity") in ("critical", "warning")
            and f.get("file")
        ]
        if not fixable:
            return []

        user_message = json.dumps({
            "diff": diff_content[:8000],
            "findings": [
                {
                    "index": i,
                    "file": f.get("file"),
                    "line": f.get("line"),
                    "severity": f.get("severity"),
                    "category": f.get("category"),
                    "message": f.get("message"),
                    "suggestion": f.get("suggestion"),
                }
                for i, f in enumerate(fixable)
            ],
        }, indent=2)

        try:
            result = self.llm.chat_json(FIX_PROMPT, user_message, temperature=0.1)
            data = result.get("data", {})
            fixes = data.get("fixes", [])

            for fix in fixes:
                idx = fix.get("finding_index", 0)
                if 0 <= idx < len(fixable):
                    fix["file"] = fixable[idx].get("file")
                    fix["line"] = fixable[idx].get("line")
                    fix["category"] = fixable[idx].get("category")
                    fix["severity"] = fixable[idx].get("severity")

            return fixes
        except Exception:
            logger.exception("Auto-fix generation failed")
            return []
