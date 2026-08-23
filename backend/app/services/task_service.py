import uuid

from sqlalchemy.orm import Session

from app.core.exceptions import ForbiddenException, NotFoundException
from app.database.models.task import Task
from app.repositories.task_repository import TaskRepository
from app.schemas.task import TaskCreate, TaskUpdate


class TaskService:
    def __init__(self, db: Session):
        self.repo = TaskRepository(db)

    def create_task(self, task_data: TaskCreate, user_id: uuid.UUID) -> Task:
        return self.repo.create({
            "title": task_data.title,
            "description": task_data.description,
            "project_id": task_data.project_id,
            "repository_id": task_data.repository_id,
            "created_by_id": user_id,
            "language": task_data.language,
            "difficulty": task_data.difficulty,
            "expected_output": task_data.expected_output,
            "test_command": task_data.test_command,
            "time_limit_seconds": task_data.time_limit_seconds,
        })

    def get_task(self, task_id: uuid.UUID) -> Task:
        task = self.repo.get_by_id(task_id)
        if not task:
            raise NotFoundException("Task not found")
        return task

    def list_tasks(self, project_id: uuid.UUID, skip: int = 0, limit: int = 20) -> list[Task]:
        return self.repo.get_by_project(project_id, skip=skip, limit=limit)

    def update_task(self, task_id: uuid.UUID, update_data: TaskUpdate, user_id: uuid.UUID) -> Task:
        task = self.get_task(task_id)
        self._check_ownership(task, user_id)
        data = update_data.model_dump(exclude_unset=True)
        if not data:
            return task
        return self.repo.update(task, data)

    def delete_task(self, task_id: uuid.UUID, user_id: uuid.UUID) -> None:
        task = self.get_task(task_id)
        self._check_ownership(task, user_id)
        self.repo.delete(task)

    def _check_ownership(self, task: Task, user_id: uuid.UUID) -> None:
        if task.created_by_id != user_id:
            raise ForbiddenException("You do not own this task")
