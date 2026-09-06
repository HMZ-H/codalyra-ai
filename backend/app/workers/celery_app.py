from celery import Celery

from app.config import settings

celery_app = Celery(
    "codalyra_ai",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True
)

celery_app.conf.include = [
    "app.workers.review_tasks",
    "app.workers.execution_tasks",
    "app.workers.evaluation_tasks",
]
