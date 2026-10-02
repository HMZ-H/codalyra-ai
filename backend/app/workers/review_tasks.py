import json
import logging
from datetime import datetime, timezone

from app.ai.analyzer import deduplicate_findings, score_findings, sort_findings
from app.ai.client import LLMClient
from app.ai.providers import create_provider
from app.ai.reviewer import AgentReviewer
from app.database.models.agent_config import AgentConfig
from app.database.models.custom_rule import CustomRule
from app.database.models.evaluation import Evaluation
from app.database.models.review import Review
from app.database.models.run import Run
from app.database.models.trajectory import Trajectory
from app.database.session import SessionLocal
from app.validators.custom_rules import run_custom_rules
from app.validators.detector import detect_languages
from app.validators.golang_validator import run_golang_checks
from app.validators.javascript_validator import run_javascript_checks
from app.validators.python_validator import run_python_checks
from app.validators.security_validator import run_security_checks
from app.workers.celery_app import celery_app

logger = logging.getLogger(__name__)


def _get_user_api_key(db, review_id: str, provider: str = "gemini") -> str | None:
    review = db.get(Review, review_id)
    if not review:
        return None
    from app.database.models.user import User
    user = db.get(User, review.created_by_id)
    if not user:
        return None

    key_fields = {
        "gemini": "gemini_api_key_encrypted",
        "openai": "openai_api_key_encrypted",
        "anthropic": "anthropic_api_key_encrypted",
    }
    field = key_fields.get(provider, "gemini_api_key_encrypted")
    encrypted = getattr(user, field, None)
    if not encrypted:
        return None
    try:
        from app.core.encryption import decrypt_value
        return decrypt_value(encrypted)
    except Exception:
        return None


def _record_trajectory(db, run_id, seq, action_type, action_input, action_output, duration_ms=0):
    trajectory = Trajectory(
        run_id=run_id,
        sequence_number=seq,
        action_type=action_type,
        action_input=action_input[:2000] if action_input else "",
        action_output=action_output[:5000] if action_output else "",
        timestamp=datetime.now(timezone.utc),
        duration_ms=duration_ms,
    )
    db.add(trajectory)
    db.flush()


@celery_app.task(bind=True, max_retries=2)
def run_specialist_review(self, run_id: str, review_id: str, agent_type: str, diff_content: str):
    db = SessionLocal()
    try:
        run = db.get(Run, run_id)
        if not run:
            logger.error(f"Run {run_id} not found")
            return

        run.status = "running"
        run.started_at = datetime.now(timezone.utc)
        db.commit()

        languages = detect_languages(diff_content)
        static_findings = []
        static_findings.extend(run_security_checks(diff_content))
        if "python" in languages:
            static_findings.extend(run_python_checks(diff_content))
        if "javascript" in languages or "typescript" in languages:
            static_findings.extend(run_javascript_checks(diff_content))
        if "go" in languages:
            static_findings.extend(run_golang_checks(diff_content))

        review = db.get(Review, review_id)
        if review:
            custom_rules_list = db.query(CustomRule).filter(
                CustomRule.project_id == review.project_id,
                CustomRule.is_enabled == True,
            ).all()
            if custom_rules_list:
                rule_dicts = [
                    {"name": r.name, "pattern": r.pattern, "severity": r.severity,
                     "category": r.category, "message": r.message, "suggestion": r.suggestion,
                     "file_pattern": r.file_pattern, "is_enabled": r.is_enabled}
                    for r in custom_rules_list
                ]
                static_findings.extend(run_custom_rules(diff_content, rule_dicts))

        relevant_static = [f for f in static_findings if _is_relevant_to_agent(f, agent_type)]

        lang_str = ', '.join(languages) or 'unknown'
        _record_trajectory(
            db, run.id, 1, "static_analysis",
            f"Running static checks for {agent_type} (langs: {lang_str})",
            json.dumps({"findings_count": len(relevant_static)}),
        )

        agent_cfg = None
        if review:
            agent_cfg = db.query(AgentConfig).filter(
                AgentConfig.project_id == review.project_id,
                AgentConfig.agent_type == agent_type,
            ).first()

        provider_name = (agent_cfg.provider if agent_cfg and agent_cfg.provider else "gemini")
        model_name = (agent_cfg.model_name if agent_cfg and agent_cfg.model_name else None)
        user_key = _get_user_api_key(db, review_id, provider=provider_name)

        if provider_name != "gemini" and user_key:
            llm = create_provider(provider_name, api_key=user_key, model=model_name)
        else:
            gemini_key = _get_user_api_key(db, review_id, provider="gemini")
            llm = LLMClient(api_key=gemini_key)

        reviewer = AgentReviewer(llm)
        result = reviewer.run_specialist_agent(
            agent_type, diff_content,
            relevant_static if relevant_static else None,
            custom_prompt=agent_cfg.custom_prompt if agent_cfg else None,
            temperature=agent_cfg.temperature if agent_cfg else 0.2,
        )

        _record_trajectory(
            db, run.id, 2, "llm_review",
            f"Running {agent_type} agent via {provider_name}",
            json.dumps({"findings_count": len(result.get("findings", [])), "summary": result.get("summary", "")[:500]}),
            duration_ms=int(result.get("duration_seconds", 0) * 1000),
        )

        all_findings = relevant_static + result.get("findings", [])
        all_findings = deduplicate_findings(all_findings)
        all_findings = sort_findings(all_findings)

        _record_trajectory(db, run.id, 3, "merge_findings", "Merging static + LLM findings", json.dumps({"total_findings": len(all_findings)}))

        evaluation = Evaluation(
            run_id=run.id,
            tests_passed=len([f for f in all_findings if f.get("severity") == "info"]),
            tests_total=len(all_findings),
            score=score_findings(all_findings),
            is_correct=len([f for f in all_findings if f.get("severity") == "critical"]) == 0,
            feedback=json.dumps({"findings": all_findings, "summary": result.get("summary", "")}),
            evaluation_method="agent_review",
            evaluated_at=datetime.now(timezone.utc),
            metadata_={"tokens": result.get("tokens", {}), "agent_type": agent_type},
        )
        db.add(evaluation)

        run.status = "completed"
        run.completed_at = datetime.now(timezone.utc)
        run.duration_seconds = (run.completed_at - run.started_at).total_seconds()
        db.commit()

        check_and_trigger_synthesis.delay(review_id)
        return {"run_id": run_id, "findings_count": len(all_findings)}

    except Exception as exc:
        logger.exception(f"Specialist review failed for run {run_id}")
        try:
            db.rollback()
            run = db.get(Run, run_id)
            if run:
                run.status = "failed"
                run.error_message = str(exc)[:500]
                run.completed_at = datetime.now(timezone.utc)
                db.commit()
        except Exception:
            db.rollback()
        raise self.retry(exc=exc, countdown=15)
    finally:
        db.close()


@celery_app.task
def check_and_trigger_synthesis(review_id: str):
    db = SessionLocal()
    try:
        specialist_runs = db.query(Run).filter(
            Run.review_id == review_id,
            Run.agent_name.in_(["logic-agent", "security-agent", "performance-agent", "quality-agent"]),
        ).all()

        if all(r.status in ("completed", "skipped") for r in specialist_runs):
            synthesis_run = db.query(Run).filter(
                Run.review_id == review_id,
                Run.agent_name == "synthesis-agent",
            ).first()
            if synthesis_run and synthesis_run.status == "pending":
                run_synthesis_review.delay(str(synthesis_run.id), review_id)
        elif any(r.status == "failed" for r in specialist_runs):
            review = db.get(Review, review_id)
            if review:
                review.status = "failed"
                db.commit()
    finally:
        db.close()


@celery_app.task(bind=True, max_retries=2)
def run_synthesis_review(self, run_id: str, review_id: str):
    db = SessionLocal()
    try:
        run = db.get(Run, run_id)
        review = db.get(Review, review_id)
        if not run or not review:
            return

        run.status = "running"
        run.started_at = datetime.now(timezone.utc)
        review.status = "running"
        db.commit()

        specialist_runs = db.query(Run).filter(
            Run.review_id == review_id,
            Run.agent_name.in_(["logic-agent", "security-agent", "performance-agent", "quality-agent"]),
        ).all()

        specialist_results = {}
        for sr in specialist_runs:
            agent_type = sr.agent_name.replace("-agent", "")
            if sr.evaluation and sr.evaluation.feedback:
                try:
                    feedback = json.loads(sr.evaluation.feedback) if isinstance(sr.evaluation.feedback, str) else sr.evaluation.feedback
                    specialist_results[agent_type] = feedback
                except (json.JSONDecodeError, TypeError):
                    specialist_results[agent_type] = {"findings": [], "summary": ""}
            else:
                specialist_results[agent_type] = {"findings": [], "summary": ""}

        _record_trajectory(db, run.id, 1, "collect_findings", "Collecting specialist findings", json.dumps({k: len(v.get("findings", [])) for k, v in specialist_results.items()}))

        user_key = _get_user_api_key(db, review_id)
        llm = LLMClient(api_key=user_key)
        reviewer = AgentReviewer(llm)
        diff_summary = review.diff_content[:3000]
        result = reviewer.run_synthesis_agent(specialist_results, diff_summary)

        _record_trajectory(
            db, run.id, 2, "synthesis",
            "Running synthesis agent",
            json.dumps({"findings_count": len(result.get("findings", [])), "overall_score": result.get("overall_score")}),
            duration_ms=int(result.get("duration_seconds", 0) * 1000),
        )

        synthesis_findings = sort_findings(result.get("findings", []))

        evaluation = Evaluation(
            run_id=run.id,
            tests_passed=len(synthesis_findings),
            tests_total=len(synthesis_findings),
            score=result.get("overall_score", 0),
            is_correct=len([f for f in synthesis_findings if f.get("severity") == "critical"]) == 0,
            feedback=json.dumps({"findings": synthesis_findings, "summary": result.get("summary", "")}),
            evaluation_method="synthesis",
            evaluated_at=datetime.now(timezone.utc),
            metadata_={"tokens": result.get("tokens", {}), "agent_confidence": result.get("agent_confidence", {})},
        )
        db.add(evaluation)

        review.overall_score = result.get("overall_score")
        review.summary = result.get("summary", "")
        review.findings_count = len(synthesis_findings)
        review.status = "completed"
        review.metadata_ = {
            "synthesis_findings": synthesis_findings,
            "agent_confidence": result.get("agent_confidence", {}),
        }

        run.status = "completed"
        run.completed_at = datetime.now(timezone.utc)
        run.duration_seconds = (run.completed_at - run.started_at).total_seconds()
        db.commit()

        try:
            from app.database.models.project import Project
            from app.services.notification_service import notify_review_complete
            project = db.get(Project, review.project_id)
            notify_review_complete(
                {
                    "review_id": review_id,
                    "pr_title": review.pr_title,
                    "overall_score": result.get("overall_score"),
                    "summary": result.get("summary", ""),
                    "findings": synthesis_findings,
                },
                slack_url=getattr(project, "slack_webhook_url", None),
                discord_url=getattr(project, "discord_webhook_url", None),
            )
        except Exception:
            logger.warning("Notification dispatch failed", exc_info=True)

        return {"review_id": review_id, "overall_score": result.get("overall_score"), "findings_count": len(synthesis_findings)}

    except Exception as exc:
        logger.exception(f"Synthesis failed for review {review_id}")
        try:
            db.rollback()
            r = db.get(Run, run_id)
            if r:
                r.status = "failed"
                r.error_message = str(exc)[:500]
                db.commit()
        except Exception:
            db.rollback()
        raise self.retry(exc=exc, countdown=15)
    finally:
        db.close()


@celery_app.task(bind=True, max_retries=2)
def run_baseline_review(self, run_id: str, review_id: str, diff_content: str):
    db = SessionLocal()
    try:
        run = db.get(Run, run_id)
        review = db.get(Review, review_id)
        if not run or not review:
            return

        run.status = "running"
        run.started_at = datetime.now(timezone.utc)
        db.commit()

        _record_trajectory(db, run.id, 1, "baseline_start", "Running single-prompt baseline review", "")

        user_key = _get_user_api_key(db, review_id)
        llm = LLMClient(api_key=user_key)
        reviewer = AgentReviewer(llm)
        result = reviewer.run_baseline(diff_content)

        findings = sort_findings(result.get("findings", []))

        _record_trajectory(
            db, run.id, 2, "baseline_complete",
            "Baseline review completed",
            json.dumps({"findings_count": len(findings)}),
            duration_ms=int(result.get("duration_seconds", 0) * 1000),
        )

        evaluation = Evaluation(
            run_id=run.id,
            tests_passed=len(findings),
            tests_total=len(findings),
            score=score_findings(findings),
            is_correct=len([f for f in findings if f.get("severity") == "critical"]) == 0,
            feedback=json.dumps({"findings": findings, "summary": result.get("summary", "")}),
            evaluation_method="baseline",
            evaluated_at=datetime.now(timezone.utc),
            metadata_={"tokens": result.get("tokens", {})},
        )
        db.add(evaluation)

        review.baseline_summary = result.get("summary", "")
        review.baseline_score = score_findings(findings)

        run.status = "completed"
        run.completed_at = datetime.now(timezone.utc)
        run.duration_seconds = (run.completed_at - run.started_at).total_seconds()
        db.commit()

        return {"run_id": run_id, "findings_count": len(findings)}

    except Exception as exc:
        logger.exception(f"Baseline review failed for run {run_id}")
        try:
            db.rollback()
            r = db.get(Run, run_id)
            if r:
                r.status = "failed"
                r.error_message = str(exc)[:500]
                db.commit()
        except Exception:
            db.rollback()
        raise self.retry(exc=exc, countdown=15)
    finally:
        db.close()


def _is_relevant_to_agent(finding: dict, agent_type: str) -> bool:
    category = finding.get("category", "").lower()
    security_categories = {
        "hardcoded-api-key", "hardcoded-secret", "aws-access-key", "github-token",
        "openai-key", "slack-token", "dangerous-eval", "dangerous-exec",
        "command-injection", "shell-injection", "insecure-deserialization", "insecure-yaml",
        "xss-risk", "xss-innerHTML", "xss-document-write", "xss-dangerouslySetInnerHTML",
        "dangerous-new-function", "string-timeout", "dynamic-import",
        "sql-concatenation", "sql-sprintf", "prototype-pollution",
    }
    quality_categories = {
        "bare-except", "wildcard-import", "todo-comment", "print-statement",
        "console-log", "var-usage", "loose-equality", "loose-inequality",
        "typescript-any", "ts-ignore", "ts-nocheck", "missing-async",
        "fmt-print", "empty-interface", "env-without-default",
    }
    performance_categories = {
        "goroutine-leak", "goroutine-in-loop", "time-sleep", "mutex-without-lock",
    }
    logic_categories = {
        "mutable-default", "assert-in-prod",
        "unchecked-error", "unclosed-resource", "log-fatal", "panic-usage",
    }

    agent_categories = {
        "security": security_categories,
        "quality": quality_categories,
        "performance": performance_categories,
        "logic": logic_categories,
    }

    return category in agent_categories.get(agent_type, set())
