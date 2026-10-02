import json
import logging
import uuid

from sqlalchemy.orm import Session

from app.ai.analyzer import compare_findings
from app.ai.fixer import AutoFixer
from app.database.models.agent_config import AgentConfig
from app.database.models.review import Review
from app.database.models.run import Run
from app.database.models.task import Task
from app.repositories.review_repository import ReviewRepository

logger = logging.getLogger(__name__)

SPECIALIST_AGENTS = ["logic", "security", "performance", "quality"]


class ReviewService:
    @staticmethod
    def create_review(
        db: Session,
        project_id: uuid.UUID,
        created_by_id: uuid.UUID,
        diff_content: str,
        pr_title: str | None = None,
    ) -> Review:
        repo = ReviewRepository(db)
        review = repo.create({
            "project_id": project_id,
            "created_by_id": created_by_id,
            "pr_title": pr_title or "Code Review",
            "diff_content": diff_content,
            "status": "pending",
        })

        task = Task(
            project_id=project_id,
            created_by_id=created_by_id,
            title=f"Review: {pr_title or 'Code Review'}",
            description="Automated multi-agent PR review",
            status="active",
        )
        db.add(task)
        db.flush()

        agent_names = [f"{a}-agent" for a in SPECIALIST_AGENTS] + ["synthesis-agent", "baseline-agent"]
        runs = []
        for agent_name in agent_names:
            run = Run(
                task_id=task.id,
                review_id=review.id,
                agent_name=agent_name,
                status="pending",
            )
            db.add(run)
            runs.append(run)

        db.commit()
        for run in runs:
            db.refresh(run)

        disabled_agents = {
            cfg.agent_type
            for cfg in db.query(AgentConfig).filter(
                AgentConfig.project_id == project_id,
                AgentConfig.is_enabled == False,
            ).all()
        }

        from app.workers.review_tasks import run_baseline_review, run_specialist_review
        for run in runs:
            if run.agent_name == "synthesis-agent":
                continue
            elif run.agent_name == "baseline-agent":
                run_baseline_review.delay(str(run.id), str(review.id), diff_content)
            else:
                agent_type = run.agent_name.replace("-agent", "")
                if agent_type in disabled_agents:
                    run.status = "skipped"
                    db.commit()
                    continue
                run_specialist_review.delay(str(run.id), str(review.id), agent_type, diff_content)

        return review

    @staticmethod
    def get_review(db: Session, review_id: uuid.UUID) -> Review | None:
        repo = ReviewRepository(db)
        return repo.get_with_runs(review_id)

    @staticmethod
    def list_reviews(db: Session, project_id: uuid.UUID, skip: int = 0, limit: int = 50) -> list[Review]:
        repo = ReviewRepository(db)
        return repo.get_by_project(project_id, skip, limit)

    @staticmethod
    def get_review_report(db: Session, review_id: uuid.UUID) -> dict | None:
        repo = ReviewRepository(db)
        review = repo.get_with_runs(review_id)
        if not review:
            return None

        agent_results = []
        all_agent_findings = []
        baseline_findings = []

        for run in review.runs:
            if not run.evaluation:
                agent_results.append({
                    "agent_type": run.agent_name.replace("-agent", ""),
                    "status": run.status,
                    "findings_count": 0,
                    "score": None,
                    "summary": None,
                })
                continue

            feedback = {}
            if run.evaluation.feedback:
                try:
                    feedback = json.loads(run.evaluation.feedback) if isinstance(run.evaluation.feedback, str) else run.evaluation.feedback
                except (json.JSONDecodeError, TypeError):
                    feedback = {}

            findings = feedback.get("findings", [])

            if run.agent_name == "baseline-agent":
                baseline_findings = findings
            else:
                all_agent_findings.extend(findings)

            agent_results.append({
                "agent_type": run.agent_name.replace("-agent", ""),
                "status": run.status,
                "findings_count": len(findings),
                "score": run.evaluation.score,
                "summary": feedback.get("summary"),
            })

        baseline_comparison = None
        if baseline_findings or all_agent_findings:
            baseline_comparison = compare_findings(all_agent_findings, baseline_findings)

        synthesis_findings = []
        if review.metadata_ and isinstance(review.metadata_, dict):
            synthesis_findings = review.metadata_.get("synthesis_findings", [])

        display_findings = synthesis_findings if synthesis_findings else all_agent_findings

        return {
            "review_id": str(review.id),
            "overall_score": review.overall_score,
            "summary": review.summary,
            "findings": display_findings,
            "agent_results": agent_results,
            "baseline_comparison": baseline_comparison,
        }

    @staticmethod
    def generate_auto_fixes(db: Session, review_id: uuid.UUID) -> list[dict]:
        from app.ai.client import LLMClient
        from app.core.encryption import decrypt_value
        from app.database.models.user import User

        review = db.get(Review, review_id)
        if not review or review.status != "completed":
            return []

        findings = []
        if review.metadata_ and isinstance(review.metadata_, dict):
            findings = review.metadata_.get("synthesis_findings", [])
        if not findings:
            for run in review.runs:
                if run.evaluation and run.evaluation.feedback:
                    try:
                        fb = json.loads(run.evaluation.feedback) if isinstance(run.evaluation.feedback, str) else run.evaluation.feedback
                        findings.extend(fb.get("findings", []))
                    except (json.JSONDecodeError, TypeError):
                        pass

        user = db.get(User, review.created_by_id)
        if not user or not user.gemini_api_key_encrypted:
            return []

        try:
            api_key = decrypt_value(user.gemini_api_key_encrypted)
        except Exception:
            return []

        llm = LLMClient(api_key=api_key)
        fixer = AutoFixer(llm)
        return fixer.generate_fixes(review.diff_content, findings)
