---
sidebar_position: 3
title: CI/CD Pipeline
---

# CI/CD Pipeline

Codalyra uses GitHub Actions for continuous integration. The pipeline runs on every push and pull request to `main`.

## Pipeline Overview

```
push/PR to main
    │
    ├── backend-lint (ruff check)
    ├── backend-test (pytest)
    ├── frontend-lint (oxlint)
    └── frontend-test (vitest)
            │
            ├── frontend-build (vite build) ← depends on lint + test
            └── docker-build (docker compose build) ← depends on backend-test + frontend-build
```

## Jobs

### 1. Backend Lint

```yaml
backend-lint:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4
    - uses: actions/setup-python@v5
      with:
        python-version: "3.12"
    - run: pip install ruff
    - run: ruff check .
      working-directory: backend
```

Ruff checks Python code for errors (E), pyflakes (F), import sorting (I), and modern syntax (UP). Configuration is in `backend/ruff.toml`.

### 2. Backend Test

```yaml
backend-test:
  runs-on: ubuntu-latest
  steps:
    - run: pip install -r requirements.txt
    - run: pytest app/tests/ -v
      working-directory: backend
```

126 tests with SQLite in-memory database.

### 3. Frontend Lint

```yaml
frontend-lint:
  runs-on: ubuntu-latest
  steps:
    - run: npm ci
    - run: npx oxlint
      working-directory: frontend
```

### 4. Frontend Test

```yaml
frontend-test:
  runs-on: ubuntu-latest
  steps:
    - run: npm ci
    - run: npm test
      working-directory: frontend
```

47 Vitest tests with jsdom.

### 5. Frontend Build

Depends on `frontend-lint` and `frontend-test`. Runs `vite build` to verify the production build succeeds.

### 6. Docker Build

Depends on `backend-test` and `frontend-build`. Runs `docker compose build` to verify all Docker images build successfully.

## Ruff Configuration

```toml
# backend/ruff.toml
line-length = 200

[lint]
select = ["E", "F", "I", "UP"]
ignore = ["F401", "F821", "UP007", "UP017", "UP035", "UP041", "E712"]

[lint.per-file-ignores]
"alembic/*" = ["ALL"]
"app/tests/*" = ["ALL"]

[lint.isort]
known-first-party = ["app"]
```

Key decisions:
- **Line length 200** — Avoids breaking long strings and formatted output
- **Ignore F401** — Unused imports in `__init__.py` re-exports are intentional
- **Ignore E712** — SQLAlchemy uses `== True`/`== False` for column comparisons
- **Exclude alembic/tests** — Auto-generated code and test files have different standards
