import re
import uuid
from datetime import datetime

from pydantic import BaseModel, Field, field_validator

VALID_SEVERITIES = {"critical", "warning", "info"}


class CustomRuleCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: str | None = None
    pattern: str = Field(..., min_length=1)
    severity: str = Field(default="warning")
    category: str = Field(default="custom-rule", max_length=100)
    message: str = Field(..., min_length=1)
    suggestion: str | None = None
    file_pattern: str | None = Field(default=None, max_length=200)
    is_enabled: bool = True

    @field_validator("pattern")
    @classmethod
    def validate_pattern(cls, v):
        try:
            re.compile(v)
        except re.error as e:
            raise ValueError(f"Invalid regex pattern: {e}")
        return v

    @field_validator("severity")
    @classmethod
    def validate_severity(cls, v):
        if v not in VALID_SEVERITIES:
            raise ValueError(f"Severity must be one of: {', '.join(sorted(VALID_SEVERITIES))}")
        return v

    @field_validator("file_pattern")
    @classmethod
    def validate_file_pattern(cls, v):
        if v is not None:
            try:
                re.compile(v)
            except re.error as e:
                raise ValueError(f"Invalid file pattern regex: {e}")
        return v


class CustomRuleUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    pattern: str | None = None
    severity: str | None = None
    category: str | None = None
    message: str | None = None
    suggestion: str | None = None
    file_pattern: str | None = None
    is_enabled: bool | None = None

    @field_validator("pattern")
    @classmethod
    def validate_pattern(cls, v):
        if v is not None:
            try:
                re.compile(v)
            except re.error as e:
                raise ValueError(f"Invalid regex pattern: {e}")
        return v


class CustomRuleResponse(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    name: str
    description: str | None
    pattern: str
    severity: str
    category: str
    message: str
    suggestion: str | None
    file_pattern: str | None
    is_enabled: bool
    created_at: datetime

    model_config = {"from_attributes": True}
