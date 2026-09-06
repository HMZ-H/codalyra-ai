import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database.models.user import User
from app.database.session import get_db
from app.dependencies import get_current_active_user
from app.schemas.project import ProjectCreate, ProjectResponse, ProjectUpdate
from app.services.project_service import ProjectService

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("/", response_model=ProjectResponse, status_code=201)
def create_project(
    project_data: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> ProjectResponse:
    service = ProjectService(db)
    return service.create_project(project_data, current_user.id)


@router.get("/", response_model=list[ProjectResponse])
def list_projects(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> list[ProjectResponse]:
    service = ProjectService(db)
    return service.list_user_projects(current_user.id, skip=skip, limit=limit)


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(
    project_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> ProjectResponse:
    from app.core.permissions import verify_project_owner
    verify_project_owner(db, project_id, current_user.id)
    service = ProjectService(db)
    return service.get_project(project_id)


@router.put("/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id: uuid.UUID,
    update_data: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> ProjectResponse:
    service = ProjectService(db)
    return service.update_project(project_id, update_data, current_user.id)


@router.delete("/{project_id}", status_code=204)
def delete_project(
    project_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> None:
    service = ProjectService(db)
    service.delete_project(project_id, current_user.id)
