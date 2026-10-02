---
sidebar_position: 4
title: Projects
---

# Projects API

## Create Project

```http
POST /api/v1/projects/
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "My Backend",
  "description": "FastAPI microservice"
}
```

**Response** (201):
```json
{
  "id": "uuid",
  "name": "My Backend",
  "description": "FastAPI microservice",
  "user_id": "uuid",
  "created_at": "2026-09-17T10:30:00Z"
}
```

## List Projects

```http
GET /api/v1/projects/
Authorization: Bearer <token>
```

Returns all projects owned by the authenticated user.

## Get Project

```http
GET /api/v1/projects/{project_id}
Authorization: Bearer <token>
```

## Update Project

```http
PUT /api/v1/projects/{project_id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "Updated Name",
  "description": "Updated description"
}
```

## Delete Project

```http
DELETE /api/v1/projects/{project_id}
Authorization: Bearer <token>
```

**Warning**: Cascades to all reviews, tasks, runs, evaluations, repositories, agent configs, custom rules, and feedback for this project.

## Authorization

All project endpoints enforce ownership. You can only access projects where `project.user_id == current_user.id`. Attempting to access another user's project returns 403.
