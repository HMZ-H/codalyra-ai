import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class TaskBase(BaseModel):
    title: str = Field(min_length=1, max_length=500)
    description: str = Field(min_length=1)
    language: str | None = None
    difficulty: Literal["easy", "medium", "hard"] | None = None
    expected_output: str | None = None
    test_command: str | None = None
    time_limit_seconds: int = Field(default=300, ge=10, le=3600)


class TaskCreate(TaskBase):
    project_id: uuid.UUID
    repository_id: uuid.UUID | None = None


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=500)
    description: str | None = Field(default=None, min_length=1)
    language: str | None = None
    difficulty: Literal["easy", "medium", "hard"] | None = None
    status: Literal["draft", "active", "archived"] | None = None
    expected_output: str | None = None
    test_command: str | None = None
    time_limit_seconds: int | None = Field(default=None, ge=10, le=3600)


class TaskResponse(TaskBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_id: uuid.UUID
    repository_id: uuid.UUID | None = None
    created_by_id: uuid.UUID
    status: str
    created_at: datetime
    updated_at: datetime | None = None
