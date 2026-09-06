import json
import uuid
from datetime import datetime, timedelta

from sqlalchemy import and_, case, func, select
from sqlalchemy.orm import Session, joinedload

from app.database.models.evaluation import Evaluation
from app.database.models.project import Project
from app.database.models.review import Review
from app.database.models.run import Run


class AnalyticsService:
    def __init__(self, db: Session):
        self.db = db

    def get_review_history(
        self,
        user_id: uuid.UUID,
        project_id: uuid.UUID | None = None,
        status: str | None = None,
        min_score: float | None = None,
        max_score: float | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        search: str | None = None,
        page: int = 1,
        per_page: int = 20,
    ) -> dict:
        base = (
            select(Review)
            .join(Project, Review.project_id == Project.id)
            .where(Project.owner_id == user_id)
        )

        if project_id:
            base = base.where(Review.project_id == project_id)
        if status:
            base = base.where(Review.status == status)
        if min_score is not None:
            base = base.where(Review.overall_score >= min_score)
        if max_score is not None:
            base = base.where(Review.overall_score <= max_score)
        if date_from:
            base = base.where(Review.created_at >= date_from)
        if date_to:
            base = base.where(Review.created_at <= date_to)
        if search:
            base = base.where(Review.pr_title.ilike(f"%{search}%"))

        count_stmt = select(func.count()).select_from(base.subquery())
        total = self.db.scalar(count_stmt) or 0

        stmt = (
            base
            .order_by(Review.created_at.desc())
            .offset((page - 1) * per_page)
            .limit(per_page)
        )
        reviews = list(self.db.scalars(stmt).all())

        return {
            "reviews": reviews,
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": max(1, (total + per_page - 1) // per_page),
        }

    def get_score_trends(
        self,
        user_id: uuid.UUID,
        project_id: uuid.UUID | None = None,
        days: int = 30,
    ) -> list[dict]:
        since = datetime.utcnow() - timedelta(days=days)
        base = (
            select(
                func.date(Review.created_at).label("date"),
                func.avg(Review.overall_score).label("avg_score"),
                func.count(Review.id).label("review_count"),
            )
            .join(Project, Review.project_id == Project.id)
            .where(
                Project.owner_id == user_id,
                Review.created_at >= since,
                Review.overall_score.isnot(None),
            )
        )
        if project_id:
            base = base.where(Review.project_id == project_id)

        stmt = base.group_by(func.date(Review.created_at)).order_by(func.date(Review.created_at))
        rows = self.db.execute(stmt).all()
        return [
            {"date": str(r.date), "avg_score": round(r.avg_score, 2), "review_count": r.review_count}
            for r in rows
        ]

    def get_category_breakdown(
        self,
        user_id: uuid.UUID,
        project_id: uuid.UUID | None = None,
    ) -> list[dict]:
        base = (
            select(Run)
            .join(Review, Run.review_id == Review.id)
            .join(Project, Review.project_id == Project.id)
            .options(joinedload(Run.evaluation))
            .where(
                Project.owner_id == user_id,
                Run.status == "completed",
            )
        )
        if project_id:
            base = base.where(Review.project_id == project_id)

        runs = self.db.scalars(base).unique().all()

        category_counts: dict[str, int] = {}
        for run in runs:
            if not run.evaluation or not run.evaluation.feedback:
                continue
            try:
                feedback = json.loads(run.evaluation.feedback) if isinstance(run.evaluation.feedback, str) else run.evaluation.feedback
            except (json.JSONDecodeError, TypeError):
                continue
            for finding in feedback.get("findings", []):
                cat = finding.get("category", "unknown")
                category_counts[cat] = category_counts.get(cat, 0) + 1

        sorted_cats = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)
        return [{"category": cat, "count": count} for cat, count in sorted_cats]

    def get_agent_performance(
        self,
        user_id: uuid.UUID,
        project_id: uuid.UUID | None = None,
    ) -> list[dict]:
        base = (
            select(Run)
            .join(Review, Run.review_id == Review.id)
            .join(Project, Review.project_id == Project.id)
            .options(joinedload(Run.evaluation))
            .where(
                Project.owner_id == user_id,
                Run.agent_name.notin_(["synthesis-agent", "baseline-agent"]),
            )
        )
        if project_id:
            base = base.where(Review.project_id == project_id)

        runs = self.db.scalars(base).unique().all()

        agents: dict[str, dict] = {}
        for run in runs:
            name = run.agent_name.replace("-agent", "")
            if name not in agents:
                agents[name] = {
                    "agent": name,
                    "total_runs": 0,
                    "completed_runs": 0,
                    "total_findings": 0,
                    "scores": [],
                    "avg_duration": [],
                }

            agents[name]["total_runs"] += 1
            if run.status == "completed":
                agents[name]["completed_runs"] += 1
            if run.duration_seconds:
                agents[name]["avg_duration"].append(run.duration_seconds)
            if run.evaluation:
                if run.evaluation.score is not None:
                    agents[name]["scores"].append(run.evaluation.score)
                if run.evaluation.feedback:
                    try:
                        feedback = json.loads(run.evaluation.feedback) if isinstance(run.evaluation.feedback, str) else run.evaluation.feedback
                        agents[name]["total_findings"] += len(feedback.get("findings", []))
                    except (json.JSONDecodeError, TypeError):
                        pass

        result = []
        for data in agents.values():
            scores = data.pop("scores")
            durations = data.pop("avg_duration")
            data["avg_score"] = round(sum(scores) / len(scores), 2) if scores else None
            data["avg_duration_seconds"] = round(sum(durations) / len(durations), 1) if durations else None
            result.append(data)

        result.sort(key=lambda x: x["total_findings"], reverse=True)
        return result

    def get_overview(self, user_id: uuid.UUID) -> dict:
        base = (
            select(Review)
            .join(Project, Review.project_id == Project.id)
            .where(Project.owner_id == user_id)
        )

        total_reviews = self.db.scalar(select(func.count()).select_from(base.subquery())) or 0

        avg_score = self.db.scalar(
            select(func.avg(Review.overall_score))
            .join(Project, Review.project_id == Project.id)
            .where(Project.owner_id == user_id, Review.overall_score.isnot(None))
        )

        total_findings = self.db.scalar(
            select(func.sum(Review.findings_count))
            .join(Project, Review.project_id == Project.id)
            .where(Project.owner_id == user_id)
        ) or 0

        last_30 = datetime.utcnow() - timedelta(days=30)
        recent_count = self.db.scalar(
            select(func.count())
            .select_from(
                select(Review)
                .join(Project, Review.project_id == Project.id)
                .where(Project.owner_id == user_id, Review.created_at >= last_30)
                .subquery()
            )
        ) or 0

        return {
            "total_reviews": total_reviews,
            "avg_score": round(avg_score, 2) if avg_score else None,
            "total_findings": total_findings,
            "reviews_last_30_days": recent_count,
        }
