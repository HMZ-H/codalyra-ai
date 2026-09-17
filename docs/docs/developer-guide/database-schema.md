---
sidebar_position: 6
title: Database Schema
---

# Database Schema

Codalyra uses PostgreSQL 16 with SQLAlchemy 2.0 ORM and Alembic migrations. The schema has 14 models across 12 migration versions.

## Entity Relationship

```
User ──┬── Project ──┬── Review ── Task ── Run ──┬── Evaluation
       │             │                            └── Trajectory
       │             ├── Repository
       │             ├── AgentConfig
       │             ├── CustomRule
       │             └── FindingFeedback
       │
       └── Team ── TeamMember
```

## Models

### User

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID | Primary key |
| `email` | String | Unique, required |
| `username` | String | Unique, required |
| `hashed_password` | String | bcrypt hash (nullable for OAuth-only users) |
| `github_id` | Integer | GitHub user ID (nullable) |
| `github_username` | String | GitHub login (nullable) |
| `github_token` | String | Encrypted GitHub access token |

### Project

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID | Primary key |
| `name` | String | Project name |
| `description` | String | Optional |
| `user_id` | UUID | FK → User (owner) |
| `team_id` | UUID | FK → Team (optional) |

### Review

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID | Primary key |
| `project_id` | UUID | FK → Project |
| `status` | String | `pending`, `running`, `completed`, `failed` |
| `diff_content` | Text | The submitted diff |
| `score` | Integer | 0–100, set by synthesis |
| `summary` | Text | Narrative summary |
| `baseline_score` | Integer | Single-pass baseline score |
| `baseline_findings_count` | Integer | Baseline finding count |

### Task

Links a review to its agent runs. One task per review.

### Run

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID | Primary key |
| `task_id` | UUID | FK → Task |
| `agent_type` | String | `logic`, `security`, `performance`, `quality`, `synthesis`, `baseline` |
| `status` | String | `pending`, `running`, `completed`, `failed` |
| `score` | Integer | Per-agent score |
| `duration_ms` | Integer | Execution time |

### Evaluation

Stores the findings JSON for a run. One evaluation per run.

| Column | Type | Description |
|--------|------|-------------|
| `run_id` | UUID | FK → Run |
| `findings` | JSON | Array of finding objects |
| `metadata` | JSON | LLM response metadata |

### Trajectory

Step-by-step execution trace for debugging and analysis.

### Repository

Links a GitHub repository to a project for PR browsing and webhooks.

### AgentConfig

Per-project, per-agent LLM configuration (provider, model, custom prompt, enable/disable).

### CustomRule

User-defined regex rules with pattern, severity, file filter, and suggestion.

### FindingFeedback

| Column | Type | Description |
|--------|------|-------------|
| `review_id` | UUID | FK → Review |
| `finding_hash` | String | SHA-256 of (file, line, category, message) |
| `action` | String | `accepted`, `dismissed`, `false_positive` |

Unique constraint on `(review_id, finding_hash)` prevents duplicate feedback.

### Team / TeamMember

Team with name/description. TeamMember joins User to Team with a role (`admin`, `reviewer`, `viewer`).

## Cascade Deletes

All foreign keys use `CASCADE`. Deleting a Project removes all Reviews → Tasks → Runs → Evaluations/Trajectories, plus Repositories, AgentConfigs, CustomRules, and FindingFeedback.

## Migrations

Alembic manages 12 versioned migration scripts. The API container runs `alembic upgrade head` on startup to ensure the schema is current.

```bash
# Create a new migration after model changes
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback one step
alembic downgrade -1
```
