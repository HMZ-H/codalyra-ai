---
sidebar_position: 2
title: Environment Variables
---

# Environment Variables

All configuration is via environment variables, loaded by Pydantic Settings from a `.env` file.

## Required Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `postgresql://codalyra:codalyra@localhost:5432/codalyra` | PostgreSQL connection string |
| `REDIS_URL` | `redis://localhost:6379/0` | Redis connection string |
| `SECRET_KEY` | `change-me-in-production` | **Must change.** Used for JWT signing and API key encryption |

## LLM Providers

| Variable | Default | Description |
|----------|---------|-------------|
| `GEMINI_API_KEY` | — | Google Gemini API key (required for reviews) |
| `GEMINI_MODEL` | `gemini-3.6-flash` | Default Gemini model |

Users can also add OpenAI and Anthropic keys via the Settings UI. These are stored encrypted in the database, not as env vars.

## GitHub OAuth

| Variable | Default | Description |
|----------|---------|-------------|
| `GITHUB_CLIENT_ID` | — | GitHub OAuth App client ID |
| `GITHUB_CLIENT_SECRET` | — | GitHub OAuth App client secret |
| `GITHUB_REDIRECT_URI` | `http://localhost:5173/auth/github/callback` | OAuth redirect URI |
| `GITHUB_WEBHOOK_SECRET` | — | HMAC secret for webhook verification |

## Notifications

| Variable | Default | Description |
|----------|---------|-------------|
| `SLACK_WEBHOOK_URL` | — | Slack Incoming Webhook URL |
| `DISCORD_WEBHOOK_URL` | — | Discord Webhook URL |

## JWT Settings

| Variable | Default | Description |
|----------|---------|-------------|
| `ALGORITHM` | `HS256` | JWT signing algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | Token lifetime in minutes |

## Frontend Variables

Set in `frontend/.env`:

| Variable | Default | Description |
|----------|---------|-------------|
| `VITE_API_BASE_URL` | `/api/v1` | API base URL. Set to `http://localhost:8000/api/v1` for local dev |
| `VITE_GITHUB_CLIENT_ID` | — | GitHub OAuth App client ID (same as backend) |

## Docker Compose Overrides

In Docker Compose, the `environment` section overrides `.env` values:

```yaml
api:
  environment:
    DATABASE_URL: postgresql://codalyra:codalyra@postgres:5432/codalyra
    REDIS_URL: redis://redis:6379/0
```

This ensures the API connects to the container-internal hostnames (`postgres`, `redis`) regardless of what's in the `.env` file.

## Example .env File

```bash
# Database
DATABASE_URL=postgresql://codalyra:codalyra@localhost:5432/codalyra
REDIS_URL=redis://localhost:6379/0

# Security (CHANGE THESE IN PRODUCTION)
SECRET_KEY=your-random-secret-key-here

# LLM
GEMINI_API_KEY=your-gemini-api-key

# GitHub OAuth (optional)
GITHUB_CLIENT_ID=
GITHUB_CLIENT_SECRET=
GITHUB_WEBHOOK_SECRET=

# Notifications (optional)
SLACK_WEBHOOK_URL=
DISCORD_WEBHOOK_URL=
```
