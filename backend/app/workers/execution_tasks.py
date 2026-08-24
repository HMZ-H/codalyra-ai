import asyncio

from app.workers.celery_app import celery_app
from app.services.execution_service import ExecutionService


@celery_app.task(bind=True, max_retries=3)
def execute_agent(self, run_id: str):
    return asyncio.run(ExecutionService.execute(run_id))