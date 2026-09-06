import uuid

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.permissions import verify_run_owner
from app.database.models.evaluation import Evaluation
from app.database.models.user import User
from app.database.session import get_db
from app.dependencies import get_current_active_user
from app.schemas.evaluation import EvaluationResponse

router = APIRouter(prefix="/evaluations", tags=["evaluations"])


@router.get("/run/{run_id}", response_model=EvaluationResponse | None)
def get_evaluation_by_run(
    run_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> EvaluationResponse | None:
    verify_run_owner(db, run_id, current_user.id)
    stmt = select(Evaluation).where(Evaluation.run_id == run_id)
    return db.scalars(stmt).first()
