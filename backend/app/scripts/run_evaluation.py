"""
Evaluation script: runs both baseline (single-prompt) and multi-agent pipeline
on curated sample diffs and compares results.

Usage:
    cd backend
    python -m app.scripts.run_evaluation
"""

import json
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from app.ai.analyzer import compare_findings, deduplicate_findings, score_findings, sort_findings
from app.ai.client import LLMClient
from app.ai.reviewer import AgentReviewer
from app.validators.python_validator import run_python_checks
from app.validators.security_validator import run_security_checks

SAMPLE_DIR = Path(__file__).resolve().parents[1] / "tests" / "fixtures" / "sample_diffs"


def run_multi_agent(reviewer: AgentReviewer, diff_content: str) -> dict:
    start = time.time()
    total_tokens = {"input": 0, "output": 0}

    static_findings = run_security_checks(diff_content) + run_python_checks(diff_content)

    specialist_results = {}
    for agent_type in ["logic", "security", "performance", "quality"]:
        relevant_static = [f for f in static_findings if _is_relevant(f, agent_type)]
        result = reviewer.run_specialist_agent(agent_type, diff_content, relevant_static if relevant_static else None)
        specialist_results[agent_type] = result
        total_tokens["input"] += result.get("tokens", {}).get("input", 0)
        total_tokens["output"] += result.get("tokens", {}).get("output", 0)

    synthesis = reviewer.run_synthesis_agent(specialist_results, diff_content[:3000])
    total_tokens["input"] += synthesis.get("tokens", {}).get("input", 0)
    total_tokens["output"] += synthesis.get("tokens", {}).get("output", 0)

    findings = sort_findings(synthesis.get("findings", []))
    elapsed = time.time() - start

    return {
        "findings": findings,
        "score": synthesis.get("overall_score", score_findings(findings)),
        "summary": synthesis.get("summary", ""),
        "tokens": total_tokens,
        "duration_seconds": round(elapsed, 2),
    }


def run_baseline(reviewer: AgentReviewer, diff_content: str) -> dict:
    start = time.time()
    result = reviewer.run_baseline(diff_content)
    elapsed = time.time() - start

    findings = sort_findings(result.get("findings", []))
    return {
        "findings": findings,
        "score": score_findings(findings),
        "summary": result.get("summary", ""),
        "tokens": result.get("tokens", {}),
        "duration_seconds": round(elapsed, 2),
    }


def _is_relevant(finding, agent_type):
    cat = finding.get("category", "").lower()
    mapping = {
        "security": {
            "hardcoded-api-key", "hardcoded-secret", "aws-access-key", "github-token", "openai-key",
            "dangerous-eval", "dangerous-exec", "command-injection", "shell-injection",
            "insecure-deserialization", "xss-risk",
        },
        "quality": {"bare-except", "wildcard-import", "todo-comment", "print-statement"},
        "logic": {"mutable-default", "assert-in-prod"},
        "performance": set(),
    }
    return cat in mapping.get(agent_type, set())


def main():
    llm = LLMClient()
    reviewer = AgentReviewer(llm)

    diff_files = sorted(SAMPLE_DIR.glob("*.diff"))
    if not diff_files:
        print("No sample diffs found!")
        return

    results = []
    print(f"\nRunning evaluation on {len(diff_files)} sample diffs...\n")
    print(f"{'Diff':<20} {'Agent Findings':<16} {'Baseline Findings':<18} {'Agent Score':<12} {'Baseline Score':<14} {'Agent Time':<12} {'Baseline Time'}")
    print("-" * 110)

    for diff_path in diff_files:
        name = diff_path.stem
        diff_content = diff_path.read_text()

        print(f"  {name:<18} ", end="", flush=True)

        agent_result = run_multi_agent(reviewer, diff_content)
        baseline_result = run_baseline(reviewer, diff_content)

        comparison = compare_findings(agent_result["findings"], baseline_result["findings"])

        row = {
            "name": name,
            "agent": {
                "findings_count": len(agent_result["findings"]),
                "score": agent_result["score"],
                "duration": agent_result["duration_seconds"],
                "tokens": agent_result["tokens"],
                "critical": len([f for f in agent_result["findings"] if f.get("severity") == "critical"]),
            },
            "baseline": {
                "findings_count": len(baseline_result["findings"]),
                "score": baseline_result["score"],
                "duration": baseline_result["duration_seconds"],
                "tokens": baseline_result["tokens"],
                "critical": len([f for f in baseline_result["findings"] if f.get("severity") == "critical"]),
            },
            "comparison": comparison,
        }
        results.append(row)

        a, b = row['agent'], row['baseline']
        print(f"{a['findings_count']:<16} {b['findings_count']:<18} {a['score']:<12.0f} {b['score']:<14.0f} {a['duration']:<12.1f} {b['duration']:.1f}s")

    print("\n" + "=" * 110)
    print("\nSUMMARY")
    print("-" * 50)

    total_agent_findings = sum(r["agent"]["findings_count"] for r in results)
    total_baseline_findings = sum(r["baseline"]["findings_count"] for r in results)
    avg_agent_score = sum(r["agent"]["score"] for r in results) / len(results)
    avg_baseline_score = sum(r["baseline"]["score"] for r in results) / len(results)
    total_agent_time = sum(r["agent"]["duration"] for r in results)
    total_baseline_time = sum(r["baseline"]["duration"] for r in results)
    total_agent_critical = sum(r["agent"]["critical"] for r in results)
    total_baseline_critical = sum(r["baseline"]["critical"] for r in results)

    print(f"Total findings:     Agent={total_agent_findings}  Baseline={total_baseline_findings}")
    print(f"Critical findings:  Agent={total_agent_critical}  Baseline={total_baseline_critical}")
    print(f"Avg quality score:  Agent={avg_agent_score:.1f}  Baseline={avg_baseline_score:.1f}")
    print(f"Total time:         Agent={total_agent_time:.1f}s  Baseline={total_baseline_time:.1f}s")
    print()

    output_path = SAMPLE_DIR / "evaluation_results.json"
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Full results saved to: {output_path}")


if __name__ == "__main__":
    main()
