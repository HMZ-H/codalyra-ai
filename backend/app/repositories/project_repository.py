import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.models.project import Project


class ProjectRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, project_id: uuid.UUID) -> Project | None:
        return self.db.get(Project, project_id)

    def get_by_owner(self, owner_id: uuid.UUID, skip: int = 0, limit: int = 100) -> list[Project]:
        stmt = (
            select(Project)
            .where(Project.owner_id == owner_id, Project.is_active.is_(True))
            .offset(skip)
            .limit(limit)
        )
        return list(self.db.scalars(stmt).all())

    def create(self, project_data: dict) -> Project:
        project = Project(**project_data)
        self.db.add(project)
        self.db.commit()
        self.db.refresh(project)
        return project

    def update(self, project: Project, update_data: dict) -> Project:
        for key, value in update_data.items():
            setattr(project, key, value)
        self.db.commit()
        self.db.refresh(project)
        return project

    def delete(self, project: Project) -> None:
        project.is_active = False
        self.db.commit()
