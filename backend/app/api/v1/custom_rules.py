import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.models.custom_rule import CustomRule
from app.database.models.project import Project
from app.database.models.user import User
from app.database.session import get_db
from app.dependencies import get_current_user
from app.schemas.custom_rule import CustomRuleCreate, CustomRuleResponse, CustomRuleUpdate

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/projects/{project_id}/rules", tags=["custom-rules"])


def _verify_project_owner(db: Session, project_id: uuid.UUID, user: User) -> Project:
    project = db.get(Project, project_id)
    if not project or project.owner_id != user.id:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.get("", response_model=list[CustomRuleResponse])
def list_rules(
    project_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _verify_project_owner(db, project_id, current_user)
    rules = db.query(CustomRule).filter(CustomRule.project_id == project_id).order_by(CustomRule.created_at).all()
    return rules


@router.post("", response_model=CustomRuleResponse, status_code=201)
def create_rule(
    project_id: uuid.UUID,
    data: CustomRuleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _verify_project_owner(db, project_id, current_user)

    existing = db.query(CustomRule).filter(
        CustomRule.project_id == project_id,
        CustomRule.name == data.name,
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="A rule with this name already exists")

    rule = CustomRule(
        project_id=project_id,
        name=data.name,
        description=data.description,
        pattern=data.pattern,
        severity=data.severity,
        category=data.category,
        message=data.message,
        suggestion=data.suggestion,
        file_pattern=data.file_pattern,
        is_enabled=data.is_enabled,
    )
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return rule


@router.put("/{rule_id}", response_model=CustomRuleResponse)
def update_rule(
    project_id: uuid.UUID,
    rule_id: uuid.UUID,
    data: CustomRuleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _verify_project_owner(db, project_id, current_user)

    rule = db.query(CustomRule).filter(
        CustomRule.id == rule_id,
        CustomRule.project_id == project_id,
    ).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(rule, key, value)

    db.commit()
    db.refresh(rule)
    return rule


@router.delete("/{rule_id}", status_code=204)
def delete_rule(
    project_id: uuid.UUID,
    rule_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _verify_project_owner(db, project_id, current_user)

    rule = db.query(CustomRule).filter(
        CustomRule.id == rule_id,
        CustomRule.project_id == project_id,
    ).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")

    db.delete(rule)
    db.commit()
