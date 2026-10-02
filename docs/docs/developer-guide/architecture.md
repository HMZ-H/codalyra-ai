---
sidebar_position: 1
title: Architecture Overview
---

# Architecture Overview

Codalyra-AI is a full-stack application with a FastAPI backend, React frontend, PostgreSQL database, Redis message broker, and Celery workers.

## System Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          FRONTEND (React 19 + Vite)                     │
│  Login ─ Dashboard ─ ReviewDetail ─ Analytics ─ Teams ─ Settings       │
│  Nginx reverse proxy (/api/ → backend)                                  │
└──────────────────────────────┬──────────────────────────────────────────┘
                               │ Axios + JWT
┌──────────────────────────────▼──────────────────────────────────────────┐
│                        FASTAPI BACKEND (18 routers)                     │
│  Auth (JWT+OAuth) │ Reviews │ GitHub │ Analytics │ Teams │ Feedback     │
│  Rate Limiter │ Permissions │ Encrypted API Keys (Fernet)               │
└────────┬─────────────────────┬─────────────────────────┬───────────────┘
         │                     │                         │
    ┌────▼────┐          ┌─────▼──────┐           ┌─────▼──────┐
    │ Postgres │          │   Redis    │           │  Celery    │
    │  16      │          │   7        │           │  Workers   │
    │ 14 models│          │ broker +   │           │            │
    │ Alembic  │          │ rate limit │           │            │
    └──────────┘          └────────────┘           └─────┬──────┘
                                                         │
         ┌──────────────┬───────────────┬────────────────┤
         │              │               │                │
    ┌────▼─────┐  ┌─────▼─────┐  ┌─────▼──────┐  ┌─────▼─────┐
    │  Logic   │  │ Security  │  │Performance │  │ Quality   │
    │  Agent   │  │ Agent     │  │ Agent      │  │ Agent     │
    └────┬─────┘  └─────┬─────┘  └─────┬──────┘  └─────┬─────┘
         └──────────────┴───────┬───────┘                │
                         ┌──────▼──────┐                 │
                         │  Synthesis  │◄────────────────┘
                         │  Agent      │
                         └──────┬──────┘
                         ┌──────▼──────┐
                         │ Scored Report│
                         └─────────────┘
```

## Project Structure

```
codalyra-ai/
├── backend/
│   ├── alembic/versions/          # 12 migration scripts
│   ├── app/
│   │   ├── ai/                    # LLM clients, prompts, analysis, auto-fixer
│   │   ├── api/v1/                # 18 REST API routers
│   │   ├── core/                  # JWT, bcrypt, Fernet encryption, permissions
│   │   ├── database/models/       # 14 SQLAlchemy models
│   │   ├── middleware/            # Redis rate limiter
│   │   ├── repositories/         # Data access layer
│   │   ├── schemas/              # Pydantic validation models
│   │   ├── services/             # Business logic
│   │   ├── validators/           # Static analysis engines
│   │   ├── workers/              # Celery task definitions
│   │   └── tests/                # pytest test suites
│   ├── Dockerfile
│   └── ruff.toml                  # Linter config
├── frontend/
│   ├── src/
│   │   ├── api/                   # Axios client (14 API modules)
│   │   ├── components/            # Shared React components
│   │   ├── context/               # Auth context
│   │   ├── hooks/                 # WebSocket, theme hooks
│   │   ├── pages/                 # 14 pages
│   │   ├── styles/                # Global CSS
│   │   └── __tests__/             # Vitest test suites
│   ├── Dockerfile                 # Multi-stage build
│   └── nginx.conf                 # Reverse proxy config
├── docs/                          # This documentation site
├── docker-compose.yml             # 5 services
└── .github/workflows/ci.yml      # CI pipeline
```

## Technology Choices

| Layer | Technology | Why |
|-------|-----------|-----|
| Backend API | FastAPI (Python 3.12) | Async, dependency injection, auto OpenAPI |
| ORM | SQLAlchemy 2.0 | Type-safe models, relationships, migrations |
| Database | PostgreSQL 16 | JSONB for findings, robust FK constraints |
| Task Queue | Redis 7 + Celery | Parallel agent execution, reliable delivery |
| LLM | Gemini / OpenAI / Anthropic | Multi-provider with JSON mode |
| Migrations | Alembic | Version-controlled schema changes |
| Frontend | React 19 + Vite | Fast dev, modern JSX |
| Auth | JWT + bcrypt + GitHub OAuth | Stateless auth, secure passwords |
| Encryption | Fernet (SHA-256 derived) | API keys encrypted at rest |
| Containers | Docker Compose (5 services) | One-command deployment |
| CI/CD | GitHub Actions | Lint + test + build on every push |

## Design Principles

1. **Specialization over generalization** — Each agent focuses on one domain instead of a single prompt trying to cover everything.

2. **Synthesis is the product** — Without deduplication and prioritization, multi-agent review produces noise, not signal.

3. **Static before semantic** — Deterministic regex catches patterns cheaply; the LLM builds on those findings for deeper analysis.

4. **Fail gracefully** — One agent crashing doesn't kill the review. Redis going down doesn't block requests. Bad JSON gets retried.

5. **Measurable improvement** — The baseline comparison proves the multi-agent approach works, on every single review.
