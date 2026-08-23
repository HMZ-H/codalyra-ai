import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.models.run import Run


class RunRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, run_id: uuid.UUID) -> Run | None:
        return self.db.get(Run, run_id)

    def get_by_task(self, task_id: uuid.UUID, skip: int = 0, limit: int = 100) -> list[Run]:
        stmt = (
            select(Run)
            .where(Run.task_id == task_id)
            .order_by(Run.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(self.db.scalars(stmt).all())

    def create(self, run_data: dict) -> Run:
        run = Run(**run_data)
        self.db.add(run)
        self.db.commit()
        self.db.refresh(run)
        return run

    def update(self, run: Run, update_data: dict) -> Run:
        for key, value in update_data.items():
            setattr(run, key, value)
        self.db.commit()
        self.db.refresh(run)
        return run
