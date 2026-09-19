import logging

from app.workers.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, max_retries=3)
def sync_repos(self, github_token: str, user_id: str):
    from app.services.github_service import GitHubService

    try:
        gh = GitHubService(github_token)
        repos = gh.list_repos(page=1, per_page=100)
        logger.info(f"Synced {len(repos)} repos for user {user_id}")
        return repos
    except Exception as exc:
        logger.error(f"Failed to sync repos for user {user_id}: {exc}")
        raise self.retry(exc=exc, countdown=30)
