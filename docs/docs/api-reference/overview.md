---
sidebar_position: 1
title: API Overview
---

# API Reference

Codalyra-AI exposes a RESTful API at `/api/v1` with 18 routers. All endpoints return JSON.

## Base URL

```
http://localhost:8000/api/v1    # Local development
https://your-domain.com/api/v1  # Production
```

## Authentication

Most endpoints require a JWT Bearer token:

```
Authorization: Bearer <token>
```

Get a token via `POST /api/v1/auth/login` or `POST /api/v1/auth/register`.

## Routers

| Router | Prefix | Auth Required | Description |
|--------|--------|---------------|-------------|
| **health** | `/health` | No | Health check |
| **auth** | `/auth` | No (login/register) | Authentication & GitHub OAuth |
| **users** | `/users` | Yes | User profile management |
| **projects** | `/projects` | Yes | Project CRUD |
| **repositories** | `/repositories` | Yes | GitHub repository linking |
| **reviews** | `/reviews` | Yes | Submit and manage reviews |
| **tasks** | `/tasks` | Yes | View review tasks |
| **runs** | `/runs` | Yes | View agent runs |
| **evaluations** | `/evaluations` | Yes | View findings/evaluations |
| **trajectories** | `/trajectories` | Yes | View execution traces |
| **github** | `/github` | Yes | GitHub repos, PRs, diffs, webhooks |
| **settings** | `/settings` | Yes | API keys, preferences |
| **analytics** | `/analytics` | Yes | Score trends, agent performance |
| **exports** | `/exports` | Yes | Markdown report export |
| **agent_configs** | `/agent-configs` | Yes | Per-agent LLM configuration |
| **teams** | `/teams` | Yes | Team management |
| **custom_rules** | `/custom-rules` | Yes | Custom regex rules |
| **feedback** | `/feedback` | Yes | Finding feedback (accept/dismiss) |
| **ws** | `/ws` | No | WebSocket for real-time updates |

## Common Response Patterns

### Success

```json
{
  "id": "uuid",
  "name": "My Project",
  "created_at": "2026-09-17T10:30:00Z"
}
```

### Error

```json
{
  "detail": "Project not found"
}
```

### Paginated List

```json
[
  {"id": "uuid-1", "name": "Project 1"},
  {"id": "uuid-2", "name": "Project 2"}
]
```

## Auto-Generated Docs

FastAPI generates interactive API documentation automatically:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

These include all endpoints, request/response schemas, and the ability to try endpoints directly.
