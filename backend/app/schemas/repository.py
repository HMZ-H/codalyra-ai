import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class RepositoryBase(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    url: str = Field(max_length=500)
    default_branch: str = "main"
    language: str | None = None


class RepositoryCreate(RepositoryBase):
    project_id: uuid.UUID


class RepositoryUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    url: str | None = Field(default=None, max_length=500)
    default_branch: str | None = None
    language: str | None = None


class RepositoryResponse(RepositoryBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_id: uuid.UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime | None = None
