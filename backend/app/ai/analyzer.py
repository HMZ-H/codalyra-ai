def deduplicate_findings(findings: list[dict]) -> list[dict]:
    seen = set()
    unique = []
    for f in findings:
        key = (f.get("file", ""), f.get("line"), f.get("category", "").lower())
        if key in seen:
            continue
        seen.add(key)
        unique.append(f)
    return unique


def score_findings(findings: list[dict]) -> float:
    score = 100.0
    for f in findings:
        severity = f.get("severity", "info")
        if severity == "critical":
            score -= 30
        elif severity == "warning":
            score -= 10
        elif severity == "info":
            score -= 2
    return max(0.0, min(100.0, score))


def sort_findings(findings: list[dict]) -> list[dict]:
    severity_order = {"critical": 0, "warning": 1, "info": 2}
    return sorted(findings, key=lambda f: (severity_order.get(f.get("severity", "info"), 3), f.get("file", ""), f.get("line") or 0))


def get_categories(findings: list[dict]) -> list[str]:
    return sorted(set(f.get("category", "unknown") for f in findings))


def compare_findings(agent_findings: list[dict], baseline_findings: list[dict]) -> dict:
    def finding_key(f):
        return (f.get("file", ""), f.get("category", "").lower())

    agent_keys = {finding_key(f) for f in agent_findings}
    baseline_keys = {finding_key(f) for f in baseline_findings}

    return {
        "baseline_findings_count": len(baseline_findings),
        "agent_findings_count": len(agent_findings),
        "baseline_score": score_findings(baseline_findings),
        "agent_score": score_findings(agent_findings),
        "unique_to_agents": len(agent_keys - baseline_keys),
        "unique_to_baseline": len(baseline_keys - agent_keys),
        "categories_covered_agents": get_categories(agent_findings),
        "categories_covered_baseline": get_categories(baseline_findings),
    }
