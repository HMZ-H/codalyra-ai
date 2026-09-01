import uuid
import json
import logging

from sqlalchemy.orm import Session

from app.database.models.review import Review
from app.database.models.run import Run
from app.database.models.task import Task
from app.repositories.review_repository import ReviewRepository
from app.ai.analyzer import compare_findings

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

        from app.workers.review_tasks import run_specialist_review, run_baseline_review
        for run in runs:
            if run.agent_name == "synthesis-agent":
                continue
            elif run.agent_name == "baseline-agent":
                run_baseline_review.delay(str(run.id), str(review.id), diff_content)
            else:
                agent_type = run.agent_name.replace("-agent", "")
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
