import pytest
from fastapi.testclient import TestClient


class TestAuthFlow:
    def test_register_and_login(self, client: TestClient):
        res = client.post("/api/v1/auth/register", json={
            "email": "new@example.com",
            "username": "newuser",
            "password": "password123",
            "full_name": "New User",
        })
        assert res.status_code == 201
        assert res.json()["email"] == "new@example.com"

        res = client.post("/api/v1/auth/login", json={
            "email": "new@example.com",
            "password": "password123",
        })
        assert res.status_code == 200
        assert "access_token" in res.json()

    def test_register_duplicate_email(self, client: TestClient, auth_headers):
        res = client.post("/api/v1/auth/register", json={
            "email": "test@example.com",
            "username": "another",
            "password": "password123",
        })
        assert res.status_code in (400, 409)

    def test_login_wrong_password(self, client: TestClient, auth_headers):
        res = client.post("/api/v1/auth/login", json={
            "email": "test@example.com",
            "password": "wrongpassword",
        })
        assert res.status_code == 401

    def test_get_me(self, client: TestClient, auth_headers):
        res = client.get("/api/v1/auth/me", headers=auth_headers)
        assert res.status_code == 200
        assert res.json()["email"] == "test@example.com"

    def test_get_me_no_auth(self, client: TestClient):
        res = client.get("/api/v1/auth/me")
        assert res.status_code == 401


class TestProjectsCRUD:
    def test_create_project(self, client: TestClient, auth_headers):
        res = client.post("/api/v1/projects/", json={
            "name": "Test Project",
            "description": "A test project",
        }, headers=auth_headers)
        assert res.status_code == 201
        data = res.json()
        assert data["name"] == "Test Project"
        assert "id" in data

    def test_list_projects(self, client: TestClient, auth_headers):
        client.post("/api/v1/projects/", json={"name": "P1"}, headers=auth_headers)
        client.post("/api/v1/projects/", json={"name": "P2"}, headers=auth_headers)
        res = client.get("/api/v1/projects/", headers=auth_headers)
        assert res.status_code == 200
        assert len(res.json()) == 2

    def test_get_project(self, client: TestClient, auth_headers):
        create = client.post("/api/v1/projects/", json={"name": "MyProj"}, headers=auth_headers)
        pid = create.json()["id"]
        res = client.get(f"/api/v1/projects/{pid}", headers=auth_headers)
        assert res.status_code == 200
        assert res.json()["name"] == "MyProj"

    def test_update_project(self, client: TestClient, auth_headers):
        create = client.post("/api/v1/projects/", json={"name": "Old Name"}, headers=auth_headers)
        pid = create.json()["id"]
        res = client.put(f"/api/v1/projects/{pid}", json={"name": "New Name"}, headers=auth_headers)
        assert res.status_code == 200
        assert res.json()["name"] == "New Name"

    def test_delete_project(self, client: TestClient, auth_headers):
        create = client.post("/api/v1/projects/", json={"name": "ToDelete"}, headers=auth_headers)
        pid = create.json()["id"]
        res = client.delete(f"/api/v1/projects/{pid}", headers=auth_headers)
        assert res.status_code == 204

    def test_projects_require_auth(self, client: TestClient):
        res = client.get("/api/v1/projects/")
        assert res.status_code == 401


class TestSettingsAPI:
    def test_get_api_key_status_empty(self, client: TestClient, auth_headers):
        res = client.get("/api/v1/settings/api-keys", headers=auth_headers)
        assert res.status_code == 200
        data = res.json()
        assert data["has_gemini_key"] is False
        assert data["has_openai_key"] is False
        assert data["has_anthropic_key"] is False

    def test_save_and_retrieve_gemini_key(self, client: TestClient, auth_headers):
        res = client.put("/api/v1/settings/api-keys", json={
            "gemini_api_key": "AIzaSyTest1234567890abcdef",
        }, headers=auth_headers)
        assert res.status_code == 200

        res = client.get("/api/v1/settings/api-keys", headers=auth_headers)
        data = res.json()
        assert data["has_gemini_key"] is True
        assert data["gemini_key_preview"].startswith("AIza")

    def test_save_openai_key(self, client: TestClient, auth_headers):
        res = client.put("/api/v1/settings/api-keys", json={
            "openai_api_key": "sk-test1234567890abcdefghij",
        }, headers=auth_headers)
        assert res.status_code == 200

        res = client.get("/api/v1/settings/api-keys", headers=auth_headers)
        assert res.json()["has_openai_key"] is True

    def test_delete_provider_key(self, client: TestClient, auth_headers):
        client.put("/api/v1/settings/api-keys", json={
            "gemini_api_key": "AIzaSyTestKey12345678",
        }, headers=auth_headers)

        res = client.delete("/api/v1/settings/api-keys/gemini", headers=auth_headers)
        assert res.status_code == 200

        res = client.get("/api/v1/settings/api-keys", headers=auth_headers)
        assert res.json()["has_gemini_key"] is False


class TestAgentConfigAPI:
    def _create_project(self, client, auth_headers):
        res = client.post("/api/v1/projects/", json={"name": "Config Test"}, headers=auth_headers)
        return res.json()["id"]

    def test_list_agent_configs(self, client: TestClient, auth_headers):
        pid = self._create_project(client, auth_headers)
        res = client.get(f"/api/v1/projects/{pid}/agents", headers=auth_headers)
        assert res.status_code == 200
        data = res.json()
        assert len(data) == 4
        types = {a["agent_type"] for a in data}
        assert types == {"logic", "security", "performance", "quality"}

    def test_configs_have_default_prompts(self, client: TestClient, auth_headers):
        pid = self._create_project(client, auth_headers)
        res = client.get(f"/api/v1/projects/{pid}/agents", headers=auth_headers)
        for agent in res.json():
            assert len(agent["default_prompt"]) > 50
            assert agent["is_customized"] is False
            assert agent["is_enabled"] is True

    def test_upsert_agent_config(self, client: TestClient, auth_headers):
        pid = self._create_project(client, auth_headers)
        res = client.put(f"/api/v1/projects/{pid}/agents/security", json={
            "custom_prompt": "Custom security instructions",
            "temperature": 0.5,
        }, headers=auth_headers)
        assert res.status_code == 200
        assert res.json()["custom_prompt"] == "Custom security instructions"
        assert res.json()["temperature"] == 0.5

    def test_upsert_with_provider(self, client: TestClient, auth_headers):
        pid = self._create_project(client, auth_headers)
        res = client.put(f"/api/v1/projects/{pid}/agents/logic", json={
            "provider": "openai",
            "model_name": "gpt-4o",
        }, headers=auth_headers)
        assert res.status_code == 200
        assert res.json()["provider"] == "openai"
        assert res.json()["model_name"] == "gpt-4o"

    def test_disable_agent(self, client: TestClient, auth_headers):
        pid = self._create_project(client, auth_headers)
        res = client.put(f"/api/v1/projects/{pid}/agents/quality", json={
            "is_enabled": False,
        }, headers=auth_headers)
        assert res.status_code == 200
        assert res.json()["is_enabled"] is False

    def test_reset_agent_config(self, client: TestClient, auth_headers):
        pid = self._create_project(client, auth_headers)
        client.put(f"/api/v1/projects/{pid}/agents/logic", json={
            "custom_prompt": "Custom",
        }, headers=auth_headers)

        res = client.delete(f"/api/v1/projects/{pid}/agents/logic", headers=auth_headers)
        assert res.status_code == 200

        res = client.get(f"/api/v1/projects/{pid}/agents", headers=auth_headers)
        logic = next(a for a in res.json() if a["agent_type"] == "logic")
        assert logic["is_customized"] is False

    def test_invalid_agent_type(self, client: TestClient, auth_headers):
        pid = self._create_project(client, auth_headers)
        res = client.put(f"/api/v1/projects/{pid}/agents/invalid", json={
            "temperature": 0.5,
        }, headers=auth_headers)
        assert res.status_code == 400

    def test_list_providers(self, client: TestClient, auth_headers):
        pid = self._create_project(client, auth_headers)
        res = client.get(f"/api/v1/projects/{pid}/agents/providers", headers=auth_headers)
        assert res.status_code == 200
        data = res.json()
        assert "gemini" in data
        assert "openai" in data
        assert "anthropic" in data
        assert "models" in data["gemini"]


class TestHealthEndpoint:
    def test_health(self, client: TestClient):
        res = client.get("/api/v1/health")
        assert res.status_code == 200
        assert res.json()["status"] == "healthy"
