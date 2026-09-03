# Codalyra-AI: Agentic PR Review Pipeline

A multi-agent code review system where 4 specialized AI agents analyze a code diff from different angles, then a synthesis agent combines their findings into a unified, prioritized report — with a built-in single-prompt baseline for measurable comparison.

## The Problem

**Who has this problem?** Developers and engineering teams who review pull requests daily.

**What bottleneck makes it worth solving?** Code reviews are:
- **Slow** — reviewers take hours to days, blocking merge queues
- **Inconsistent** — different reviewers catch different things
- **Shallow** — humans focus on style/naming and miss subtle bugs, security issues, or performance problems
- **Single-perspective** — one reviewer cannot simultaneously think like a security engineer, a performance engineer, and a quality expert

A single AI prompt reviewing code suffers from the same problem — it tries to do everything at once and misses specialized concerns.

## The Solution: Multi-Agent Specialization

```
                     ┌──────────────┐
                     │  Code Diff   │
                     └──────┬───────┘
                            │
              ┌─────────────┼─────────────┐
              │             │             │
     ┌────────▼──┐  ┌──────▼──────┐  ┌───▼─────────┐  ┌────────────┐
     │  Logic    │  │  Security   │  │ Performance │  │  Quality   │
     │  Agent    │  │  Agent      │  │ Agent       │  │  Agent     │
     └────────┬──┘  └──────┬──────┘  └───┬─────────┘  └─────┬──────┘
              │            │             │                   │
              └────────────┼─────────────┘                   │
                           │                                 │
                    ┌──────▼──────┐                          │
                    │  Synthesis  │◄─────────────────────────┘
                    │  Agent      │
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │  Unified    │
                    │  Report     │
                    └─────────────┘
```

**5 agents, each with a clear purpose:**

| Agent | Focus | What It Catches |
|-------|-------|-----------------|
| **Logic** | Correctness bugs | Off-by-one, null deref, race conditions, wrong operators |
| **Security** | Vulnerabilities | SQL injection, XSS, hardcoded secrets, command injection |
| **Performance** | Efficiency | N+1 queries, O(n²), resource leaks, blocking I/O |
| **Quality** | Maintainability | DRY violations, dead code, poor naming, magic numbers |
| **Synthesis** | Orchestration | Deduplicates, prioritizes, produces unified scored report |

**Plus:** Static validators (regex-based) run first and pass preliminary findings to LLM agents as context — a "tool use" dimension that improves precision.

**Baseline comparison built in:** Every review also runs a single-prompt baseline in parallel, so improvement is measurable on every single review.

## Tech Stack

| Component | Technology |
|-----------|-----------|
| API | FastAPI |
| ORM | SQLAlchemy 2.0 |
| Database | PostgreSQL 16 |
| Queue | Redis 7 + Celery |
| LLM | Google Gemini (gemini-3.6-flash) |
| Auth | JWT + bcrypt |
| Frontend | React 19 + Vite |

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.12+ with `uv`
- Node.js 20+
- A Google Gemini API key

### Setup

```bash
# 1. Clone
git clone https://github.com/HMZ-H/codalyra-ai.git
cd codalyra-ai

# 2. Start PostgreSQL & Redis
docker compose up -d

# 3. Backend setup
cd backend
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
uv sync
uv run alembic upgrade head
uv run fastapi dev app/main.py

# 4. Start Celery worker (separate terminal)
cd backend
uv run celery -A app.workers.celery_app worker -l info -c 4

# 5. Frontend (separate terminal)
cd frontend
npm install
npm run dev
```

### Demo

1. Open http://localhost:5173
2. Register an account
3. Create a project
4. Click **"Review Code"** on the dashboard
5. Paste a diff (or click "Load Sample Diff" for a pre-loaded example with SQL injection + hardcoded secrets)
6. Watch the 5 agents analyze your code in real-time
7. View the unified report with severity-coded findings and baseline comparison

### Run Evaluation

```bash
cd backend
GEMINI_API_KEY=your-key python -m app.scripts.run_evaluation
```

Runs both multi-agent and single-prompt baseline on 5 curated diffs and outputs comparison metrics.

## Improvement Changelog

| Stage | What & Why | Evidence | Decision |
|-------|-----------|----------|----------|
| **Baseline** | Single Gemini prompt reviewing the full diff | Catches obvious issues but misses specialized concerns | Starting point |
| **Iteration 1** | Split into 4 specialized agents (logic, security, perf, quality) | Higher recall — each agent focuses deeply on its domain | Kept — specialization works |
| **Iteration 2** | Added static validators as pre-scan | Regex catches hardcoded secrets + dangerous calls that LLMs sometimes miss | Kept — cheap, fast, reliable first pass |
| **Iteration 3** | Added synthesis agent to combine findings | Eliminates duplicates, assigns consistent severity, produces coherent report | Kept — key quality improvement |
| **Iteration 4** | Pass static findings as context to LLM agents | Agents can confirm/refine static findings rather than rediscovering them | Kept — improves precision |
| **Final** | Complete pipeline: static → 4 specialists (parallel) → synthesis | Multi-agent catches more issues with better categorization vs single prompt | Main contribution: specialization + orchestration |

## Architecture

### Core Platform
- FastAPI backend with 8+ SQLAlchemy models (User, Project, Repository, Task, Run, Review, Checkpoint, Trajectory, Evaluation)
- JWT authentication with bcrypt password hashing
- CRUD APIs for all entities with ownership enforcement
- Celery task queue with parallel agent execution workers
- React frontend with dashboard, project management, and review visualization

### Multi-Agent Review Layer
- **Review model** — groups multiple agent runs into one review
- **AI layer** — Gemini client with JSON mode, 6 specialized prompt templates, agent reviewer, finding analyzer
- **Static validators** — 12 security regex patterns + 6 Python code smell patterns
- **Review workers** — Celery tasks orchestrating parallel agent execution + synthesis triggering
- **Review API** — submit, list, get, report endpoints
- **ReviewDetail page** — pipeline visualization, score gauge, findings display, baseline comparison
- **ReviewSubmit modal** — diff input with sample loading
- **Evaluation script** — automated benchmark comparison across sample diffs

## Design Philosophy

Single-agent code review is fundamentally limited because reviewing code requires holding multiple conflicting mental models simultaneously. A security mindset is adversarial to the code. A performance mindset is sympathetic to the machine. A quality mindset is sympathetic to the next developer. No single prompt can authentically adopt all four stances — it compromises on depth to cover breadth.

Multi-agent specialization mirrors how expert human teams actually work. The key insight is that the synthesis agent is more important than the specialists — without deduplication and prioritization, multi-agent review produces noise, not signal. The orchestration is the product.

**Approximate runtime:** Each review takes ~20-40 seconds (5 LLM calls in parallel + 1 synthesis).
**Approximate cost:** ~$0.01-0.03 per review with Gemini Flash pricing.

## License

MIT
