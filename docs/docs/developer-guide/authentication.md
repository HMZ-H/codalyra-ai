---
sidebar_position: 7
title: Authentication & Security
---

# Authentication & Security

Codalyra uses JWT tokens for stateless authentication, bcrypt for password hashing, Fernet for API key encryption, and GitHub OAuth for social login.

## JWT Authentication

### Token Creation

On login or registration, the server creates a JWT:

```python
payload = {
    "sub": str(user.id),     # Subject: user UUID
    "exp": now + timedelta(minutes=30),  # 30-minute expiry
}
token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
```

### Token Verification

Every protected endpoint uses the `get_current_user` FastAPI dependency:

```python
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    user_id = payload.get("sub")
    user = db.query(User).get(user_id)
    if not user:
        raise HTTPException(401)
    return user
```

### Frontend Flow

1. On login, the JWT is stored in `localStorage`
2. The Axios interceptor attaches it to every request as `Authorization: Bearer <token>`
3. On 401 response, the interceptor clears the token and redirects to `/login`
4. `AuthContext` validates the token on app mount via `GET /auth/me`

## Password Security

Passwords are hashed with **bcrypt** (cost factor 12):

```python
hashed = bcrypt.hash(password)        # On registration
verified = bcrypt.verify(password, hashed)  # On login
```

Bcrypt is intentionally slow (~200ms per hash), making brute-force attacks impractical.

## API Key Encryption

LLM API keys are stored encrypted using **Fernet** symmetric encryption:

```python
def _get_fernet():
    key = hashlib.sha256(settings.SECRET_KEY.encode()).digest()
    return Fernet(base64.urlsafe_b64encode(key))

def encrypt_value(plaintext: str) -> str:
    return _get_fernet().encrypt(plaintext.encode()).decode()

def decrypt_value(ciphertext: str) -> str:
    return _get_fernet().decrypt(ciphertext.encode()).decode()
```

- Encrypted on `PUT /settings/api-keys`
- Decrypted only inside Celery workers at LLM call time
- Plaintext exists in memory for the duration of one API call only
- Never exposed in API responses

## GitHub OAuth

### Login Flow

1. Frontend redirects to `github.com/login/oauth/authorize`
2. GitHub redirects back with an authorization code
3. Backend exchanges the code for an access token
4. Backend fetches the GitHub user profile
5. Backend finds or creates a User (links by `github_id` or email)
6. Backend issues a JWT

### Connect Flow

For existing accounts that want to link GitHub:

1. Same OAuth redirect but with `state=connect`
2. Requires an existing JWT (the user must be logged in)
3. Links the GitHub account to the existing Codalyra user

## Authorization

### Ownership Model

Every entity traces back to a project owner:

```
Run → Task → Review → Project → User
```

The `permissions.py` module provides guard functions:

```python
def verify_project_owner(db, project_id, user_id):
    project = db.query(Project).get(project_id)
    if project.user_id != user_id:
        raise ForbiddenException()
```

Every mutating endpoint calls the appropriate guard before proceeding.

## Rate Limiting

Redis-backed sliding window counter:

- Key: `{user_id}:{action}`
- Window: 1 hour
- Limit: 10 review requests

If Redis is unavailable, the rate limiter **degrades open** (allows the request). Rate limiting is a protection, not a security boundary.

## Webhook Verification

GitHub webhooks are verified with HMAC-SHA256:

```python
expected = hmac.new(secret, body, sha256).hexdigest()
if not hmac.compare_digest(expected, received):
    raise HTTPException(403)
```

`compare_digest()` prevents timing attacks.

## CSRF Protection

The API uses Bearer tokens in headers, not cookies. Since tokens must be explicitly set by JavaScript, cross-origin pages cannot include them — CSRF is not a viable attack vector.
