import hashlib
import hmac
import json
import logging
import uuid

from fastapi import APIRouter, Depends, Header, HTTPException, Query, Request
from sqlalchemy.orm import Session

from app.config import settings
from app.database.session import get_db
from app.dependencies import get_current_active_user
from app.database.models.user import User
from app.database.models.repository import Repository
from app.database.models.review import Review
from app.services.github_service import GitHubService
from app.services.review_service import ReviewService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/github", tags=["github"])


@router.get("/repos")
def list_github_repos(
    page: int = Query(1, ge=1),
    current_user: User = Depends(get_current_active_user),
):
    if not current_user.github_token:
        raise HTTPException(400, "GitHub account not connected")
    gh = GitHubService(current_user.github_token)
    return gh.list_repos(page=page)


@router.post("/repos/connect")
def connect_repo(
    data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    if not current_user.github_token:
        raise HTTPException(400, "GitHub account not connected")

    project_id = data.get("project_id")
    if not project_id:
        raise HTTPException(400, "project_id is required")

    repo = Repository(
        project_id=uuid.UUID(project_id),
        name=data["name"],
        url=data["url"],
        clone_url=data.get("clone_url"),
        default_branch=data.get("default_branch", "main"),
        language=data.get("language"),
    )
    db.add(repo)
    db.commit()
    db.refresh(repo)
    return {"id": str(repo.id), "name": repo.name, "url": repo.url}


@router.get("/repos/{owner}/{repo}/pulls")
def list_pulls(
    owner: str,
    repo: str,
    state: str = Query("open"),
    current_user: User = Depends(get_current_active_user),
):
    if not current_user.github_token:
        raise HTTPException(400, "GitHub account not connected")
    gh = GitHubService(current_user.github_token)
    return gh.list_pulls(owner, repo, state=state)


@router.get("/repos/{owner}/{repo}/pulls/{pr_number}/diff")
def get_pull_diff(
    owner: str,
    repo: str,
    pr_number: int,
    current_user: User = Depends(get_current_active_user),
):
    if not current_user.github_token:
        raise HTTPException(400, "GitHub account not connected")
    gh = GitHubService(current_user.github_token)
    diff = gh.get_pull_diff(owner, repo, pr_number)
    return {"diff": diff}


@router.post("/repos/{owner}/{repo}/pulls/{pr_number}/review")
def review_pull_request(
    owner: str,
    repo: str,
    pr_number: int,
    data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    if not current_user.github_token:
        raise HTTPException(400, "GitHub account not connected")

    project_id = data.get("project_id")
    if not project_id:
        raise HTTPException(400, "project_id is required")

    gh = GitHubService(current_user.github_token)
    diff = gh.get_pull_diff(owner, repo, pr_number)

    if len(diff) > 100_000:
        raise HTTPException(400, "Diff too large (max 100KB)")

    pr_title = f"PR #{pr_number} - {owner}/{repo}"
    review = ReviewService.create_review(
        db=db,
        project_id=uuid.UUID(project_id),
        created_by_id=current_user.id,
        diff_content=diff,
        pr_title=pr_title,
    )
    return {"review_id": str(review.id), "status": "started"}


@router.post("/repos/{owner}/{repo}/pulls/{pr_number}/post-comments")
def post_review_to_pr(
    owner: str,
    repo: str,
    pr_number: int,
    data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    if not current_user.github_token:
        raise HTTPException(400, "GitHub account not connected")

    review_id = data.get("review_id")
    if not review_id:
        raise HTTPException(400, "review_id is required")

    report = ReviewService.get_review_report(db, uuid.UUID(review_id))
    if not report:
        raise HTTPException(404, "Review not found")

    findings = report.get("findings", [])
    if not findings:
        raise HTTPException(400, "No findings to post")

    body = _format_review_comment(report)
    gh = GitHubService(current_user.github_token)
    result = gh.post_review_comment(owner, repo, pr_number, body)
    return {"comment_id": result.get("id"), "url": result.get("html_url")}


@router.post("/webhooks")
async def github_webhook(
    request: Request,
    db: Session = Depends(get_db),
    x_hub_signature_256: str | None = Header(None),
    x_github_event: str | None = Header(None),
):
    body = await request.body()

    if settings.GITHUB_WEBHOOK_SECRET:
        if not x_hub_signature_256:
            raise HTTPException(403, "Missing signature")
        expected = "sha256=" + hmac.new(
            settings.GITHUB_WEBHOOK_SECRET.encode(),
            body,
            hashlib.sha256,
        ).hexdigest()
        if not hmac.compare_digest(expected, x_hub_signature_256):
            raise HTTPException(403, "Invalid signature")

    payload = json.loads(body)

    if x_github_event == "pull_request" and payload.get("action") in ("opened", "synchronize"):
        pr = payload["pull_request"]
        repo_full = payload["repository"]["full_name"]
        owner, repo_name = repo_full.split("/")
        pr_number = pr["number"]
        sender_login = payload["sender"]["login"]

        from app.repositories.user_repository import UserRepository
        user_repo = UserRepository(db)
        user = user_repo.get_by_github_id(payload["sender"]["id"])
        if not user:
            logger.info(f"Webhook from unknown user {sender_login}, skipping")
            return {"status": "skipped", "reason": "unknown user"}

        if not user.github_token:
            return {"status": "skipped", "reason": "no github token"}

        db_repo = db.query(Repository).filter(
            Repository.url.contains(repo_full),
        ).first()
        if not db_repo:
            return {"status": "skipped", "reason": "repo not connected"}

        gh = GitHubService(user.github_token)
        diff = gh.get_pull_diff(owner, repo_name, pr_number)

        if len(diff) > 100_000:
            return {"status": "skipped", "reason": "diff too large"}

        review = ReviewService.create_review(
            db=db,
            project_id=db_repo.project_id,
            created_by_id=user.id,
            diff_content=diff,
            pr_title=f"PR #{pr_number}: {pr['title']}",
        )
        logger.info(f"Auto-review started for {repo_full}#{pr_number}: {review.id}")
        return {"status": "review_started", "review_id": str(review.id)}

    return {"status": "ignored", "event": x_github_event}


def _format_review_comment(report: dict) -> str:
    score = report.get("overall_score")
    summary = report.get("summary", "")
    findings = report.get("findings", [])

    lines = ["## Codalyra-AI Review Report\n"]
    if score is not None:
        emoji = "🟢" if score >= 80 else "🟡" if score >= 60 else "🔴"
        lines.append(f"**Quality Score:** {emoji} {score}/100\n")
    if summary:
        lines.append(f"{summary}\n")

    if findings:
        lines.append(f"### Findings ({len(findings)})\n")
        severity_emoji = {"critical": "🔴", "warning": "🟡", "info": "🔵"}
        for f in findings:
            sev = severity_emoji.get(f.get("severity", "info"), "⚪")
            file_loc = f.get("file", "")
            if f.get("line"):
                file_loc += f":{f['line']}"
            lines.append(f"- {sev} **{f.get('severity', 'info').upper()}** `{file_loc}` — {f.get('message', '')}")
            if f.get("suggestion"):
                lines.append(f"  - 💡 {f['suggestion']}")

    lines.append("\n---\n*Generated by [Codalyra-AI](https://github.com/HMZ-H/codalyra-ai)*")
    return "\n".join(lines)
