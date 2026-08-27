import uuid as uuid_mod

from app.database.models.evaluation import Evaluation


def _setup_run(client, auth_headers, db_session) -> str:
    project_resp = client.post(
        "/api/v1/projects/", json={"name": "Eval Project"}, headers=auth_headers
    )
    project_id = project_resp.json()["id"]

    task_resp = client.post(
        "/api/v1/tasks/",
        json={
            "title": "Eval Task",
            "description": "Task for evaluation tests",
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


def test_get_evaluation_not_found(client, auth_headers, db_session):
    run_id = _setup_run(client, auth_headers, db_session)

    response = client.get(f"/api/v1/evaluations/run/{run_id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json() is None


def test_get_evaluation_exists(client, auth_headers, db_session):
    run_id = _setup_run(client, auth_headers, db_session)

    evaluation = Evaluation(
        run_id=uuid_mod.UUID(run_id),
        tests_passed=3,
        tests_total=5,
        score=0.6,
        is_correct=False,
        feedback="3 of 5 tests passed",
        evaluation_method="auto",
    )
    db_session.add(evaluation)
    db_session.commit()

    response = client.get(f"/api/v1/evaluations/run/{run_id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["tests_passed"] == 3
    assert data["tests_total"] == 5
    assert data["score"] == 0.6
    assert data["is_correct"] is False
    assert data["feedback"] == "3 of 5 tests passed"


def test_get_evaluation_no_auth(client):
    fake_id = str(uuid_mod.uuid4())
    response = client.get(f"/api/v1/evaluations/run/{fake_id}")
    assert response.status_code == 401
