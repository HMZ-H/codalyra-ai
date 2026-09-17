---
sidebar_position: 2
title: Authentication
---

# Authentication API

## Register

```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "username": "johndoe",
  "password": "securepassword"
}
```

**Response** (201):
```json
{
  "access_token": "eyJhbGciOiJI...",
  "token_type": "bearer",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "username": "johndoe"
  }
}
```

## Login

```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword"
}
```

**Response** (200): Same as register.

## Get Current User

```http
GET /api/v1/auth/me
Authorization: Bearer <token>
```

**Response** (200):
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "username": "johndoe",
  "github_username": "johndoe"
}
```

## GitHub OAuth Callback

```http
POST /api/v1/auth/github/callback
Content-Type: application/json

{
  "code": "github-authorization-code",
  "state": "login"
}
```

**State values:**
- `login` — Create or find user, return JWT
- `connect` — Link GitHub to existing account (requires Authorization header)

**Response** (200):
```json
{
  "access_token": "eyJhbGciOiJI...",
  "token_type": "bearer",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "github_username": "johndoe"
  }
}
```

## Error Responses

| Status | Description |
|--------|-------------|
| 400 | Invalid input (bad email, weak password) |
| 401 | Invalid credentials or expired token |
| 409 | Email or username already taken |
