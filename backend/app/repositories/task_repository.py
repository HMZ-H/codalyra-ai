import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database.models.task import Task


class TaskRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, task_id: uuid.UUID) -> Task | None:
        return self.db.get(Task, task_id)

    def get_by_project(self, project_id: uuid.UUID, skip: int = 0, limit: int = 100) -> list[Task]:
        stmt = (
            select(Task)
            .where(Task.project_id == project_id)
            .order_by(Task.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(self.db.scalars(stmt).all())

    def create(self, task_data: dict) -> Task:
        task = Task(**task_data)
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        return task

    def update(self, task: Task, update_data: dict) -> Task:
        for key, value in update_data.items():
            setattr(task, key, value)
        self.db.commit()
        self.db.refresh(task)
        return task

    def delete(self, task: Task) -> None:
        self.db.delete(task)
        self.db.commit()

    def count_by_project(self, project_id: uuid.UUID) -> int:
        stmt = select(func.count()).select_from(Task).where(Task.project_id == project_id)
        return self.db.scalar(stmt) or 0
