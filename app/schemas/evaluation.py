import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class EvaluationBase(BaseModel):
    tests_passed: int = Field(ge=0)
    tests_total: int = Field(ge=0)
    score: float | None = Field(default=None, ge=0.0, le=1.0)
    is_correct: bool | None = None
    feedback: str | None = None
    evaluation_method: str = "auto"


class EvaluationCreate(EvaluationBase):
    run_id: uuid.UUID


class EvaluationResponse(EvaluationBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    run_id: uuid.UUID
    evaluated_at: datetime
    created_at: datetime
