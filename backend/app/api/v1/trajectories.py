import uuid
from datetime import datetime

from fastapi import APIRouter, Depends
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.permissions import verify_run_owner
from app.database.models.trajectory import Trajectory
from app.database.models.user import User
from app.database.session import get_db
from app.dependencies import get_current_active_user

router = APIRouter(prefix="/trajectories", tags=["trajectories"])


class TrajectoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    run_id: uuid.UUID
    sequence_number: int
    action_type: str
    action_input: str | None = None
    action_output: str | None = None
    timestamp: datetime
    duration_ms: int | None = None
    created_at: datetime


@router.get("/run/{run_id}", response_model=list[TrajectoryResponse])
def get_trajectories_by_run(
    run_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> list[TrajectoryResponse]:
    verify_run_owner(db, run_id, current_user.id)
    stmt = (
        select(Trajectory)
        .where(Trajectory.run_id == run_id)
        .order_by(Trajectory.sequence_number)
    )
    return list(db.scalars(stmt).all())
