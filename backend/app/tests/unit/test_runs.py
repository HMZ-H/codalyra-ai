import uuid


def _create_project(client, auth_headers) -> str:
    resp = client.post(
        "/api/v1/projects/", json={"name": "Run Project"}, headers=auth_headers
    )
    return resp.json()["id"]


def _create_task(client, auth_headers, project_id) -> str:
    resp = client.post(
        "/api/v1/tasks/",
        json={
            "title": "Test Task",
            "description": "A task for testing runs",
            "project_id": project_id,
        },
        headers=auth_headers,
    )
    return resp.json()["id"]


def test_create_run(client, auth_headers):
    project_id = _create_project(client, auth_headers)
    task_id = _create_task(client, auth_headers, project_id)

    response = client.post(
        "/api/v1/runs/",
        json={"task_id": task_id, "agent_name": "gpt-4"},
        headers=auth_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["agent_name"] == "gpt-4"
    assert data["status"] == "pending"
    assert data["task_id"] == task_id


def test_list_runs_by_task(client, auth_headers):
    project_id = _create_project(client, auth_headers)
    task_id = _create_task(client, auth_headers, project_id)

    for name in ["agent-a", "agent-b", "agent-c"]:
        client.post(
            "/api/v1/runs/",
            json={"task_id": task_id, "agent_name": name},
            headers=auth_headers,
        )

    response = client.get(
        f"/api/v1/runs/?task_id={task_id}", headers=auth_headers
    )
    assert response.status_code == 200
    assert len(response.json()) == 3


def test_get_run(client, auth_headers):
    project_id = _create_project(client, auth_headers)
    task_id = _create_task(client, auth_headers, project_id)

    create_resp = client.post(
        "/api/v1/runs/",
        json={"task_id": task_id, "agent_name": "claude-sonnet"},
        headers=auth_headers,
    )
    run_id = create_resp.json()["id"]

    response = client.get(f"/api/v1/runs/{run_id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["agent_name"] == "claude-sonnet"


def test_get_nonexistent_run(client, auth_headers):
    fake_id = str(uuid.uuid4())
    response = client.get(f"/api/v1/runs/{fake_id}", headers=auth_headers)
    assert response.status_code == 404


def test_create_run_no_auth(client):
    response = client.post(
        "/api/v1/runs/",
        json={"task_id": str(uuid.uuid4()), "agent_name": "test"},
    )
    assert response.status_code == 401


def test_list_runs_requires_task_id(client, auth_headers):
    response = client.get("/api/v1/runs/", headers=auth_headers)
    assert response.status_code == 422
