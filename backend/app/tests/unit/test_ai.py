import json
import pytest
from unittest.mock import MagicMock, patch

from app.ai.analyzer import (
    compare_findings,
    deduplicate_findings,
    get_categories,
    score_findings,
    sort_findings,
)
from app.ai.prompts import PROMPT_MAP, FINDING_SCHEMA
from app.ai.reviewer import AgentReviewer


class TestDeduplicateFindings:
    def test_removes_exact_duplicates(self):
        findings = [
            {"file": "a.py", "line": 10, "category": "sql-injection", "severity": "critical"},
            {"file": "a.py", "line": 10, "category": "sql-injection", "severity": "critical"},
        ]
        result = deduplicate_findings(findings)
        assert len(result) == 1

    def test_keeps_different_files(self):
        findings = [
            {"file": "a.py", "line": 10, "category": "sql-injection"},
            {"file": "b.py", "line": 10, "category": "sql-injection"},
        ]
        result = deduplicate_findings(findings)
        assert len(result) == 2

    def test_keeps_different_lines(self):
        findings = [
            {"file": "a.py", "line": 10, "category": "xss"},
            {"file": "a.py", "line": 20, "category": "xss"},
        ]
        result = deduplicate_findings(findings)
        assert len(result) == 2

    def test_keeps_different_categories(self):
        findings = [
            {"file": "a.py", "line": 10, "category": "xss"},
            {"file": "a.py", "line": 10, "category": "sql-injection"},
        ]
        result = deduplicate_findings(findings)
        assert len(result) == 2

    def test_case_insensitive_category(self):
        findings = [
            {"file": "a.py", "line": 10, "category": "SQL-Injection"},
            {"file": "a.py", "line": 10, "category": "sql-injection"},
        ]
        result = deduplicate_findings(findings)
        assert len(result) == 1

    def test_empty_list(self):
        assert deduplicate_findings([]) == []

    def test_preserves_order(self):
        findings = [
            {"file": "c.py", "line": 1, "category": "a"},
            {"file": "a.py", "line": 1, "category": "b"},
            {"file": "b.py", "line": 1, "category": "c"},
        ]
        result = deduplicate_findings(findings)
        assert [f["file"] for f in result] == ["c.py", "a.py", "b.py"]


class TestScoreFindings:
    def test_perfect_score_no_findings(self):
        assert score_findings([]) == 100.0

    def test_critical_deducts_30(self):
        findings = [{"severity": "critical"}]
        assert score_findings(findings) == 70.0

    def test_warning_deducts_10(self):
        findings = [{"severity": "warning"}]
        assert score_findings(findings) == 90.0

    def test_info_deducts_2(self):
        findings = [{"severity": "info"}]
        assert score_findings(findings) == 98.0

    def test_score_floors_at_zero(self):
        findings = [{"severity": "critical"}] * 10
        assert score_findings(findings) == 0.0

    def test_mixed_severities(self):
        findings = [
            {"severity": "critical"},
            {"severity": "warning"},
            {"severity": "info"},
        ]
        assert score_findings(findings) == 58.0

    def test_unknown_severity_treated_as_info(self):
        findings = [{"severity": "unknown"}]
        assert score_findings(findings) == 100.0


class TestSortFindings:
    def test_sorts_by_severity(self):
        findings = [
            {"severity": "info", "file": "a.py", "line": 1},
            {"severity": "critical", "file": "a.py", "line": 1},
            {"severity": "warning", "file": "a.py", "line": 1},
        ]
        result = sort_findings(findings)
        assert [f["severity"] for f in result] == ["critical", "warning", "info"]

    def test_sorts_by_file_within_severity(self):
        findings = [
            {"severity": "warning", "file": "b.py", "line": 1},
            {"severity": "warning", "file": "a.py", "line": 1},
        ]
        result = sort_findings(findings)
        assert [f["file"] for f in result] == ["a.py", "b.py"]

    def test_sorts_by_line_within_file(self):
        findings = [
            {"severity": "warning", "file": "a.py", "line": 20},
            {"severity": "warning", "file": "a.py", "line": 5},
        ]
        result = sort_findings(findings)
        assert [f["line"] for f in result] == [5, 20]

    def test_handles_none_line(self):
        findings = [
            {"severity": "warning", "file": "a.py", "line": None},
            {"severity": "warning", "file": "a.py", "line": 5},
        ]
        result = sort_findings(findings)
        assert result[0]["line"] is None or result[0]["line"] == 0


class TestGetCategories:
    def test_returns_sorted_unique(self):
        findings = [
            {"category": "xss"},
            {"category": "sql-injection"},
            {"category": "xss"},
        ]
        assert get_categories(findings) == ["sql-injection", "xss"]

    def test_empty_findings(self):
        assert get_categories([]) == []

    def test_missing_category_defaults_to_unknown(self):
        findings = [{}]
        assert get_categories(findings) == ["unknown"]


class TestCompareFindings:
    def test_basic_comparison(self):
        agent = [
            {"file": "a.py", "category": "xss", "severity": "critical"},
            {"file": "b.py", "category": "sql-injection", "severity": "warning"},
        ]
        baseline = [
            {"file": "a.py", "category": "xss", "severity": "critical"},
        ]
        result = compare_findings(agent, baseline)
        assert result["agent_findings_count"] == 2
        assert result["baseline_findings_count"] == 1
        assert result["unique_to_agents"] == 1
        assert result["unique_to_baseline"] == 0

    def test_empty_comparison(self):
        result = compare_findings([], [])
        assert result["agent_findings_count"] == 0
        assert result["baseline_findings_count"] == 0
        assert result["agent_score"] == 100.0
        assert result["baseline_score"] == 100.0


class TestPromptMap:
    def test_all_agent_types_have_prompts(self):
        expected = {"logic", "security", "performance", "quality", "synthesis", "baseline"}
        assert set(PROMPT_MAP.keys()) == expected

    def test_prompts_contain_finding_schema(self):
        for agent_type in ["logic", "security", "performance", "quality", "baseline"]:
            assert "findings" in PROMPT_MAP[agent_type]

    def test_prompts_are_non_empty(self):
        for prompt in PROMPT_MAP.values():
            assert len(prompt) > 100


class TestAgentReviewer:
    def _make_reviewer(self, response_data):
        mock_llm = MagicMock()
        mock_llm.chat_json.return_value = {
            "data": response_data,
            "tokens": {"input": 100, "output": 50},
            "duration_seconds": 1.5,
        }
        return AgentReviewer(mock_llm), mock_llm

    def test_specialist_returns_findings(self):
        reviewer, mock = self._make_reviewer({
            "findings": [
                {"file": "a.py", "line": 10, "severity": "critical", "category": "sql-injection", "message": "SQL injection"}
            ],
            "summary": "Found SQL injection",
        })
        result = reviewer.run_specialist_agent("security", "diff content")
        assert len(result["findings"]) == 1
        assert result["findings"][0]["agent"] == "security"
        assert result["summary"] == "Found SQL injection"
        assert result["tokens"]["input"] == 100

    def test_specialist_with_static_findings(self):
        reviewer, mock = self._make_reviewer({"findings": [], "summary": "Clean"})
        static = [{"file": "a.py", "category": "eval", "severity": "critical"}]
        reviewer.run_specialist_agent("security", "diff", static)
        call_args = mock.chat_json.call_args
        assert "Static Analysis" in call_args[0][1]

    def test_specialist_uses_custom_prompt(self):
        reviewer, mock = self._make_reviewer({"findings": [], "summary": ""})
        reviewer.run_specialist_agent("logic", "diff", custom_prompt="Custom system prompt")
        call_args = mock.chat_json.call_args
        assert call_args[0][0] == "Custom system prompt"

    def test_specialist_uses_custom_temperature(self):
        reviewer, mock = self._make_reviewer({"findings": [], "summary": ""})
        reviewer.run_specialist_agent("logic", "diff", temperature=0.8)
        call_args = mock.chat_json.call_args
        assert call_args[1]["temperature"] == 0.8

    def test_synthesis_returns_score(self):
        reviewer, mock = self._make_reviewer({
            "findings": [],
            "summary": "All good",
            "overall_score": 95,
            "agent_confidence": {"logic": "high", "security": "high", "performance": "medium", "quality": "high"},
        })
        result = reviewer.run_synthesis_agent(
            {"logic": {"findings": [], "summary": ""}},
            "diff summary",
        )
        assert result["overall_score"] == 95
        assert result["agent_confidence"]["logic"] == "high"

    def test_baseline_sets_agent_field(self):
        reviewer, mock = self._make_reviewer({
            "findings": [{"file": "a.py", "line": 1, "severity": "info", "category": "naming", "message": "Poor name"}],
            "summary": "Minor issue",
        })
        result = reviewer.run_baseline("diff")
        assert result["findings"][0]["agent"] == "baseline"
