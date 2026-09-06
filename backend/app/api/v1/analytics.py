import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database.models.user import User
from app.database.session import get_db
from app.dependencies import get_current_active_user
from app.schemas.analytics import (
    AgentPerformanceItem,
    AnalyticsOverview,
    CategoryBreakdownItem,
    ReviewHistoryItem,
    ReviewHistoryResponse,
    ScoreTrendPoint,
)
from app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/overview", response_model=AnalyticsOverview)
def get_overview(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> AnalyticsOverview:
    service = AnalyticsService(db)
    return service.get_overview(current_user.id)


@router.get("/reviews", response_model=ReviewHistoryResponse)
def get_review_history(
    project_id: uuid.UUID | None = Query(None),
    status: str | None = Query(None),
    min_score: float | None = Query(None, ge=0, le=10),
    max_score: float | None = Query(None, ge=0, le=10),
    date_from: datetime | None = Query(None),
    date_to: datetime | None = Query(None),
    search: str | None = Query(None, max_length=200),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> ReviewHistoryResponse:
    service = AnalyticsService(db)
    result = service.get_review_history(
        user_id=current_user.id,
        project_id=project_id,
        status=status,
        min_score=min_score,
        max_score=max_score,
        date_from=date_from,
        date_to=date_to,
        search=search,
        page=page,
        per_page=per_page,
    )
    return ReviewHistoryResponse(
        reviews=[ReviewHistoryItem.model_validate(r) for r in result["reviews"]],
        total=result["total"],
        page=result["page"],
        per_page=result["per_page"],
        total_pages=result["total_pages"],
    )


@router.get("/score-trends", response_model=list[ScoreTrendPoint])
def get_score_trends(
    project_id: uuid.UUID | None = Query(None),
    days: int = Query(30, ge=7, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> list[ScoreTrendPoint]:
    service = AnalyticsService(db)
    return service.get_score_trends(current_user.id, project_id, days)


@router.get("/categories", response_model=list[CategoryBreakdownItem])
def get_category_breakdown(
    project_id: uuid.UUID | None = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> list[CategoryBreakdownItem]:
    service = AnalyticsService(db)
    return service.get_category_breakdown(current_user.id, project_id)


@router.get("/agents", response_model=list[AgentPerformanceItem])
def get_agent_performance(
    project_id: uuid.UUID | None = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> list[AgentPerformanceItem]:
    service = AnalyticsService(db)
    return service.get_agent_performance(current_user.id, project_id)
