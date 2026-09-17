---
sidebar_position: 1
title: Docker Compose
---

# Docker Compose Deployment

Codalyra runs as 5 services via Docker Compose.

## Services

| Service | Image | Port | Purpose |
|---------|-------|------|---------|
| **postgres** | `postgres:16-alpine` | 5433:5432 | Database |
| **redis** | `redis:7-alpine` | 6379 | Message broker + rate limiting |
| **api** | Custom (Python 3.12) | 8000 | FastAPI backend |
| **celery-worker** | Same as api | — | Background task processing |
| **frontend** | Custom (nginx:alpine) | 3000:80 | React app + reverse proxy |

## Startup Order

```
postgres (healthcheck: pg_isready)
    ↓
redis (healthcheck: redis-cli ping)
    ↓
api (runs: alembic upgrade head → uvicorn)
celery-worker (runs: celery worker)
    ↓
frontend (nginx serves static + proxies /api/)
```

`depends_on` with `condition: service_healthy` ensures services start in order.

## Quick Start

```bash
# Clone and configure
git clone https://github.com/HMZ-H/codalyra-ai.git
cd codalyra-ai
cp backend/.env.example backend/.env

# Edit backend/.env with your values
# At minimum: GEMINI_API_KEY, SECRET_KEY

# Build and start
docker compose up --build

# Access at http://localhost:3000
```

## Backend Dockerfile

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

The API container runs `alembic upgrade head` before starting uvicorn (configured in `docker-compose.yml` command).

## Frontend Dockerfile

Multi-stage build for a minimal production image:

```dockerfile
# Stage 1: Build (Node 22, ~1GB)
FROM node:22-alpine AS build
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm ci
COPY . .
RUN npm run build

# Stage 2: Serve (nginx:alpine, ~30MB)
FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

The final image is ~30MB — no Node, npm, or source code.

## Nginx Configuration

```nginx
server {
    listen 80;
    
    location / {
        root /usr/share/nginx/html;
        try_files $uri $uri/ /index.html;  # SPA fallback
    }
    
    location /api/ {
        proxy_pass http://api:8000;  # Reverse proxy to backend
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location /ws/ {
        proxy_pass http://api:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";  # WebSocket support
    }
}
```

## Rebuilding

```bash
# Rebuild a single service
docker compose build api
docker compose up -d api

# Rebuild everything
docker compose up --build -d

# View logs
docker compose logs -f api
docker compose logs -f celery-worker
```

## Volumes

- `pgdata` — PostgreSQL data directory (persists across restarts)
