---
sidebar_position: 6
title: Analytics
---

# Analytics API

## Overview Stats

```http
GET /api/v1/analytics/overview?project_id=uuid
Authorization: Bearer <token>
```

**Response** (200):
```json
{
  "total_reviews": 42,
  "average_score": 84.5,
  "total_findings": 312,
  "recent_reviews": [...]
}
```

## Score Trends

```http
GET /api/v1/analytics/score-trends?project_id=uuid&days=30
Authorization: Bearer <token>
```

**Response** (200):
```json
{
  "trends": [
    {"date": "2026-09-01", "average_score": 82.3, "review_count": 5},
    {"date": "2026-09-02", "average_score": 87.1, "review_count": 3}
  ]
}
```

## Category Breakdown

```http
GET /api/v1/analytics/categories?project_id=uuid
Authorization: Bearer <token>
```

**Response** (200):
```json
{
  "categories": [
    {"name": "security", "count": 45, "percentage": 28.5},
    {"name": "quality", "count": 38, "percentage": 24.1},
    {"name": "performance", "count": 35, "percentage": 22.2},
    {"name": "logic", "count": 40, "percentage": 25.3}
  ]
}
```

## Agent Performance

```http
GET /api/v1/analytics/agents?project_id=uuid
Authorization: Bearer <token>
```

**Response** (200):
```json
{
  "agents": [
    {
      "agent_type": "security",
      "average_score": 88.2,
      "average_duration_ms": 4500,
      "average_findings": 3.2,
      "total_runs": 42
    }
  ]
}
```

## Filtering

All analytics endpoints accept optional query parameters:

| Parameter | Type | Description |
|-----------|------|-------------|
| `project_id` | UUID | Filter by project |
| `days` | Integer | Time window (default: 30) |
| `start_date` | Date | Start of date range |
| `end_date` | Date | End of date range |
