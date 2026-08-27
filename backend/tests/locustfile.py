"""Нагрузочное тестирование для KEDO."""
from locust import HttpUser, task, between
import random
from datetime import datetime, timedelta

PASS = "Password123!"
USERS = {
    "employee": "employee@kedo.local",
    "manager": "manager@kedo.local",
    "hr": "hr@kedo.local",
    "admin": "admin@kedo.local",
}


class KEDOLoadTest(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        """Авторизация при старте"""
        self.role = random.choice(list(USERS.keys()))
        self.email = USERS[self.role]

        # Добавляем заголовок User-Agent (как в Swagger)
        headers = {"User-Agent": "Locust-Load-Test"}

        response = self.client.post(
            "/api/v1/auth/login",
            json={"email": self.email, "password": PASS},
            headers=headers
        )

        if response.status_code == 200:
            data = response.json()
            self.token = data.get("access_token")
            self.headers = {
                "Authorization": f"Bearer {self.token}",
                "User-Agent": "Locust-Load-Test"
            }
            print(f"✅ {self.role} авторизован: {self.email}")
        else:
            self.token = None
            self.headers = {}
            print(f"❌ Ошибка авторизации {self.role}: {response.status_code} - {response.text[:100]}")

    @task(4)
    def get_me(self):
        """GET /api/v1/users/me"""
        if not self.headers:
            return

        with self.client.get(
            "/api/v1/users/me",
            headers=self.headers,
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Status: {response.status_code}, Body: {response.text[:50]}")

    @task(4)
    def get_requests(self):
        """GET /api/v1/requests"""
        if not self.headers:
            return

        with self.client.get(
            "/api/v1/requests",
            headers=self.headers,
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Status: {response.status_code}")

    @task(3)
    def get_dictionaries_statuses(self):
        """GET /api/v1/dictionaries/statuses"""
        if not self.headers:
            return

        self.client.get(
            "/api/v1/dictionaries/statuses",
            headers=self.headers
        )

    @task(3)
    def get_dictionaries_request_types(self):
        """GET /api/v1/dictionaries/request-types"""
        if not self.headers:
            return

        self.client.get(
            "/api/v1/dictionaries/request-types",
            headers=self.headers
        )

    @task(2)
    def create_request(self):
        """POST /api/v1/requests"""
        # Admin не создаёт заявки
        if not self.headers or self.role == "admin":
            return

        # Получаем тип заявки
        types_resp = self.client.get(
            "/api/v1/dictionaries/request-types",
            headers=self.headers
        )

        if types_resp.status_code != 200 or not types_resp.json():
            return

        types = types_resp.json()
        if not types:
            return

        type_id = types[0]["id"]

        # Создаём заявку с датами
        start = datetime.now() + timedelta(days=random.randint(5, 30))
        end = start + timedelta(days=random.randint(3, 14))

        with self.client.post(
            "/api/v1/requests",
            headers=self.headers,
            json={
                "request_type_id": type_id,
                "comment": f"Load test {random.randint(1, 9999)}",
                "start_date": start.strftime("%Y-%m-%d"),
                "end_date": end.strftime("%Y-%m-%d"),
            },
            catch_response=True
        ) as response:
            if response.status_code in [200, 201]:
                response.success()
            else:
                response.failure(f"Status: {response.status_code}, Body: {response.text[:100]}")

    @task(1)
    def get_stats(self):
        """GET /api/v1/requests/stats (HR и Admin)"""
        if not self.headers or self.role not in ["hr", "admin"]:
            return

        with self.client.get(
            "/api/v1/requests/stats",
            headers=self.headers,
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Status: {response.status_code}")

    @task(1)
    def get_admin_users(self):
        """GET /api/v1/admin/users (HR и Admin)"""
        if not self.headers or self.role not in ["hr", "admin"]:
            return

        with self.client.get(
            "/api/v1/admin/users",
            headers=self.headers,
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Status: {response.status_code}")

    @task(1)
    def get_admin_audit(self):
        """GET /api/v1/admin/audit (только Admin)"""
        if not self.headers or self.role != "admin":
            return

        with self.client.get(
            "/api/v1/admin/audit",
            headers=self.headers,
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Status: {response.status_code}")

    @task(2)
    def get_notifications(self):
        """GET /api/v1/notifications"""
        if not self.headers:
            return

        self.client.get(
            "/api/v1/notifications",
            headers=self.headers
        )