import json
import logging

from sqlalchemy.orm import Session

from app.ai.analyzer import compare_findings, score_findings, sort_findings
from app.database.models.review import Review
from app.database.models.run import Run

logger = logging.getLogger(__name__)


class ReportService:
    @staticmethod
    def generate_report(db: Session, review_id: str) -> dict:
        review = db.get(Review, review_id)
        if not review:
            return {}

        runs = db.query(Run).filter(Run.review_id == review_id).all()

        agent_findings = {}
        baseline_findings = []

        for run in runs:
            if not run.evaluation or not run.evaluation.feedback:
                continue
            try:
                feedback = json.loads(run.evaluation.feedback) if isinstance(run.evaluation.feedback, str) else run.evaluation.feedback
            except (json.JSONDecodeError, TypeError):
                continue

            findings = feedback.get("findings", [])
            agent_type = run.agent_name.replace("-agent", "")

            if agent_type == "baseline":
                baseline_findings = findings
            else:
                agent_findings[agent_type] = findings

        all_agent = []
        for findings_list in agent_findings.values():
            all_agent.extend(findings_list)

        comparison = compare_findings(all_agent, baseline_findings)

        return {
            "review_id": str(review.id),
            "overall_score": review.overall_score,
            "summary": review.summary,
            "findings_count": review.findings_count,
            "agent_findings": agent_findings,
            "baseline_findings": baseline_findings,
            "comparison": comparison,
        }
