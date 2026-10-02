---
sidebar_position: 3
title: Reviews
---

# Reviews API

## Create Review

Submit a code diff for multi-agent review.

```http
POST /api/v1/reviews/
Authorization: Bearer <token>
Content-Type: application/json

{
  "project_id": "uuid",
  "diff_content": "diff --git a/app.py b/app.py\n..."
}
```

**Response** (201):
```json
{
  "id": "uuid",
  "project_id": "uuid",
  "status": "pending",
  "created_at": "2026-09-17T10:30:00Z"
}
```

This triggers 6 Celery tasks (4 specialists + synthesis + baseline).

## List Reviews

```http
GET /api/v1/reviews/?project_id=uuid
Authorization: Bearer <token>
```

**Response** (200):
```json
[
  {
    "id": "uuid",
    "status": "completed",
    "score": 85,
    "summary": "Overall good code with minor security concerns...",
    "baseline_score": 72,
    "baseline_findings_count": 4,
    "created_at": "2026-09-17T10:30:00Z"
  }
]
```

## Get Review

```http
GET /api/v1/reviews/{review_id}
Authorization: Bearer <token>
```

Returns the full review with all agent runs, findings, and scores.

## Get Review Report

```http
GET /api/v1/reviews/{review_id}/report
Authorization: Bearer <token>
```

Returns the synthesized report with:
- Overall score and summary
- Per-agent findings with file, line, severity, message, suggestion
- Baseline comparison
- Agent execution durations

## Auto-Fix

Generate LLM-powered fix suggestions for critical/warning findings.

```http
POST /api/v1/reviews/{review_id}/auto-fix
Authorization: Bearer <token>
```

**Response** (200):
```json
{
  "fixes": [
    {
      "finding_index": 0,
      "original_code": "password = 'admin123'",
      "fixed_code": "password = os.environ['DB_PASSWORD']",
      "explanation": "Move hardcoded password to environment variable"
    }
  ]
}
```

## WebSocket (Real-time Updates)

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/reviews/{review_id}');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  // { "status": "running", "agent": "security", "message": "Security agent completed" }
};
```

Status updates stream as each agent completes.
