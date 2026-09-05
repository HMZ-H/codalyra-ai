import json
import logging

from app.ai.client import LLMClient
from app.ai.providers import LLMProvider
from app.ai.prompts import PROMPT_MAP

logger = logging.getLogger(__name__)


class AgentReviewer:
    def __init__(self, llm_client: LLMClient | LLMProvider):
        self.llm = llm_client

    def run_specialist_agent(self, agent_type: str, diff_context: str, static_findings: list | None = None, custom_prompt: str | None = None, temperature: float = 0.2) -> dict:
        system_prompt = custom_prompt if custom_prompt else PROMPT_MAP[agent_type]

        user_message = f"Code diff to review:\n\n{diff_context}"

        if static_findings:
            user_message += (
                "\n\n--- Static Analysis Pre-scan Results ---\n"
                "The following issues were detected by static analysis tools before your review. "
                "You may confirm, refine, or dismiss these. Do not simply repeat them — add value.\n\n"
                + json.dumps(static_findings, indent=2)
            )

        result = self.llm.chat_json(system_prompt, user_message, temperature=temperature)

        data = result.get("data", {})
        findings = data.get("findings", [])
        for f in findings:
            f.setdefault("agent", agent_type)

        return {
            "findings": findings,
            "summary": data.get("summary", ""),
            "tokens": result.get("tokens", {}),
            "duration_seconds": result.get("duration_seconds", 0),
        }

    def run_synthesis_agent(self, specialist_results: dict[str, dict], diff_summary: str) -> dict:
        system_prompt = PROMPT_MAP["synthesis"]

        user_message = json.dumps({
            "specialist_findings": {
                agent: {
                    "findings": r.get("findings", []),
                    "summary": r.get("summary", ""),
                }
                for agent, r in specialist_results.items()
            },
            "diff_summary": diff_summary[:3000],
        }, indent=2)

        result = self.llm.chat_json(system_prompt, user_message)

        data = result.get("data", {})
        return {
            "findings": data.get("findings", []),
            "summary": data.get("summary", ""),
            "overall_score": data.get("overall_score"),
            "agent_confidence": data.get("agent_confidence", {}),
            "tokens": result.get("tokens", {}),
            "duration_seconds": result.get("duration_seconds", 0),
        }

    def run_baseline(self, diff_context: str) -> dict:
        system_prompt = PROMPT_MAP["baseline"]
        user_message = f"Code diff to review:\n\n{diff_context}"

        result = self.llm.chat_json(system_prompt, user_message)

        data = result.get("data", {})
        findings = data.get("findings", [])
        for f in findings:
            f.setdefault("agent", "baseline")

        return {
            "findings": findings,
            "summary": data.get("summary", ""),
            "tokens": result.get("tokens", {}),
            "duration_seconds": result.get("duration_seconds", 0),
        }
