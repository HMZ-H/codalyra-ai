import logging

import httpx

from app.config import settings

logger = logging.getLogger(__name__)

GITHUB_API = "https://api.github.com"


class GitHubService:
    def __init__(self, token: str):
        self.token = token
        self.headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json",
        }

    @staticmethod
    async def exchange_code_for_token(code: str) -> dict:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                "https://github.com/login/oauth/access_token",
                json={
                    "client_id": settings.GITHUB_CLIENT_ID,
                    "client_secret": settings.GITHUB_CLIENT_SECRET,
                    "code": code,
                },
                headers={"Accept": "application/json"},
            )
            resp.raise_for_status()
            data = resp.json()
            if "error" in data:
                raise ValueError(f"GitHub OAuth error: {data['error_description']}")
            return data

    @staticmethod
    async def get_github_user(access_token: str) -> dict:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{GITHUB_API}/user",
                headers={
                    "Authorization": f"token {access_token}",
                    "Accept": "application/vnd.github.v3+json",
                },
            )
            resp.raise_for_status()
            return resp.json()

    @staticmethod
    async def get_user_emails(access_token: str) -> list[dict]:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{GITHUB_API}/user/emails",
                headers={
                    "Authorization": f"token {access_token}",
                    "Accept": "application/vnd.github.v3+json",
                },
            )
            resp.raise_for_status()
            return resp.json()

    def _get(self, path: str, params: dict | None = None) -> dict | list:
        with httpx.Client() as client:
            resp = client.get(f"{GITHUB_API}{path}", headers=self.headers, params=params)
            resp.raise_for_status()
            return resp.json()

    def _post(self, path: str, json: dict | None = None) -> dict:
        with httpx.Client() as client:
            resp = client.post(f"{GITHUB_API}{path}", headers=self.headers, json=json)
            resp.raise_for_status()
            return resp.json()

    def list_repos(self, page: int = 1, per_page: int = 30) -> list[dict]:
        repos = self._get("/user/repos", params={
            "sort": "updated",
            "direction": "desc",
            "per_page": per_page,
            "page": page,
            "type": "owner",
        })
        return [
            {
                "github_id": r["id"],
                "name": r["name"],
                "full_name": r["full_name"],
                "url": r["html_url"],
                "clone_url": r["clone_url"],
                "default_branch": r["default_branch"],
                "language": r.get("language"),
                "private": r["private"],
                "description": r.get("description"),
                "updated_at": r["updated_at"],
            }
            for r in repos
        ]

    def list_pulls(self, owner: str, repo: str, state: str = "open") -> list[dict]:
        pulls = self._get(f"/repos/{owner}/{repo}/pulls", params={"state": state, "per_page": 30})
        return [
            {
                "number": pr["number"],
                "title": pr["title"],
                "state": pr["state"],
                "user": pr["user"]["login"],
                "url": pr["html_url"],
                "created_at": pr["created_at"],
                "updated_at": pr["updated_at"],
                "head_sha": pr["head"]["sha"],
                "base_branch": pr["base"]["ref"],
                "head_branch": pr["head"]["ref"],
                "additions": pr.get("additions"),
                "deletions": pr.get("deletions"),
                "changed_files": pr.get("changed_files"),
            }
            for pr in pulls
        ]

    def get_pull_diff(self, owner: str, repo: str, pr_number: int) -> str:
        with httpx.Client() as client:
            resp = client.get(
                f"{GITHUB_API}/repos/{owner}/{repo}/pulls/{pr_number}",
                headers={**self.headers, "Accept": "application/vnd.github.v3.diff"},
            )
            resp.raise_for_status()
            return resp.text

    def post_review_comment(self, owner: str, repo: str, pr_number: int, body: str) -> dict:
        return self._post(
            f"/repos/{owner}/{repo}/issues/{pr_number}/comments",
            json={"body": body},
        )

    def post_inline_comments(self, owner: str, repo: str, pr_number: int, commit_sha: str, comments: list[dict]) -> dict:
        return self._post(
            f"/repos/{owner}/{repo}/pulls/{pr_number}/reviews",
            json={
                "commit_id": commit_sha,
                "event": "COMMENT",
                "comments": comments,
            },
        )
