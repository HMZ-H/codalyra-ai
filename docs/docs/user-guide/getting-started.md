---
sidebar_position: 1
title: Getting Started
---

# Getting Started with Codalyra-AI

Codalyra-AI is a multi-agent AI code review system that analyzes pull request diffs using 4 specialized agents, then synthesizes their findings into a unified scored report.

## How It Works

Instead of one generic AI prompt reviewing your code, Codalyra dispatches your diff to **4 specialist agents** running in parallel:

| Agent | Focus | What It Catches |
|-------|-------|----------------|
| **Logic** | Correctness | Off-by-one errors, null derefs, race conditions |
| **Security** | Vulnerabilities | SQL injection, XSS, hardcoded secrets, OWASP Top 10 |
| **Performance** | Efficiency | N+1 queries, O(n²) loops, resource leaks |
| **Quality** | Maintainability | DRY violations, dead code, poor naming |

A **synthesis agent** then merges, deduplicates, and prioritizes all findings into a single scored report. A **baseline** single-pass review runs alongside for comparison.

## Quick Start

### Option 1: Docker Compose (Recommended)

```bash
git clone https://github.com/HMZ-H/codalyra-ai.git
cd codalyra-ai

# Configure
cp backend/.env.example backend/.env
# Edit backend/.env — set GEMINI_API_KEY and SECRET_KEY

# Launch all 5 services
docker compose up --build

# Open http://localhost:3000
```

### Option 2: Local Development

```bash
# 1. Start infrastructure
docker compose up -d postgres redis

# 2. Backend
cd backend
cp .env.example .env
# Edit .env — add GEMINI_API_KEY, set DATABASE_URL
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --port 8000

# 3. Celery worker (separate terminal)
cd backend && source .venv/bin/activate
celery -A app.workers.celery_app worker -l info -c 2

# 4. Frontend (separate terminal)
cd frontend
cp .env.example .env
npm install
npm run dev
```

## First Review

1. **Register** an account at `/register` or sign in with GitHub
2. **Create a project** from the Dashboard
3. **Submit a review** — paste a code diff or connect a GitHub repository
4. **View the report** — see findings from each agent, the synthesized score, and auto-fix suggestions

## What You'll Need

- **Docker** and **Docker Compose** (for Docker setup)
- **Python 3.12+**, **Node 20+**, **PostgreSQL 16**, **Redis 7** (for local setup)
- A **Gemini API key** (free tier works) — get one at [ai.google.dev](https://ai.google.dev)
- Optional: **GitHub OAuth App** credentials for GitHub integration
