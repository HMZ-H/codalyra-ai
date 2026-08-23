def test_register_success(client):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "new@example.com",
            "username": "newuser",
            "password": "password123",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "new@example.com"
    assert data["username"] == "newuser"
    assert "id" in data
    assert "hashed_password" not in data


def test_register_duplicate_email(client):
    user = {"email": "dup@example.com", "username": "user1", "password": "password123"}
    client.post("/api/v1/auth/register", json=user)

    user2 = {"email": "dup@example.com", "username": "user2", "password": "password123"}
    response = client.post("/api/v1/auth/register", json=user2)
    assert response.status_code == 409


def test_register_duplicate_username(client):
    user = {"email": "a@example.com", "username": "sameuser", "password": "password123"}
    client.post("/api/v1/auth/register", json=user)

    user2 = {"email": "b@example.com", "username": "sameuser", "password": "password123"}
    response = client.post("/api/v1/auth/register", json=user2)
    assert response.status_code == 409


def test_login_success(client):
    client.post(
        "/api/v1/auth/register",
        json={"email": "login@example.com", "username": "loginuser", "password": "password123"},
    )
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "login@example.com", "password": "password123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client):
    client.post(
        "/api/v1/auth/register",
        json={"email": "wrong@example.com", "username": "wronguser", "password": "password123"},
    )
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "wrong@example.com", "password": "wrongpassword"},
    )
    assert response.status_code == 401


def test_login_nonexistent_user(client):
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "noone@example.com", "password": "password123"},
    )
    assert response.status_code == 401


def test_get_me(client, auth_headers):
    response = client.get("/api/v1/auth/me", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["username"] == "testuser"


def test_get_me_no_token(client):
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401
