import uuid
from datetime import datetime

from pydantic import BaseModel, Field

VALID_ROLES = {"admin", "reviewer", "viewer"}


class TeamCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    slug: str = Field(..., min_length=1, max_length=100, pattern=r"^[a-z0-9\-]+$")
    description: str | None = None


class TeamUpdate(BaseModel):
    name: str | None = None
    description: str | None = None


class TeamMemberAdd(BaseModel):
    email: str
    role: str = Field(default="viewer")


class TeamMemberUpdate(BaseModel):
    role: str


class TeamMemberResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    email: str | None = None
    username: str | None = None
    full_name: str | None = None
    role: str
    joined_at: datetime

    model_config = {"from_attributes": True}


class TeamResponse(BaseModel):
    id: uuid.UUID
    name: str
    slug: str
    description: str | None
    owner_id: uuid.UUID
    member_count: int = 0
    created_at: datetime

    model_config = {"from_attributes": True}
