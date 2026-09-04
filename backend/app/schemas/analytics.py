import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ReviewHistoryItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_id: uuid.UUID
    pr_title: str | None = None
    status: str
    overall_score: float | None = None
    findings_count: int
    created_at: datetime


class ReviewHistoryResponse(BaseModel):
    reviews: list[ReviewHistoryItem]
    total: int
    page: int
    per_page: int
    total_pages: int


class ScoreTrendPoint(BaseModel):
    date: str
    avg_score: float
    review_count: int


class CategoryBreakdownItem(BaseModel):
    category: str
    count: int


class AgentPerformanceItem(BaseModel):
    agent: str
    total_runs: int
    completed_runs: int
    total_findings: int
    avg_score: float | None = None
    avg_duration_seconds: float | None = None


class AnalyticsOverview(BaseModel):
    total_reviews: int
    avg_score: float | None = None
    total_findings: int
    reviews_last_30_days: int
