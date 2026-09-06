import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.permissions import verify_run_owner, verify_task_owner
from app.database.models.user import User
from app.database.session import get_db
from app.dependencies import get_current_active_user
from app.repositories.run_repository import RunRepository
from app.schemas.run import RunCreate, RunResponse

router = APIRouter(prefix="/runs", tags=["runs"])


@router.post("/", response_model=RunResponse, status_code=201)
def create_run(
    run_data: RunCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> RunResponse:
    verify_task_owner(db, run_data.task_id, current_user.id)
    repo = RunRepository(db)
    run = repo.create(run_data.model_dump())
    return run


@router.get("/", response_model=list[RunResponse])
def list_runs(
    task_id: uuid.UUID = Query(...),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> list[RunResponse]:
    verify_task_owner(db, task_id, current_user.id)
    repo = RunRepository(db)
    return repo.get_by_task(task_id, skip=skip, limit=limit)


@router.get("/{run_id}", response_model=RunResponse)
def get_run(
    run_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> RunResponse:
    verify_run_owner(db, run_id, current_user.id)
    repo = RunRepository(db)
    run = repo.get_by_id(run_id)
    if not run:
        from app.core.exceptions import NotFoundException
        raise NotFoundException("Run not found")
    return run


@router.post("/{run_id}/execute", response_model=dict)
def execute_run(
    run_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> dict:
    verify_run_owner(db, run_id, current_user.id)
    from app.workers.execution_tasks import execute_agent
    execute_agent.delay(str(run_id))
    return {"status": "queued", "run_id": str(run_id)}


@router.post("/{run_id}/evaluate", response_model=dict)
def evaluate_run_endpoint(
    run_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> dict:
    verify_run_owner(db, run_id, current_user.id)
    from app.workers.evaluation_tasks import evaluate_run
    evaluate_run.delay(str(run_id))
    return {"status": "queued", "run_id": str(run_id)}
