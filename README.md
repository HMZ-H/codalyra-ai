# Codalyra-AI

Backend platform for creating, running, validating, and evaluating AI coding-agent tasks in isolated, reproducible environments.

## What is this?

Codalyra-AI provides infrastructure to:
- **Create** coding tasks with difficulty ratings, test commands, and time limits
- **Execute** AI agents in isolated Docker sandboxes
- **Record** complete agent trajectories (every file read, edit, and command)
- **Evaluate** solutions with automated validators and AI-powered code review

## Tech Stack

| Component | Technology |
|-----------|-----------|
| API | FastAPI 0.141 |
| ORM | SQLAlchemy 2.0 |
| Database | PostgreSQL 16 |
| Cache/Queue | Redis 7 |
| Auth | JWT (python-jose) + bcrypt |
| Migrations | Alembic |
| Testing | pytest |
| Package Manager | uv |

## Quick Start

```bash
# Clone
git clone https://github.com/HMZ-H/codalyra-ai.git
cd codalyra-ai

# Environment
cp .env.example .env

# Start PostgreSQL & Redis
docker compose up -d

# Install dependencies
uv sync

# Run migrations
uv run alembic upgrade head

# Start dev server
uv run fastapi dev app/main.py
```

Open [http://localhost:8000/docs](http://localhost:8000/docs) for interactive API docs.

## API Endpoints

### Public
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/health` | Health check |
| `POST` | `/api/v1/auth/register` | Create account |
| `POST` | `/api/v1/auth/login` | Get JWT token |

### Protected (Bearer token required)
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/auth/me` | Current user |
| `CRUD` | `/api/v1/projects/` | Project management |
| `CRUD` | `/api/v1/repositories/` | Repository management |
| `CRUD` | `/api/v1/tasks/` | Task management |

## Project Structure

```
app/
  main.py              # FastAPI entry point
  config.py            # Settings (pydantic-settings)
  dependencies.py      # Auth dependencies
  api/v1/              # Route handlers
  core/                # Security, JWT, exceptions
  database/models/     # 8 SQLAlchemy models
  schemas/             # Pydantic validation
  repositories/        # Data access layer
  services/            # Business logic
  tests/               # 21 unit tests
  workers/             # Celery tasks (Phase 2)
  ai/                  # LLM integration (Phase 3)
  validators/          # Code validators (Phase 4)
```

## Data Model

**8 models:** User, Project, Repository, Task, Run, Checkpoint, Trajectory, Evaluation

```
User 1:N Project 1:N Repository
                 1:N Task 1:N Run 1:N Checkpoint
                                  1:N Trajectory
                                  1:1 Evaluation
```

## Development

```bash
# Run tests
uv run pytest

# Generate migration after model changes
uv run alembic revision --autogenerate -m "description"

# Apply migrations
uv run alembic upgrade head
```

## Roadmap

- [x] **Phase 1** - Backend Foundation (FastAPI, models, auth, CRUD, tests)
- [ ] **Phase 2** - Task Execution (Celery workers, Docker sandboxes, Git integration)
- [ ] **Phase 3** - Agent System (tool interface, trajectory recording, checkpoints)
- [ ] **Phase 4** - Evaluation (validators, hidden tests, AI reviewer, scoring)
- [ ] **Phase 5** - Reliability (retries, dead-letter queues, structured logging)
- [ ] **Phase 6** - Production (CI/CD, Kubernetes, Prometheus, Terraform)

## License

MIT
