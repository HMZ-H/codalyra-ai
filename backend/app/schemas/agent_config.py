import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


VALID_AGENT_TYPES = {"logic", "security", "performance", "quality"}


class AgentConfigBase(BaseModel):
    agent_type: str
    custom_prompt: str | None = None
    temperature: float = Field(default=0.2, ge=0.0, le=1.0)
    is_enabled: bool = True


class AgentConfigCreate(AgentConfigBase):
    pass


class AgentConfigUpdate(BaseModel):
    custom_prompt: str | None = None
    temperature: float | None = Field(default=None, ge=0.0, le=1.0)
    is_enabled: bool | None = None


class AgentConfigResponse(AgentConfigBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_id: uuid.UUID
    created_at: datetime
    updated_at: datetime | None = None


class AgentConfigWithDefaults(BaseModel):
    agent_type: str
    custom_prompt: str | None = None
    default_prompt: str
    temperature: float = 0.2
    is_enabled: bool = True
    is_customized: bool = False
