import subprocess
import logging

from app.workers.celery_app import celery_app
from app.database.session import SessionLocal
from app.database.models.run import Run
from app.database.models.task import Task
from app.database.models.evaluation import Evaluation

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, max_retries=3)
def evaluate_run(self, run_id: str):
    db = SessionLocal()
    try:
        run = db.query(Run).filter(Run.id == run_id).first()
        if not run:
            raise ValueError(f"Run {run_id} not found")

        task = db.query(Task).filter(Task.id == run.task_id).first()

        tests_passed = 0
        tests_total = 0
        score = 0.0
        is_correct = False
        feedback = ""

        if task.test_command:
            result = subprocess.run(
                task.test_command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=task.time_limit_seconds,
            )
            tests_total = 1
            if result.returncode == 0:
                tests_passed = 1
                is_correct = True
                score = 1.0
                feedback = f"Tests passed.\n{result.stdout}"
            else:
                feedback = f"Tests failed.\n{result.stderr}"
        elif task.expected_output and run.metadata_:
            agent_output = run.metadata_.get("output", "")
            tests_total = 1
            if agent_output.strip() == task.expected_output.strip():
                tests_passed = 1
                is_correct = True
                score = 1.0
                feedback = "Output matches expected result."
            else:
                feedback = "Output does not match expected result."
        else:
            feedback = "No test command or expected output defined for this task."

        evaluation = Evaluation(
            run_id=run.id,
            tests_passed=tests_passed,
            tests_total=tests_total,
            score=score,
            is_correct=is_correct,
            feedback=feedback,
            evaluation_method="auto",
        )
        db.add(evaluation)

        run.status = "evaluated"
        db.commit()

        logger.info("Run %s evaluated: score=%.2f, passed=%d/%d", run_id, score, tests_passed, tests_total)
        return {"run_id": run_id, "score": score, "is_correct": is_correct}

    except subprocess.TimeoutExpired:
        db.rollback()
        run.status = "timeout"
        db.commit()
        logger.error("Evaluation timed out for run %s", run_id)
        return {"run_id": run_id, "error": "timeout"}

    except Exception as exc:
        db.rollback()
        logger.error("Evaluation failed for run %s: %s", run_id, exc)
        raise self.retry(exc=exc, countdown=30)

    finally:
        db.close()
