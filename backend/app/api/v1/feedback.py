import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.permissions import verify_review_owner
from app.database.models.review import Review
from app.database.models.user import User
from app.database.session import get_db
from app.dependencies import get_current_user
from app.services.feedback_service import (
    VALID_ACTIONS,
    get_agent_accuracy,
    get_feedback_for_review,
    get_project_feedback_stats,
    record_feedback,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/feedback", tags=["feedback"])


class FeedbackSubmit(BaseModel):
    finding: dict
    action: str = Field(...)
    reason: str | None = None


class FeedbackResponse(BaseModel):
    id: uuid.UUID
    finding_hash: str
    action: str
    agent: str | None
    category: str | None
    severity: str | None
    reason: str | None

    model_config = {"from_attributes": True}


@router.post("/reviews/{review_id}", response_model=FeedbackResponse)
def submit_feedback(
    review_id: uuid.UUID,
    data: FeedbackSubmit,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if data.action not in VALID_ACTIONS:
        raise HTTPException(status_code=400, detail=f"Action must be one of: {', '.join(sorted(VALID_ACTIONS))}")

    verify_review_owner(db, review_id, current_user.id)
    review = db.get(Review, review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    fb = record_feedback(
        db=db,
        review_id=review_id,
        project_id=review.project_id,
        user_id=current_user.id,
        finding=data.finding,
        action=data.action,
        reason=data.reason,
    )
    return fb


@router.get("/reviews/{review_id}", response_model=list[FeedbackResponse])
def get_review_feedback(
    review_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    verify_review_owner(db, review_id, current_user.id)
    return get_feedback_for_review(db, review_id)


@router.get("/projects/{project_id}/stats")
def get_feedback_stats(
    project_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from app.core.permissions import verify_project_owner
    verify_project_owner(db, project_id, current_user.id)

    return {
        "category_stats": get_project_feedback_stats(db, project_id),
        "agent_accuracy": get_agent_accuracy(db, project_id),
    }
