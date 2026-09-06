import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ProjectBase(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    slack_webhook_url: str | None = None
    discord_webhook_url: str | None = None


class ProjectResponse(ProjectBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    owner_id: uuid.UUID
    team_id: uuid.UUID | None = None
    slack_webhook_url: str | None = None
    discord_webhook_url: str | None = None
    is_active: bool
    created_at: datetime
    updated_at: datetime | None = None
