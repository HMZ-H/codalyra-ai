import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.dependencies import get_current_active_user
from app.database.models.user import User
from app.schemas.repository import RepositoryCreate, RepositoryResponse, RepositoryUpdate
from app.services.repository_service import RepositoryService

router = APIRouter(prefix="/repositories", tags=["repositories"])


@router.post("/", response_model=RepositoryResponse, status_code=201)
def create_repository(
    repo_data: RepositoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> RepositoryResponse:
    service = RepositoryService(db)
    return service.create_repository(repo_data, current_user.id)


@router.get("/", response_model=list[RepositoryResponse])
def list_repositories(
    project_id: uuid.UUID = Query(...),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> list[RepositoryResponse]:
    service = RepositoryService(db)
    return service.list_repositories(project_id, skip=skip, limit=limit)


@router.get("/{repo_id}", response_model=RepositoryResponse)
def get_repository(
    repo_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> RepositoryResponse:
    service = RepositoryService(db)
    return service.get_repository(repo_id)


@router.put("/{repo_id}", response_model=RepositoryResponse)
def update_repository(
    repo_id: uuid.UUID,
    update_data: RepositoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> RepositoryResponse:
    service = RepositoryService(db)
    return service.update_repository(repo_id, update_data, current_user.id)


@router.delete("/{repo_id}", status_code=204)
def delete_repository(
    repo_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> None:
    service = RepositoryService(db)
    service.delete_repository(repo_id, current_user.id)
