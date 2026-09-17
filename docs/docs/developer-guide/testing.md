---
sidebar_position: 8
title: Testing
---

# Testing Strategy

Codalyra has **173 tests** across backend (pytest) and frontend (Vitest).

## Backend Tests (126 tests)

### Running

```bash
cd backend
source .venv/bin/activate
pytest app/tests/ -v
```

### Test Structure

```
app/tests/
├── conftest.py                    # Shared fixtures (SQLite in-memory DB)
├── test_auth.py                   # Auth endpoints + JWT
├── test_projects.py               # CRUD + ownership
├── test_reviews.py                # Review creation + pipeline
├── test_review_pipeline.py        # Full integration test
├── test_github.py                 # GitHub OAuth + webhooks
├── test_feedback.py               # Finding feedback + accuracy
├── test_custom_rules.py           # Rule CRUD + execution
├── test_teams.py                  # Team management + roles
├── test_analytics.py              # Score trends + category breakdown
├── test_ai_client.py              # LLM provider mocking
├── test_validators.py             # Static analysis validators
├── test_scoring.py                # Score calculation
└── test_encryption.py             # Fernet encrypt/decrypt
```

### Test Database

Tests use **SQLite in-memory** via `conftest.py`:

```python
@pytest.fixture
def db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    session = Session(engine)
    yield session
    session.close()
```

This gives instant setup/teardown without needing PostgreSQL. The tradeoff: PostgreSQL-specific features (JSONB) aren't fully exercised.

### Mocking LLM Calls

The pipeline integration test mocks the LLM client to avoid real API calls:

```python
@patch("app.ai.client.LLMClient.chat_json")
def test_full_pipeline(mock_llm, db):
    mock_llm.return_value = {
        "findings": [
            {"file": "app.py", "line": 10, "severity": "critical", ...}
        ]
    }
    # Test the full flow without API costs
```

## Frontend Tests (47 tests)

### Running

```bash
cd frontend
npm test
```

### Test Structure

```
src/__tests__/
├── setup.js                       # @testing-library/jest-dom
├── Login.test.jsx                 # Form, submission, GitHub button
├── Dashboard.test.jsx             # Loading, empty state, project cards
├── Settings.test.jsx              # Provider sections, save states
├── AuthContext.test.jsx           # Token loading, login/logout
└── ApiClient.test.js              # All 14 API modules (mocked Axios)
```

### Tools

- **Vitest** — Test runner (Jest-compatible, Vite-native)
- **React Testing Library** — Component rendering + user event simulation
- **jsdom** — Browser environment simulation

### Philosophy

Tests verify **behavior**, not implementation:

```jsx
// Good: tests what the user sees
expect(screen.getByText('Sign In')).toBeInTheDocument();
await userEvent.click(submitButton);
expect(mockLogin).toHaveBeenCalledWith('user@test.com', 'pass');

// Bad: tests implementation details
expect(component.state.loading).toBe(true);
```

## CI Integration

All tests run in GitHub Actions on every push and PR:

```yaml
backend-test:
  runs-on: ubuntu-latest
  steps:
    - run: pip install -r requirements.txt
    - run: pytest app/tests/ -v

frontend-test:
  runs-on: ubuntu-latest
  steps:
    - run: npm ci
    - run: npm test
```

Tests must pass before the Docker build job runs.

## Known Gaps

1. **No E2E tests** — No Playwright/Cypress for full user flows
2. **Partial frontend coverage** — ReviewDetail, Analytics, CustomRules pages untested
3. **No load testing** — No throughput benchmarks under concurrent reviews
4. **No database integration tests** — SQLite doesn't catch PostgreSQL-specific issues
