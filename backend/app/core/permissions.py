import uuid

from sqlalchemy.orm import Session

from app.core.exceptions import ForbiddenException, NotFoundException
from app.database.models.project import Project
from app.database.models.repository import Repository
from app.database.models.review import Review
from app.database.models.run import Run
from app.database.models.task import Task


def verify_project_owner(db: Session, project_id: uuid.UUID, user_id: uuid.UUID) -> Project:
    project = db.get(Project, project_id)
    if not project or not project.is_active:
        raise NotFoundException("Project not found")
    if project.owner_id != user_id:
        raise ForbiddenException("You do not own this project")
    return project


def verify_review_owner(db: Session, review_id: uuid.UUID, user_id: uuid.UUID) -> Review:
    review = db.get(Review, review_id)
    if not review:
        raise NotFoundException("Review not found")
    if review.created_by_id != user_id:
        project = db.get(Project, review.project_id)
        if not project or project.owner_id != user_id:
            raise ForbiddenException("You do not have access to this review")
    return review


def verify_task_owner(db: Session, task_id: uuid.UUID, user_id: uuid.UUID) -> Task:
    task = db.get(Task, task_id)
    if not task:
        raise NotFoundException("Task not found")
    if task.created_by_id != user_id:
        project = db.get(Project, task.project_id)
        if not project or project.owner_id != user_id:
            raise ForbiddenException("You do not have access to this task")
    return task


def verify_run_owner(db: Session, run_id: uuid.UUID, user_id: uuid.UUID) -> Run:
    run = db.get(Run, run_id)
    if not run:
        raise NotFoundException("Run not found")
    if run.review_id:
        review = db.get(Review, run.review_id)
        if review and review.created_by_id == user_id:
            return run
    task = db.get(Task, run.task_id)
    if not task:
        raise NotFoundException("Run not found")
    if task.created_by_id == user_id:
        return run
    project = db.get(Project, task.project_id)
    if not project or project.owner_id != user_id:
        raise ForbiddenException("You do not have access to this run")
    return run


def verify_repository_owner(db: Session, repo_id: uuid.UUID, user_id: uuid.UUID) -> Repository:
    repo = db.get(Repository, repo_id)
    if not repo or not repo.is_active:
        raise NotFoundException("Repository not found")
    project = db.get(Project, repo.project_id)
    if not project or project.owner_id != user_id:
        raise ForbiddenException("You do not have access to this repository")
    return repo
