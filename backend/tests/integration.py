"""
Интеграционные тесты API КЭДО.

Нужен запущенный backend (и БД с dev-пользователями):
    docker compose up -d
    pytest tests/integration.py -v

Базовый URL: KEDO_API_BASE (по умолчанию http://127.0.0.1:8000).
Пароль dev-пользователей: Password123!
"""

from __future__ import annotations

import os
import uuid

import httpx
import pytest

BASE_URL = os.environ.get("KEDO_API_BASE", "http://127.0.0.1:8000").rstrip("/")
API = f"{BASE_URL}/api/v1"
PASSWORD = "Password123!"
USERS = {
    "employee": "employee@kedo.local",
    "manager": "manager@kedo.local",
    "hr": "hr@kedo.local",
    "admin": "admin@kedo.local",
}


def _auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="session")
def client() -> httpx.Client:
    with httpx.Client(timeout=30.0) as http:
        try:
            health = http.get(f"{BASE_URL}/health")
        except httpx.ConnectError as exc:
            pytest.skip(f"API недоступен ({BASE_URL}). Запустите backend. {exc}")
        if health.status_code != 200:
            pytest.skip(f"GET /health вернул {health.status_code}: {health.text[:200]}")
        yield http


@pytest.fixture(scope="session")
def tokens(client: httpx.Client) -> dict[str, str]:
    result: dict[str, str] = {}
    for role, email in USERS.items():
        response = client.post(
            f"{API}/auth/login",
            json={"email": email, "password": PASSWORD},
        )
        assert response.status_code == 200, f"login {email}: {response.status_code} {response.text[:300]}"
        body = response.json()
        assert "access_token" in body
        result[role] = body["access_token"]
    return result


@pytest.fixture(scope="session")
def profiles(client: httpx.Client, tokens: dict[str, str]) -> dict[str, dict]:
    result: dict[str, dict] = {}
    for role, token in tokens.items():
        response = client.get(f"{API}/users/me", headers=_auth(token))
        assert response.status_code == 200, response.text[:300]
        result[role] = response.json()
        assert result[role]["role"] == role
    return result


@pytest.fixture(scope="session")
def statuses(client: httpx.Client, tokens: dict[str, str]) -> dict[str, int]:
    response = client.get(f"{API}/dictionaries/statuses", headers=_auth(tokens["employee"]))
    assert response.status_code == 200
    items = response.json()
    assert len(items) >= 6
    return {item["name"]: item["id"] for item in items}


@pytest.fixture(scope="session")
def request_type_id(client: httpx.Client, tokens: dict[str, str]) -> int:
    response = client.get(f"{API}/dictionaries/request-types", headers=_auth(tokens["employee"]))
    assert response.status_code == 200
    items = response.json()
    assert items, "В справочнике нет типов заявок"
    return items[0]["id"]


class TestHealth:
    def test_health_ok(self, client: httpx.Client) -> None:
        response = client.get(f"{BASE_URL}/health")
        assert response.status_code == 200
        body = response.json()
        assert body.get("status") == "ok"
        assert body.get("service") == "KEDO"


class TestAuth:
    def test_login_wrong_password(self, client: httpx.Client) -> None:
        response = client.post(
            f"{API}/auth/login",
            json={"email": USERS["employee"], "password": "WrongPass1"},
        )
        assert response.status_code == 401

    def test_login_unknown_user(self, client: httpx.Client) -> None:
        response = client.post(
            f"{API}/auth/login",
            json={"email": "nobody@kedo.local", "password": PASSWORD},
        )
        assert response.status_code == 401

    def test_me_without_token(self, client: httpx.Client) -> None:
        response = client.get(f"{API}/users/me")
        assert response.status_code == 401

    def test_refresh_and_logout(self, client: httpx.Client) -> None:
        login = client.post(
            f"{API}/auth/login",
            json={"email": USERS["employee"], "password": PASSWORD},
        )
        assert login.status_code == 200
        pair = login.json()
        refresh = client.post(f"{API}/auth/refresh", json={"refresh_token": pair["refresh_token"]})
        assert refresh.status_code == 200
        assert "access_token" in refresh.json()

        logout = client.post(
            f"{API}/auth/logout",
            headers=_auth(pair["access_token"]),
            json={"refresh_token": pair["refresh_token"], "all_sessions": False},
        )
        assert logout.status_code == 200


class TestUsers:
    def test_me_permissions(self, profiles: dict[str, dict]) -> None:
        employee = profiles["employee"]
        assert "permissions" in employee
        assert "requests:create" in employee["permissions"]
        assert "audit:read" not in employee["permissions"]

        admin = profiles["admin"]
        assert "audit:read" in admin["permissions"]
        assert "requests:create" not in admin["permissions"]

    def test_patch_own_profile(self, client: httpx.Client, tokens: dict[str, str]) -> None:
        city = f"Тест-{uuid.uuid4().hex[:6]}"
        response = client.patch(
            f"{API}/users/me",
            headers=_auth(tokens["employee"]),
            json={"city": city},
        )
        assert response.status_code == 200
        assert response.json()["city"] == city

    def test_hr_reads_employee_profile(
        self,
        client: httpx.Client,
        tokens: dict[str, str],
        profiles: dict[str, dict],
    ) -> None:
        emp_id = profiles["employee"]["id"]
        response = client.get(f"{API}/users/{emp_id}", headers=_auth(tokens["hr"]))
        assert response.status_code == 200
        assert response.json()["id"] == emp_id

    def test_manager_reads_department_employee(
        self,
        client: httpx.Client,
        tokens: dict[str, str],
        profiles: dict[str, dict],
    ) -> None:
        emp_id = profiles["employee"]["id"]
        response = client.get(f"{API}/users/{emp_id}", headers=_auth(tokens["manager"]))
        assert response.status_code == 200

    def test_employee_cannot_read_hr_profile(
        self,
        client: httpx.Client,
        tokens: dict[str, str],
        profiles: dict[str, dict],
    ) -> None:
        hr_id = profiles["hr"]["id"]
        response = client.get(f"{API}/users/{hr_id}", headers=_auth(tokens["employee"]))
        assert response.status_code == 403


class TestPrivateData:
    def test_owner_and_hr_can_read(
        self,
        client: httpx.Client,
        tokens: dict[str, str],
        profiles: dict[str, dict],
    ) -> None:
        emp_id = profiles["employee"]["id"]
        own = client.get(f"{API}/users/{emp_id}/private-data", headers=_auth(tokens["employee"]))
        assert own.status_code == 200
        assert own.json()["user_id"] == emp_id

        hr = client.get(f"{API}/users/{emp_id}/private-data", headers=_auth(tokens["hr"]))
        assert hr.status_code == 200

    def test_manager_and_admin_forbidden(
        self,
        client: httpx.Client,
        tokens: dict[str, str],
        profiles: dict[str, dict],
    ) -> None:
        emp_id = profiles["employee"]["id"]
        manager = client.get(f"{API}/users/{emp_id}/private-data", headers=_auth(tokens["manager"]))
        admin = client.get(f"{API}/users/{emp_id}/private-data", headers=_auth(tokens["admin"]))
        assert manager.status_code == 403
        assert admin.status_code == 403


class TestDictionaries:
    @pytest.mark.parametrize(
        "path",
        [
            "/dictionaries/departments",
            "/dictionaries/positions",
            "/dictionaries/request-types",
            "/dictionaries/statuses",
            "/dictionaries/templates",
        ],
    )
    def test_dictionary_requires_auth(self, client: httpx.Client, path: str) -> None:
        response = client.get(f"{API}{path}")
        assert response.status_code == 401

    @pytest.mark.parametrize(
        "path",
        [
            "/dictionaries/departments",
            "/dictionaries/positions",
            "/dictionaries/request-types",
            "/dictionaries/statuses",
            "/dictionaries/templates",
        ],
    )
    def test_dictionary_ok(self, client: httpx.Client, tokens: dict[str, str], path: str) -> None:
        response = client.get(f"{API}{path}", headers=_auth(tokens["employee"]))
        assert response.status_code == 200
        assert isinstance(response.json(), list)


class TestRequests:
    def test_employee_creates_and_lists(
        self,
        client: httpx.Client,
        tokens: dict[str, str],
        profiles: dict[str, dict],
        request_type_id: int,
        statuses: dict[str, int],
    ) -> None:
        comment = f"integration {uuid.uuid4().hex[:8]}"
        created = client.post(
            f"{API}/requests",
            headers=_auth(tokens["employee"]),
            json={"request_type_id": request_type_id, "comment": comment},
        )
        assert created.status_code == 201, created.text[:400]
        body = created.json()
        assert body["employee_id"] == profiles["employee"]["id"]
        assert body["status_id"] == statuses["Создана"]
        request_id = body["id"]

        listing = client.get(f"{API}/requests", headers=_auth(tokens["employee"]))
        assert listing.status_code == 200
        ids = {item["id"] for item in listing.json()}
        assert request_id in ids

        detail = client.get(f"{API}/requests/{request_id}", headers=_auth(tokens["employee"]))
        assert detail.status_code == 200
        assert detail.json()["id"] == request_id
        assert "document_files" in detail.json()

        files = client.get(f"{API}/requests/{request_id}/files", headers=_auth(tokens["employee"]))
        assert files.status_code == 200
        assert files.json() == []

    def test_employee_cannot_filter_by_employee_id(
        self,
        client: httpx.Client,
        tokens: dict[str, str],
        profiles: dict[str, dict],
    ) -> None:
        response = client.get(
            f"{API}/requests",
            headers=_auth(tokens["employee"]),
            params={"employee_id": profiles["employee"]["id"]},
        )
        assert response.status_code == 403

    def test_employee_stats_forbidden(self, client: httpx.Client, tokens: dict[str, str]) -> None:
        response = client.get(f"{API}/requests/stats", headers=_auth(tokens["employee"]))
        assert response.status_code == 403

    def test_admin_cannot_create_request(
        self,
        client: httpx.Client,
        tokens: dict[str, str],
        request_type_id: int,
    ) -> None:
        response = client.post(
            f"{API}/requests",
            headers=_auth(tokens["admin"]),
            json={"request_type_id": request_type_id, "comment": "admin should fail"},
        )
        assert response.status_code == 403

    def test_admin_cannot_list_requests(self, client: httpx.Client, tokens: dict[str, str]) -> None:
        response = client.get(f"{API}/requests", headers=_auth(tokens["admin"]))
        assert response.status_code == 403

    def test_hr_stats_and_list(
        self,
        client: httpx.Client,
        tokens: dict[str, str],
        profiles: dict[str, dict],
    ) -> None:
        stats = client.get(f"{API}/requests/stats", headers=_auth(tokens["hr"]))
        assert stats.status_code == 200
        body = stats.json()
        for key in ("total", "created", "in_review", "in_approval", "approved", "rejected", "closed"):
            assert key in body

        listing = client.get(f"{API}/requests", headers=_auth(tokens["hr"]))
        assert listing.status_code == 200

        filtered = client.get(
            f"{API}/requests",
            headers=_auth(tokens["hr"]),
            params={"employee_id": profiles["employee"]["id"]},
        )
        assert filtered.status_code == 200

    def test_manager_list(self, client: httpx.Client, tokens: dict[str, str]) -> None:
        response = client.get(f"{API}/requests", headers=_auth(tokens["manager"]))
        assert response.status_code == 200

    def test_manager_stats(self, client: httpx.Client, tokens: dict[str, str]) -> None:
        response = client.get(f"{API}/requests/stats", headers=_auth(tokens["manager"]))
        assert response.status_code == 200

    def test_upload_file_to_own_request(
        self,
        client: httpx.Client,
        tokens: dict[str, str],
        request_type_id: int,
    ) -> None:
        created = client.post(
            f"{API}/requests",
            headers=_auth(tokens["employee"]),
            json={"request_type_id": request_type_id, "comment": "file upload"},
        )
        assert created.status_code == 201
        request_id = created.json()["id"]

        upload = client.post(
            f"{API}/requests/{request_id}/files",
            headers=_auth(tokens["employee"]),
            files={"file": ("note.pdf", b"%PDF-1.4 test", "application/pdf")},
        )
        assert upload.status_code == 201, upload.text[:400]
        file_id = upload.json()["id"]

        listing = client.get(f"{API}/requests/{request_id}/files", headers=_auth(tokens["employee"]))
        assert listing.status_code == 200
        assert any(item["id"] == file_id for item in listing.json())



class TestNotifications:
    def test_list(self, client: httpx.Client, tokens: dict[str, str]) -> None:
        response = client.get(f"{API}/notifications", headers=_auth(tokens["employee"]))
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_hr_sees_new_request_notification(
        self,
        client: httpx.Client,
        tokens: dict[str, str],
        request_type_id: int,
    ) -> None:
        created = client.post(
            f"{API}/requests",
            headers=_auth(tokens["employee"]),
            json={"request_type_id": request_type_id, "comment": "notify hr"},
        )
        assert created.status_code == 201
        request_id = created.json()["id"]

        notifications = client.get(f"{API}/notifications", headers=_auth(tokens["hr"]))
        assert notifications.status_code == 200
        related = [item for item in notifications.json() if item.get("request_id") == request_id]
        assert related, "HR должен получить уведомление о новой заявке"

        mark = client.patch(
            f"{API}/notifications/{related[0]['id']}/read",
            headers=_auth(tokens["hr"]),
        )
        assert mark.status_code == 200


class TestAdmin:
    def test_employee_audit_forbidden(self, client: httpx.Client, tokens: dict[str, str]) -> None:
        response = client.get(f"{API}/admin/audit", headers=_auth(tokens["employee"]))
        assert response.status_code == 403

    def test_hr_cannot_read_audit(self, client: httpx.Client, tokens: dict[str, str]) -> None:
        response = client.get(f"{API}/admin/audit", headers=_auth(tokens["hr"]))
        assert response.status_code == 403

    def test_hr_lists_users(self, client: httpx.Client, tokens: dict[str, str]) -> None:
        response = client.get(f"{API}/admin/users", headers=_auth(tokens["hr"]))
        assert response.status_code == 200
        assert len(response.json()) >= 4

    def test_admin_audit_and_users(self, client: httpx.Client, tokens: dict[str, str]) -> None:
        audit = client.get(f"{API}/admin/audit", headers=_auth(tokens["admin"]), params={"limit": 50})
        assert audit.status_code == 200
        assert isinstance(audit.json(), list)

        users = client.get(
            f"{API}/admin/users",
            headers=_auth(tokens["admin"]),
            params={"search": USERS["employee"], "limit": 200},
        )
        assert users.status_code == 200
        emails = {item["email"] for item in users.json()}
        assert USERS["employee"] in emails
