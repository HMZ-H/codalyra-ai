import json
import uuid
import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timezone

from app.database.models.user import User
from app.database.models.project import Project
from app.database.models.review import Review
from app.database.models.run import Run
from app.database.models.task import Task
from app.database.models.agent_config import AgentConfig
from app.ai.analyzer import deduplicate_findings, score_findings, sort_findings
from app.validators.security_validator import run_security_checks
from app.validators.python_validator import run_python_checks
from app.validators.javascript_validator import run_javascript_checks
from app.validators.golang_validator import run_golang_checks
from app.validators.detector import detect_languages


SAMPLE_PYTHON_DIFF = """diff --git a/app/main.py b/app/main.py
--- a/app/main.py
+++ b/app/main.py
@@ -1,5 +1,10 @@
+import os
+
+API_KEY = "sk-proj-abc123def456ghi789jkl012mno345pqr"
+
 def get_users(db):
-    pass
+    query = f"SELECT * FROM users WHERE name = '{name}'"
+    result = eval(query)
+    print(result)
+    return result
"""

SAMPLE_JS_DIFF = """diff --git a/app.js b/app.js
--- a/app.js
+++ b/app.js
@@ -1,3 +1,8 @@
+var x = 5;
+document.innerHTML = userInput;
+eval(data);
+console.log("debug");
+if (a == b) {}
"""

SAMPLE_GO_DIFF = """diff --git a/main.go b/main.go
--- a/main.go
+++ b/main.go
@@ -1,3 +1,6 @@
+fmt.Println("debug")
+panic("error")
+password := "secret12345678"
"""

SAMPLE_MULTI_LANG_DIFF = SAMPLE_PYTHON_DIFF + "\n" + SAMPLE_JS_DIFF


class TestEndToEndValidatorPipeline:
    def test_python_diff_detects_issues(self):
        security = run_security_checks(SAMPLE_PYTHON_DIFF)
        python = run_python_checks(SAMPLE_PYTHON_DIFF)

        all_findings = security + python
        categories = [f["category"] for f in all_findings]

        assert "dangerous-eval" in categories
        assert "print-statement" in categories
        assert any("key" in c or "secret" in c for c in categories)

    def test_js_diff_detects_issues(self):
        findings = run_javascript_checks(SAMPLE_JS_DIFF)
        categories = [f["category"] for f in findings]

        assert "dangerous-eval" in categories
        assert "var-usage" in categories
        assert "console-log" in categories
        assert "loose-equality" in categories

    def test_go_diff_detects_issues(self):
        findings = run_golang_checks(SAMPLE_GO_DIFF)
        categories = [f["category"] for f in findings]

        assert "fmt-print" in categories
        assert "panic-usage" in categories
        assert "hardcoded-secret" in categories

    def test_multi_language_detection(self):
        langs = detect_languages(SAMPLE_MULTI_LANG_DIFF)
        assert "python" in langs
        assert "javascript" in langs

    def test_full_pipeline_dedup_and_score(self):
        security = run_security_checks(SAMPLE_PYTHON_DIFF)
        python = run_python_checks(SAMPLE_PYTHON_DIFF)

        all_findings = security + python
        deduped = deduplicate_findings(all_findings)
        sorted_findings = sort_findings(deduped)
        score = score_findings(sorted_findings)

        assert len(deduped) <= len(all_findings)
        assert 0 <= score <= 100
        if any(f["severity"] == "critical" for f in sorted_findings):
            assert sorted_findings[0]["severity"] == "critical"

    def test_language_aware_routing(self):
        langs = detect_languages(SAMPLE_MULTI_LANG_DIFF)
        all_findings = []
        all_findings.extend(run_security_checks(SAMPLE_MULTI_LANG_DIFF))

        if "python" in langs:
            all_findings.extend(run_python_checks(SAMPLE_MULTI_LANG_DIFF))
        if "javascript" in langs:
            all_findings.extend(run_javascript_checks(SAMPLE_MULTI_LANG_DIFF))

        agents = set(f.get("agent", "") for f in all_findings)
        assert "static-security" in agents or any("security" in a for a in agents)
        py_findings = [f for f in all_findings if f.get("agent") == "static-python"]
        js_findings = [f for f in all_findings if f.get("agent") == "static-javascript"]
        assert len(py_findings) > 0
        assert len(js_findings) > 0


class TestReviewModelFlow:
    def test_create_review_with_runs(self, db_session):
        from bcrypt import hashpw, gensalt
        user = User(
            email="pipe@test.com",
            username="pipeuser",
            hashed_password=hashpw(b"test123", gensalt()).decode(),
        )
        db_session.add(user)
        db_session.flush()

        project = Project(name="Pipeline Test", owner_id=user.id)
        db_session.add(project)
        db_session.flush()

        task = Task(
            project_id=project.id,
            created_by_id=user.id,
            title="Review: Test PR",
            description="Automated review",
            status="active",
        )
        db_session.add(task)
        db_session.flush()

        review = Review(
            project_id=project.id,
            created_by_id=user.id,
            pr_title="Test PR",
            diff_content=SAMPLE_PYTHON_DIFF,
            status="pending",
        )
        db_session.add(review)
        db_session.flush()

        agent_names = ["logic-agent", "security-agent", "performance-agent", "quality-agent", "synthesis-agent", "baseline-agent"]
        runs = []
        for name in agent_names:
            run = Run(
                task_id=task.id,
                review_id=review.id,
                agent_name=name,
                status="pending",
            )
            db_session.add(run)
            runs.append(run)

        db_session.commit()

        assert len(runs) == 6
        assert review.status == "pending"
        assert all(r.status == "pending" for r in runs)

    def test_agent_config_disables_agent(self, db_session):
        from bcrypt import hashpw, gensalt
        user = User(
            email="cfg@test.com",
            username="cfguser",
            hashed_password=hashpw(b"test123", gensalt()).decode(),
        )
        db_session.add(user)
        db_session.flush()

        project = Project(name="Config Test", owner_id=user.id)
        db_session.add(project)
        db_session.flush()

        cfg = AgentConfig(
            project_id=project.id,
            agent_type="quality",
            is_enabled=False,
        )
        db_session.add(cfg)
        db_session.commit()

        disabled = db_session.query(AgentConfig).filter(
            AgentConfig.project_id == project.id,
            AgentConfig.is_enabled == False,
        ).all()

        assert len(disabled) == 1
        assert disabled[0].agent_type == "quality"

    def test_agent_config_custom_prompt(self, db_session):
        from bcrypt import hashpw, gensalt
        user = User(
            email="prompt@test.com",
            username="promptuser",
            hashed_password=hashpw(b"test123", gensalt()).decode(),
        )
        db_session.add(user)
        db_session.flush()

        project = Project(name="Prompt Test", owner_id=user.id)
        db_session.add(project)
        db_session.flush()

        cfg = AgentConfig(
            project_id=project.id,
            agent_type="security",
            custom_prompt="Focus on OWASP Top 10 for Python Flask apps",
            temperature=0.3,
            provider="openai",
            model_name="gpt-4o",
        )
        db_session.add(cfg)
        db_session.commit()

        loaded = db_session.query(AgentConfig).filter(
            AgentConfig.project_id == project.id,
            AgentConfig.agent_type == "security",
        ).first()

        assert loaded.custom_prompt == "Focus on OWASP Top 10 for Python Flask apps"
        assert loaded.temperature == 0.3
        assert loaded.provider == "openai"
        assert loaded.model_name == "gpt-4o"
