import hashlib
import uuid
import logging

from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database.models.finding_feedback import FindingFeedback

logger = logging.getLogger(__name__)

VALID_ACTIONS = {"accept", "dismiss", "false_positive"}


def _hash_finding(finding: dict) -> str:
    key = f"{finding.get('file', '')}:{finding.get('line', '')}:{finding.get('category', '')}:{finding.get('message', '')}"
    return hashlib.sha256(key.encode()).hexdigest()[:64]


def record_feedback(
    db: Session,
    review_id: uuid.UUID,
    project_id: uuid.UUID,
    user_id: uuid.UUID,
    finding: dict,
    action: str,
    reason: str | None = None,
) -> FindingFeedback:
    finding_hash = _hash_finding(finding)

    existing = db.query(FindingFeedback).filter(
        FindingFeedback.review_id == review_id,
        FindingFeedback.finding_hash == finding_hash,
    ).first()

    if existing:
        existing.action = action
        existing.reason = reason
        db.commit()
        db.refresh(existing)
        return existing

    fb = FindingFeedback(
        review_id=review_id,
        project_id=project_id,
        user_id=user_id,
        finding_hash=finding_hash,
        action=action,
        agent=finding.get("agent"),
        category=finding.get("category"),
        severity=finding.get("severity"),
        reason=reason,
    )
    db.add(fb)
    db.commit()
    db.refresh(fb)
    return fb


def get_feedback_for_review(db: Session, review_id: uuid.UUID) -> list[FindingFeedback]:
    return db.query(FindingFeedback).filter(
        FindingFeedback.review_id == review_id,
    ).all()


def get_project_feedback_stats(db: Session, project_id: uuid.UUID) -> dict:
    rows = db.query(
        FindingFeedback.category,
        FindingFeedback.action,
        func.count(FindingFeedback.id),
    ).filter(
        FindingFeedback.project_id == project_id,
    ).group_by(
        FindingFeedback.category,
        FindingFeedback.action,
    ).all()

    stats = {}
    for category, action, count in rows:
        if category not in stats:
            stats[category] = {"accept": 0, "dismiss": 0, "false_positive": 0, "total": 0}
        stats[category][action] = count
        stats[category]["total"] += count

    for cat_stats in stats.values():
        total = cat_stats["total"]
        cat_stats["dismiss_rate"] = round(
            (cat_stats["dismiss"] + cat_stats["false_positive"]) / total * 100, 1
        ) if total > 0 else 0

    return stats


def get_agent_accuracy(db: Session, project_id: uuid.UUID) -> dict:
    rows = db.query(
        FindingFeedback.agent,
        FindingFeedback.action,
        func.count(FindingFeedback.id),
    ).filter(
        FindingFeedback.project_id == project_id,
    ).group_by(
        FindingFeedback.agent,
        FindingFeedback.action,
    ).all()

    stats = {}
    for agent, action, count in rows:
        if not agent:
            continue
        if agent not in stats:
            stats[agent] = {"accept": 0, "dismiss": 0, "false_positive": 0, "total": 0}
        stats[agent][action] = count
        stats[agent]["total"] += count

    for agent_stats in stats.values():
        total = agent_stats["total"]
        agent_stats["accuracy"] = round(
            agent_stats["accept"] / total * 100, 1
        ) if total > 0 else 0

    return stats
