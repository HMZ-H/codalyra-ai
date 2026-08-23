import uuid


def _create_project(client, auth_headers) -> str:
    resp = client.post(
        "/api/v1/projects/", json={"name": "Task Project"}, headers=auth_headers
    )
    return resp.json()["id"]


def test_create_task(client, auth_headers):
    project_id = _create_project(client, auth_headers)
    response = client.post(
        "/api/v1/tasks/",
        json={
            "title": "Fix the bug",
            "description": "There is a bug in the auth middleware",
            "project_id": project_id,
            "difficulty": "medium",
            "language": "python",
        },
        headers=auth_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Fix the bug"
    assert data["status"] == "draft"
    assert data["difficulty"] == "medium"


def test_list_tasks_by_project(client, auth_headers):
    project_id = _create_project(client, auth_headers)
    for i in range(3):
        client.post(
            "/api/v1/tasks/",
            json={
                "title": f"Task {i}",
                "description": f"Description {i}",
                "project_id": project_id,
            },
            headers=auth_headers,
        )

    response = client.get(
        f"/api/v1/tasks/?project_id={project_id}", headers=auth_headers
    )
    assert response.status_code == 200
    assert len(response.json()) == 3


def test_get_task(client, auth_headers):
    project_id = _create_project(client, auth_headers)
    create_resp = client.post(
        "/api/v1/tasks/",
        json={
            "title": "Get Me",
            "description": "Fetch this task",
            "project_id": project_id,
        },
        headers=auth_headers,
    )
    task_id = create_resp.json()["id"]

    response = client.get(f"/api/v1/tasks/{task_id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["title"] == "Get Me"


def test_update_task(client, auth_headers):
    project_id = _create_project(client, auth_headers)
    create_resp = client.post(
        "/api/v1/tasks/",
        json={
            "title": "Original",
            "description": "To be updated",
            "project_id": project_id,
        },
        headers=auth_headers,
    )
    task_id = create_resp.json()["id"]

    response = client.put(
        f"/api/v1/tasks/{task_id}",
        json={"title": "Updated", "status": "active"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Updated"
    assert response.json()["status"] == "active"


def test_delete_task(client, auth_headers):
    project_id = _create_project(client, auth_headers)
    create_resp = client.post(
        "/api/v1/tasks/",
        json={
            "title": "Delete Me",
            "description": "Will be deleted",
            "project_id": project_id,
        },
        headers=auth_headers,
    )
    task_id = create_resp.json()["id"]

    response = client.delete(f"/api/v1/tasks/{task_id}", headers=auth_headers)
    assert response.status_code == 204


def test_get_nonexistent_task(client, auth_headers):
    fake_id = str(uuid.uuid4())
    response = client.get(f"/api/v1/tasks/{fake_id}", headers=auth_headers)
    assert response.status_code == 404
