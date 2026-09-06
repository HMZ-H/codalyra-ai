from app.services.github_service import GitHubService
from app.workers.celery_app import celery_app


@celery_app.task(bind=True, max_retries=3)
def setup_repos(self, repo_id: str):
    return GitHubService.fetch_repos(repo_id)

