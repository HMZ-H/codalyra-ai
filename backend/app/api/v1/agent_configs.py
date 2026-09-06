import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.ai.prompts import PROMPT_MAP
from app.ai.providers import PROVIDER_MODELS
from app.database.models.agent_config import AgentConfig
from app.database.models.project import Project
from app.database.models.user import User
from app.database.session import get_db
from app.dependencies import get_current_user
from app.schemas.agent_config import (
    VALID_AGENT_TYPES,
    AgentConfigResponse,
    AgentConfigUpdate,
    AgentConfigWithDefaults,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/projects/{project_id}/agents", tags=["agent-configs"])


def _verify_project_owner(db: Session, project_id: uuid.UUID, user: User) -> Project:
    project = db.get(Project, project_id)
    if not project or project.owner_id != user.id:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.get("", response_model=list[AgentConfigWithDefaults])
def list_agent_configs(
    project_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _verify_project_owner(db, project_id, current_user)

    existing = db.query(AgentConfig).filter(AgentConfig.project_id == project_id).all()
    config_map = {c.agent_type: c for c in existing}

    result = []
    for agent_type in sorted(VALID_AGENT_TYPES):
        default_prompt = PROMPT_MAP.get(agent_type, "")
        cfg = config_map.get(agent_type)
        result.append(AgentConfigWithDefaults(
            agent_type=agent_type,
            custom_prompt=cfg.custom_prompt if cfg else None,
            default_prompt=default_prompt,
            temperature=cfg.temperature if cfg else 0.2,
            provider=cfg.provider if cfg else None,
            model_name=cfg.model_name if cfg else None,
            is_enabled=cfg.is_enabled if cfg else True,
            is_customized=cfg is not None and (cfg.custom_prompt is not None or cfg.provider is not None),
        ))
    return result


@router.put("/{agent_type}", response_model=AgentConfigResponse)
def upsert_agent_config(
    project_id: uuid.UUID,
    agent_type: str,
    data: AgentConfigUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if agent_type not in VALID_AGENT_TYPES:
        raise HTTPException(status_code=400, detail=f"Invalid agent type. Must be one of: {', '.join(sorted(VALID_AGENT_TYPES))}")

    _verify_project_owner(db, project_id, current_user)

    cfg = db.query(AgentConfig).filter(
        AgentConfig.project_id == project_id,
        AgentConfig.agent_type == agent_type,
    ).first()

    if cfg:
        if data.custom_prompt is not None:
            cfg.custom_prompt = data.custom_prompt
        if data.temperature is not None:
            cfg.temperature = data.temperature
        if data.provider is not None:
            cfg.provider = data.provider if data.provider else None
        if data.model_name is not None:
            cfg.model_name = data.model_name if data.model_name else None
        if data.is_enabled is not None:
            cfg.is_enabled = data.is_enabled
    else:
        cfg = AgentConfig(
            project_id=project_id,
            agent_type=agent_type,
            custom_prompt=data.custom_prompt,
            temperature=data.temperature if data.temperature is not None else 0.2,
            provider=data.provider,
            model_name=data.model_name,
            is_enabled=data.is_enabled if data.is_enabled is not None else True,
        )
        db.add(cfg)

    db.commit()
    db.refresh(cfg)
    return cfg


@router.delete("/{agent_type}")
def reset_agent_config(
    project_id: uuid.UUID,
    agent_type: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if agent_type not in VALID_AGENT_TYPES:
        raise HTTPException(status_code=400, detail="Invalid agent type")

    _verify_project_owner(db, project_id, current_user)

    cfg = db.query(AgentConfig).filter(
        AgentConfig.project_id == project_id,
        AgentConfig.agent_type == agent_type,
    ).first()

    if cfg:
        db.delete(cfg)
        db.commit()

    return {"detail": f"{agent_type} agent config reset to defaults"}


@router.get("/providers", tags=["agent-configs"])
def list_providers():
    return {
        name: {"default": info["default"], "models": info["models"]}
        for name, info in PROVIDER_MODELS.items()
    }
