---
sidebar_position: 4
title: Production Checklist
---

# Production Checklist

Before deploying Codalyra-AI to production, verify these items.

## Security (Critical)

- [ ] **Change `SECRET_KEY`** — Generate a random 64+ character string. This key signs JWTs and encrypts API keys. The default `change-me-in-production` is public.
  ```bash
  python -c "import secrets; print(secrets.token_urlsafe(64))"
  ```

- [ ] **Enable HTTPS** — JWT tokens over HTTP are vulnerable to interception. Use a reverse proxy (nginx, Caddy, Traefik) with TLS certificates.

- [ ] **Set `GITHUB_CLIENT_SECRET`** — Required for GitHub OAuth. Missing in many dev setups.

- [ ] **Remove default database password** — Change `codalyra:codalyra` to a strong password.

- [ ] **Restrict CORS origins** — Update `allow_origins` in `main.py` to your production domain only.

## Database

- [ ] **Use a managed PostgreSQL** — Neon, Supabase, RDS, or Cloud SQL for backups and high availability.

- [ ] **Run migrations** — Verify `alembic upgrade head` runs cleanly against your production database.

- [ ] **Set up connection pooling** — Consider pgBouncer for high-concurrency workloads.

## Infrastructure

- [ ] **Scale Celery workers** — Each worker handles one agent at a time. For N concurrent reviews, you need ~6N worker slots.
  ```bash
  celery -A app.workers.celery_app worker --concurrency=4
  ```

- [ ] **Set Redis maxmemory** — Prevent Redis from consuming all available memory.
  ```
  maxmemory 256mb
  maxmemory-policy allkeys-lru
  ```

- [ ] **Health checks** — The `/api/v1/health` endpoint returns 200 when the API is up. Use it for load balancer health checks.

## Frontend

- [ ] **Remove `VITE_API_BASE_URL`** — In production, the frontend defaults to `/api/v1` (relative), which nginx proxies to the backend. No env var needed.

- [ ] **Update GitHub OAuth redirect URI** — Set to `https://your-domain.com/auth/github/callback` in both the GitHub OAuth App settings and `GITHUB_REDIRECT_URI` env var.

## Monitoring (Recommended)

- [ ] **Application logs** — Ship uvicorn and Celery logs to a centralized service (Datadog, CloudWatch, Loki).

- [ ] **Error tracking** — Add Sentry for exception tracking in both backend and frontend.

- [ ] **Queue monitoring** — Monitor Celery queue depth. If tasks pile up, scale workers.

- [ ] **LLM cost tracking** — Track API usage per provider to catch cost spikes.

## Backups

- [ ] **Database backups** — Automated daily backups with point-in-time recovery.

- [ ] **Redis persistence** — Enable RDB snapshots or AOF for rate limiter state (optional — rate limits can be rebuilt).

## Domain & DNS

- [ ] **Configure domain** — Point your domain to the frontend service (port 80/443).

- [ ] **Set up SSL certificates** — Let's Encrypt with auto-renewal via Certbot or Caddy.

- [ ] **Update GitHub webhook URL** — Set to `https://your-domain.com/api/v1/github/webhook`.
