def test_create_project(client, auth_headers):
    response = client.post(
        "/api/v1/projects/",
        json={"name": "My Project", "description": "Test project"},
        headers=auth_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "My Project"
    assert data["is_active"] is True


def test_create_project_unauthorized(client):
    response = client.post(
        "/api/v1/projects/",
        json={"name": "My Project"},
    )
    assert response.status_code == 401


def test_list_projects(client, auth_headers):
    client.post("/api/v1/projects/", json={"name": "Project 1"}, headers=auth_headers)
    client.post("/api/v1/projects/", json={"name": "Project 2"}, headers=auth_headers)

    response = client.get("/api/v1/projects/", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_get_project(client, auth_headers):
    create_resp = client.post(
        "/api/v1/projects/", json={"name": "Get Me"}, headers=auth_headers
    )
    project_id = create_resp.json()["id"]

    response = client.get(f"/api/v1/projects/{project_id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["name"] == "Get Me"


def test_update_project(client, auth_headers):
    create_resp = client.post(
        "/api/v1/projects/", json={"name": "Old Name"}, headers=auth_headers
    )
    project_id = create_resp.json()["id"]

    response = client.put(
        f"/api/v1/projects/{project_id}",
        json={"name": "New Name"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["name"] == "New Name"


def test_delete_project(client, auth_headers):
    create_resp = client.post(
        "/api/v1/projects/", json={"name": "Delete Me"}, headers=auth_headers
    )
    project_id = create_resp.json()["id"]

    response = client.delete(f"/api/v1/projects/{project_id}", headers=auth_headers)
    assert response.status_code == 204
