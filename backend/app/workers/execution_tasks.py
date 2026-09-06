import asyncio

from app.services.execution_service import ExecutionService
from app.workers.celery_app import celery_app


@celery_app.task(bind=True, max_retries=3)
def execute_agent(self, run_id: str):
    try:
        return asyncio.run(ExecutionService.execute(run_id))
    except Exception as exc:
        raise self.retry(exc=exc, countdown=10)