import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class RunBase(BaseModel):
    agent_name: str = Field(min_length=1, max_length=100)


class RunCreate(RunBase):
    task_id: uuid.UUID


class RunResponse(RunBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    task_id: uuid.UUID
    status: str
    started_at: datetime | None = None
    completed_at: datetime | None = None
    duration_seconds: float | None = None
    exit_code: int | None = None
    error_message: str | None = None
    created_at: datetime
    updated_at: datetime | None = None
