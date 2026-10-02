import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundException
from app.core.permissions import verify_project_owner, verify_review_owner
from app.database.models.user import User
from app.database.session import get_db
from app.dependencies import get_current_active_user
from app.middleware.rate_limit import check_rate_limit
from app.schemas.review import ReviewCreate, ReviewResponse, ReviewSummaryResponse
from app.services.review_service import ReviewService

router = APIRouter(prefix="/reviews", tags=["reviews"])


@router.post("/", response_model=ReviewResponse, status_code=201)
def create_review(
    review_data: ReviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> ReviewResponse:
    verify_project_owner(db, review_data.project_id, current_user.id)
    check_rate_limit(str(current_user.id), action="review", max_requests=10)
    review = ReviewService.create_review(
        db=db,
        project_id=review_data.project_id,
        created_by_id=current_user.id,
        diff_content=review_data.diff_content,
        pr_title=review_data.pr_title,
    )
    return review


@router.get("/", response_model=list[ReviewSummaryResponse])
def list_reviews(
    project_id: uuid.UUID = Query(...),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> list[ReviewSummaryResponse]:
    verify_project_owner(db, project_id, current_user.id)
    return ReviewService.list_reviews(db, project_id, skip, limit)


@router.get("/{review_id}", response_model=ReviewResponse)
def get_review(
    review_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> ReviewResponse:
    verify_review_owner(db, review_id, current_user.id)
    review = ReviewService.get_review(db, review_id)
    if not review:
        raise NotFoundException("Review not found")
    return review


@router.get("/{review_id}/report")
def get_review_report(
    review_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> dict:
    verify_review_owner(db, review_id, current_user.id)
    report = ReviewService.get_review_report(db, review_id)
    if not report:
        raise NotFoundException("Review not found")
    return report


@router.post("/{review_id}/auto-fix")
def generate_auto_fixes(
    review_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> dict:
    verify_review_owner(db, review_id, current_user.id)
    fixes = ReviewService.generate_auto_fixes(db, review_id)
    return {"fixes": fixes}
