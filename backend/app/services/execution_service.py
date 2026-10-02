import logging
import shutil
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy.orm import Session

from app.database.models.checkpoint import Checkpoint
from app.database.models.repository import Repository
from app.database.models.run import Run
from app.database.models.task import Task
from app.database.models.trajectory import Trajectory
from app.database.session import SessionLocal

logger = logging.getLogger(__name__)


class ExecutionService:

    @staticmethod
    async def execute(run_id: str) -> dict:
        db = SessionLocal()
        workdir = None
        try:
            run = db.query(Run).filter(Run.id == run_id).first()
            if not run:
                raise ValueError(f"Run {run_id} not found")

            task = db.query(Task).filter(Task.id == run.task_id).first()
            repo = None
            if task.repository_id:
                repo = db.query(Repository).filter(Repository.id == task.repository_id).first()

            run.status = "running"
            run.started_at = datetime.now(timezone.utc)
            db.commit()

            workdir = Path(tempfile.mkdtemp(prefix=f"codalyra-run-{run_id[:8]}-"))

            if repo:
                clone_url = repo.clone_url or repo.url
                _clone_repo(clone_url, repo.default_branch, workdir)
                _record_trajectory(db, run.id, 1, "git_clone", clone_url, f"Cloned to {workdir}")

            if task.test_command:
                result = subprocess.run(
                    task.test_command,
                    shell=True,
                    cwd=str(workdir),
                    capture_output=True,
                    text=True,
                    timeout=task.time_limit_seconds,
                )
                _record_trajectory(
                    db, run.id, 2, "run_command",
                    task.test_command,
                    result.stdout + result.stderr,
                )
                run.exit_code = result.returncode

            completed_at = datetime.now(timezone.utc)
            run.status = "completed"
            run.completed_at = completed_at
            run.duration_seconds = (completed_at - run.started_at).total_seconds()
            db.commit()

            logger.info("Run %s completed in %.1fs", run_id, run.duration_seconds)
            return {"run_id": run_id, "status": "completed", "duration": run.duration_seconds}

        except subprocess.TimeoutExpired:
            run.status = "timeout"
            run.completed_at = datetime.now(timezone.utc)
            run.error_message = f"Exceeded time limit of {task.time_limit_seconds}s"
            db.commit()
            logger.warning("Run %s timed out", run_id)
            return {"run_id": run_id, "status": "timeout"}

        except Exception as exc:
            db.rollback()
            run = db.query(Run).filter(Run.id == run_id).first()
            if run:
                run.status = "failed"
                run.error_message = str(exc)
                run.completed_at = datetime.now(timezone.utc)
                db.commit()
            logger.error("Run %s failed: %s", run_id, exc)
            raise

        finally:
            db.close()
            if workdir and workdir.exists():
                shutil.rmtree(workdir, ignore_errors=True)


def _clone_repo(url: str, branch: str, dest: Path):
    subprocess.run(
        ["git", "clone", "--branch", branch, "--depth", "1", url, str(dest)],
        check=True,
        capture_output=True,
        text=True,
        timeout=120,
    )


def _record_trajectory(db: Session, run_id, seq: int, action_type: str, action_input: str, action_output: str):
    trajectory = Trajectory(
        run_id=run_id,
        sequence_number=seq,
        action_type=action_type,
        action_input=action_input,
        action_output=action_output,
    )
    db.add(trajectory)
    db.commit()
