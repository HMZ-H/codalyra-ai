import uuid

from sqlalchemy.orm import Session

from app.core.exceptions import ForbiddenException, NotFoundException
from app.database.models.repository import Repository
from app.repositories.project_repository import ProjectRepository
from app.schemas.repository import RepositoryCreate, RepositoryUpdate


class RepositoryService:
    def __init__(self, db: Session):
        self.db = db
        self.project_repo = ProjectRepository(db)

    def create_repository(self, repo_data: RepositoryCreate, user_id: uuid.UUID) -> Repository:
        project = self.project_repo.get_by_id(repo_data.project_id)
        if not project or not project.is_active:
            raise NotFoundException("Project not found")
        if project.owner_id != user_id:
            raise ForbiddenException("You do not own this project")

        repo = Repository(
            project_id=repo_data.project_id,
            name=repo_data.name,
            url=repo_data.url,
            default_branch=repo_data.default_branch,
            language=repo_data.language,
        )
        self.db.add(repo)
        self.db.commit()
        self.db.refresh(repo)
        return repo

    def get_repository(self, repo_id: uuid.UUID) -> Repository:
        repo = self.db.get(Repository, repo_id)
        if not repo or not repo.is_active:
            raise NotFoundException("Repository not found")
        return repo

    def list_repositories(self, project_id: uuid.UUID, skip: int = 0, limit: int = 20) -> list[Repository]:
        from sqlalchemy import select

        stmt = (
            select(Repository)
            .where(Repository.project_id == project_id, Repository.is_active.is_(True))
            .offset(skip)
            .limit(limit)
        )
        return list(self.db.scalars(stmt).all())

    def update_repository(self, repo_id: uuid.UUID, update_data: RepositoryUpdate, user_id: uuid.UUID) -> Repository:
        repo = self.get_repository(repo_id)
        project = self.project_repo.get_by_id(repo.project_id)
        if not project or project.owner_id != user_id:
            raise ForbiddenException("You do not own this repository's project")

        data = update_data.model_dump(exclude_unset=True)
        if not data:
            return repo
        for key, value in data.items():
            setattr(repo, key, value)
        self.db.commit()
        self.db.refresh(repo)
        return repo

    def delete_repository(self, repo_id: uuid.UUID, user_id: uuid.UUID) -> None:
        repo = self.get_repository(repo_id)
        project = self.project_repo.get_by_id(repo.project_id)
        if not project or project.owner_id != user_id:
            raise ForbiddenException("You do not own this repository's project")

        repo.is_active = False
        self.db.commit()
