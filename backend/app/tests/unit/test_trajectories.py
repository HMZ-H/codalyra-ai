import uuid
from datetime import datetime, timezone

from app.database.models.trajectory import Trajectory


def _setup_run(client, auth_headers, db_session) -> str:
    project_resp = client.post(
        "/api/v1/projects/", json={"name": "Traj Project"}, headers=auth_headers
    )
    project_id = project_resp.json()["id"]

    task_resp = client.post(
        "/api/v1/tasks/",
        json={
            "title": "Traj Task",
            "description": "Task for trajectory tests",
            "project_id": project_id,
        },
        headers=auth_headers,
    )
    task_id = task_resp.json()["id"]

    run_resp = client.post(
        "/api/v1/runs/",
        json={"task_id": task_id, "agent_name": "test-agent"},
        headers=auth_headers,
    )
    return run_resp.json()["id"]


def test_get_trajectories_empty(client, auth_headers, db_session):
    run_id = _setup_run(client, auth_headers, db_session)

    response = client.get(f"/api/v1/trajectories/run/{run_id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json() == []


def test_get_trajectories_ordered(client, auth_headers, db_session):
    run_id = _setup_run(client, auth_headers, db_session)

    for seq in [3, 1, 2]:
        t = Trajectory(
            run_id=uuid.UUID(run_id),
            sequence_number=seq,
            action_type=f"action_{seq}",
            action_input=f"input {seq}",
            action_output=f"output {seq}",
        )
        db_session.add(t)
    db_session.commit()

    response = client.get(f"/api/v1/trajectories/run/{run_id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    assert data[0]["sequence_number"] == 1
    assert data[1]["sequence_number"] == 2
    assert data[2]["sequence_number"] == 3
    assert data[0]["action_type"] == "action_1"


def test_get_trajectories_no_auth(client):
    fake_id = str(uuid.uuid4())
    response = client.get(f"/api/v1/trajectories/run/{fake_id}")
    assert response.status_code == 401
