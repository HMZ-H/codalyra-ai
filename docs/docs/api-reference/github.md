---
sidebar_position: 5
title: GitHub
---

# GitHub API

## List Repositories

```http
GET /api/v1/github/repos
Authorization: Bearer <token>
```

Returns the user's accessible GitHub repositories (requires connected GitHub account).

## List Pull Requests

```http
GET /api/v1/github/repos/{owner}/{repo}/pulls
Authorization: Bearer <token>
```

Returns open pull requests for the specified repository.

## Get PR Diff

```http
GET /api/v1/github/repos/{owner}/{repo}/pulls/{pull_number}/diff
Authorization: Bearer <token>
```

Returns the unified diff for a pull request.

## Post PR Comment

```http
POST /api/v1/github/repos/{owner}/{repo}/pulls/{pull_number}/comments
Authorization: Bearer <token>
Content-Type: application/json

{
  "body": "## Review Results\n\nScore: 85/100\n..."
}
```

Posts a formatted comment to the pull request.

## Webhook Handler

```http
POST /api/v1/github/webhook
X-Hub-Signature-256: sha256=<hex-digest>
X-GitHub-Event: pull_request
Content-Type: application/json

{
  "action": "opened",
  "pull_request": { ... },
  "sender": { "id": 12345 }
}
```

**Verification**: The webhook handler computes `HMAC-SHA256(secret, body)` and compares with the `X-Hub-Signature-256` header using constant-time comparison.

**Supported events**:

| Event | Action | Behavior |
|-------|--------|----------|
| `pull_request` | `opened` | Creates a new review |
| `pull_request` | `synchronize` | Creates a review for the updated diff |

**Skipped when**:
- Unknown sender (no matching GitHub ID in the database)
- User has no GitHub token stored
- Repository not connected to any project
- Diff exceeds size limit

**Response** (200):
```json
{
  "status": "review_created",
  "review_id": "uuid"
}
```

Or when skipped:
```json
{
  "status": "skipped",
  "reason": "No connected repository found"
}
```
