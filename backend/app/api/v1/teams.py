import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.models.team import Team, TeamMember
from app.database.models.user import User
from app.database.session import get_db
from app.dependencies import get_current_user
from app.schemas.team import (
    VALID_ROLES,
    TeamCreate,
    TeamMemberAdd,
    TeamMemberResponse,
    TeamMemberUpdate,
    TeamResponse,
    TeamUpdate,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/teams", tags=["teams"])


def _get_team_or_404(db: Session, team_id: uuid.UUID) -> Team:
    team = db.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    return team


def _require_team_admin(db: Session, team_id: uuid.UUID, user: User):
    team = _get_team_or_404(db, team_id)
    if team.owner_id == user.id:
        return team
    member = db.query(TeamMember).filter(
        TeamMember.team_id == team_id,
        TeamMember.user_id == user.id,
    ).first()
    if not member or member.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return team


def _require_team_member(db: Session, team_id: uuid.UUID, user: User):
    team = _get_team_or_404(db, team_id)
    if team.owner_id == user.id:
        return team
    member = db.query(TeamMember).filter(
        TeamMember.team_id == team_id,
        TeamMember.user_id == user.id,
    ).first()
    if not member:
        raise HTTPException(status_code=403, detail="Not a team member")
    return team


@router.post("/", response_model=TeamResponse, status_code=201)
def create_team(
    data: TeamCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    existing = db.query(Team).filter(Team.slug == data.slug).first()
    if existing:
        raise HTTPException(status_code=409, detail="Team slug already taken")

    team = Team(
        name=data.name,
        slug=data.slug,
        description=data.description,
        owner_id=current_user.id,
    )
    db.add(team)
    db.flush()

    owner_member = TeamMember(
        team_id=team.id,
        user_id=current_user.id,
        role="admin",
    )
    db.add(owner_member)
    db.commit()
    db.refresh(team)

    return TeamResponse(
        id=team.id, name=team.name, slug=team.slug,
        description=team.description, owner_id=team.owner_id,
        member_count=1, created_at=team.created_at,
    )


@router.get("/", response_model=list[TeamResponse])
def list_teams(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    memberships = db.query(TeamMember).filter(TeamMember.user_id == current_user.id).all()
    team_ids = [m.team_id for m in memberships]
    if not team_ids:
        return []

    teams = db.query(Team).filter(Team.id.in_(team_ids)).all()
    result = []
    for t in teams:
        count = db.query(TeamMember).filter(TeamMember.team_id == t.id).count()
        result.append(TeamResponse(
            id=t.id, name=t.name, slug=t.slug,
            description=t.description, owner_id=t.owner_id,
            member_count=count, created_at=t.created_at,
        ))
    return result


@router.get("/{team_id}", response_model=TeamResponse)
def get_team(
    team_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    team = _require_team_member(db, team_id, current_user)
    count = db.query(TeamMember).filter(TeamMember.team_id == team.id).count()
    return TeamResponse(
        id=team.id, name=team.name, slug=team.slug,
        description=team.description, owner_id=team.owner_id,
        member_count=count, created_at=team.created_at,
    )


@router.put("/{team_id}", response_model=TeamResponse)
def update_team(
    team_id: uuid.UUID,
    data: TeamUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    team = _require_team_admin(db, team_id, current_user)
    if data.name is not None:
        team.name = data.name
    if data.description is not None:
        team.description = data.description
    db.commit()
    db.refresh(team)

    count = db.query(TeamMember).filter(TeamMember.team_id == team.id).count()
    return TeamResponse(
        id=team.id, name=team.name, slug=team.slug,
        description=team.description, owner_id=team.owner_id,
        member_count=count, created_at=team.created_at,
    )


@router.delete("/{team_id}", status_code=204)
def delete_team(
    team_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    team = _get_team_or_404(db, team_id)
    if team.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only the team owner can delete the team")
    db.delete(team)
    db.commit()


@router.get("/{team_id}/members", response_model=list[TeamMemberResponse])
def list_members(
    team_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_team_member(db, team_id, current_user)
    members = db.query(TeamMember).filter(TeamMember.team_id == team_id).all()

    result = []
    for m in members:
        user = db.get(User, m.user_id)
        result.append(TeamMemberResponse(
            id=m.id,
            user_id=m.user_id,
            email=user.email if user else None,
            username=user.username if user else None,
            full_name=user.full_name if user else None,
            role=m.role,
            joined_at=m.joined_at,
        ))
    return result


@router.post("/{team_id}/members", response_model=TeamMemberResponse, status_code=201)
def add_member(
    team_id: uuid.UUID,
    data: TeamMemberAdd,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_team_admin(db, team_id, current_user)

    if data.role not in VALID_ROLES:
        raise HTTPException(status_code=400, detail=f"Invalid role. Must be one of: {', '.join(sorted(VALID_ROLES))}")

    target_user = db.query(User).filter(User.email == data.email).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found with that email")

    existing = db.query(TeamMember).filter(
        TeamMember.team_id == team_id,
        TeamMember.user_id == target_user.id,
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="User is already a team member")

    member = TeamMember(
        team_id=team_id,
        user_id=target_user.id,
        role=data.role,
    )
    db.add(member)
    db.commit()
    db.refresh(member)

    return TeamMemberResponse(
        id=member.id,
        user_id=target_user.id,
        email=target_user.email,
        username=target_user.username,
        full_name=target_user.full_name,
        role=member.role,
        joined_at=member.joined_at,
    )


@router.put("/{team_id}/members/{member_id}", response_model=TeamMemberResponse)
def update_member_role(
    team_id: uuid.UUID,
    member_id: uuid.UUID,
    data: TeamMemberUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_team_admin(db, team_id, current_user)

    if data.role not in VALID_ROLES:
        raise HTTPException(status_code=400, detail=f"Invalid role. Must be one of: {', '.join(sorted(VALID_ROLES))}")

    member = db.query(TeamMember).filter(
        TeamMember.id == member_id,
        TeamMember.team_id == team_id,
    ).first()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")

    member.role = data.role
    db.commit()
    db.refresh(member)

    user = db.get(User, member.user_id)
    return TeamMemberResponse(
        id=member.id,
        user_id=member.user_id,
        email=user.email if user else None,
        username=user.username if user else None,
        full_name=user.full_name if user else None,
        role=member.role,
        joined_at=member.joined_at,
    )


@router.delete("/{team_id}/members/{member_id}", status_code=204)
def remove_member(
    team_id: uuid.UUID,
    member_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_team_admin(db, team_id, current_user)

    member = db.query(TeamMember).filter(
        TeamMember.id == member_id,
        TeamMember.team_id == team_id,
    ).first()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")

    team = db.get(Team, team_id)
    if member.user_id == team.owner_id:
        raise HTTPException(status_code=400, detail="Cannot remove the team owner")

    db.delete(member)
    db.commit()
