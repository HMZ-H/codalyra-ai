import uuid

from sqlalchemy.orm import Session

from app.core.exceptions import ForbiddenException, NotFoundException
from app.database.models.project import Project
from app.repositories.project_repository import ProjectRepository
from app.schemas.project import ProjectCreate, ProjectUpdate


class ProjectService:
    def __init__(self, db: Session):
        self.repo = ProjectRepository(db)

    def create_project(self, project_data: ProjectCreate, owner_id: uuid.UUID) -> Project:
        return self.repo.create({
            "name": project_data.name,
            "description": project_data.description,
            "owner_id": owner_id,
        })

    def get_project(self, project_id: uuid.UUID) -> Project:
        project = self.repo.get_by_id(project_id)
        if not project or not project.is_active:
            raise NotFoundException("Project not found")
        return project

    def list_user_projects(self, owner_id: uuid.UUID, skip: int = 0, limit: int = 20) -> list[Project]:
        return self.repo.get_by_owner(owner_id, skip=skip, limit=limit)

    def update_project(self, project_id: uuid.UUID, update_data: ProjectUpdate, owner_id: uuid.UUID) -> Project:
        project = self.get_project(project_id)
        self._check_ownership(project, owner_id)
        data = update_data.model_dump(exclude_unset=True)
        if not data:
            return project
        return self.repo.update(project, data)

    def delete_project(self, project_id: uuid.UUID, owner_id: uuid.UUID) -> None:
        project = self.get_project(project_id)
        self._check_ownership(project, owner_id)
        self.repo.delete(project)

    def _check_ownership(self, project: Project, user_id: uuid.UUID) -> None:
        if project.owner_id != user_id:
            raise ForbiddenException("You do not own this project")
