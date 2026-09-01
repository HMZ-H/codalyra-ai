import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ReviewCreate(BaseModel):
    project_id: uuid.UUID
    pr_title: str | None = None
    diff_content: str = Field(min_length=1)


class ReviewResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_id: uuid.UUID
    created_by_id: uuid.UUID
    pr_title: str | None = None
    diff_content: str
    status: str
    overall_score: float | None = None
    summary: str | None = None
    findings_count: int
    baseline_summary: str | None = None
    baseline_score: float | None = None
    metadata_: dict | None = None
    created_at: datetime
    updated_at: datetime | None = None


class ReviewSummaryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_id: uuid.UUID
    pr_title: str | None = None
    status: str
    overall_score: float | None = None
    findings_count: int
    created_at: datetime


class FindingItem(BaseModel):
    file: str
    line: int | None = None
    severity: str
    category: str
    message: str
    agent: str
    suggestion: str | None = None


class AgentResult(BaseModel):
    agent_type: str
    status: str
    findings_count: int
    score: float | None = None
    summary: str | None = None


class BaselineComparison(BaseModel):
    baseline_findings_count: int
    agent_findings_count: int
    baseline_score: float | None = None
    agent_score: float | None = None
    unique_to_agents: int
    unique_to_baseline: int
    categories_covered_agents: list[str]
    categories_covered_baseline: list[str]


class ReviewReportResponse(BaseModel):
    review_id: uuid.UUID
    overall_score: float | None = None
    summary: str | None = None
    findings: list[FindingItem]
    agent_results: list[AgentResult]
    baseline_comparison: BaselineComparison | None = None
