from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.models.trajectory import Trajectory


class TrajectoryService:

    def __init__(self, db: Session):
        self.db = db

    def get_by_run(self, run_id) -> list[Trajectory]:
        stmt = (
            select(Trajectory)
            .where(Trajectory.run_id == run_id)
            .order_by(Trajectory.sequence_number)
        )
        return list(self.db.scalars(stmt).all())

    def record(self, run_id, sequence_number: int, action_type: str,
               action_input: str | None = None, action_output: str | None = None,
               duration_ms: int | None = None) -> Trajectory:
        trajectory = Trajectory(
            run_id=run_id,
            sequence_number=sequence_number,
            action_type=action_type,
            action_input=action_input,
            action_output=action_output,
            duration_ms=duration_ms,
        )
        self.db.add(trajectory)
        self.db.commit()
        self.db.refresh(trajectory)
        return trajectory

    def count_by_run(self, run_id) -> int:
        stmt = select(Trajectory).where(Trajectory.run_id == run_id)
        return len(list(self.db.scalars(stmt).all()))
