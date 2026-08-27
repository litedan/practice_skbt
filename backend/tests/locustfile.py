"""Простое нагрузочное тестирование для KEDO."""
from locust import HttpUser, task, between
import random
from datetime import datetime, timedelta

# Данные из вашего smoke-теста
BASE = "/api/v1"
PASS = "Password123!"
USERS = {
    "employee": "employee@kedo.local",
    "manager": "manager@kedo.local",
    "hr": "hr@kedo.local",
    "admin": "admin@kedo.local",
}


class KEDOLoadTest(HttpUser):
    """Нагрузочный тест для всех ролей"""
    
    wait_time = between(1, 3)  # Пауза между запросами 1-3 секунды
    
    def on_start(self):
        """Авторизация при старте"""
        # Выбираем случайную роль
        self.role = random.choice(list(USERS.keys()))
        self.email = USERS[self.role]
        
        response = self.client.post(
            f"{BASE}/auth/login",
            json={"email": self.email, "password": PASS}
        )
        
        if response.status_code == 200:
            data = response.json()
            self.token = data.get("access_token")
            self.headers = {"Authorization": f"Bearer {self.token}"}
            self.user_id = None
            
            # Получаем свой ID для некоторых запросов
            me = self.client.get(f"{BASE}/users/me", headers=self.headers)
            if me.status_code == 200:
                self.user_id = me.json().get("id")
        else:
            self.token = None
            self.headers = {}
            self.user_id = None
    
    @task(3)
    def get_me(self):
        """Получение своего профиля"""
        if self.headers:
            self.client.get(f"{BASE}/users/me", headers=self.headers)
    
    @task(3)
    def get_requests(self):
        """Получение списка заявок"""
        if self.headers:
            self.client.get(f"{BASE}/requests", headers=self.headers)
    
    @task(2)
    def get_dictionaries(self):
        """Получение справочников"""
        if self.headers:
            self.client.get(f"{BASE}/dictionaries/statuses", headers=self.headers)
            self.client.get(f"{BASE}/dictionaries/request-types", headers=self.headers)
    
    @task(2)
    def create_request(self):
        """Создание заявки (только не для admin)"""
        if not self.headers or self.role == "admin":
            return
        
        # Получаем тип заявки
        types_resp = self.client.get(
            f"{BASE}/dictionaries/request-types",
            headers=self.headers
        )
        if types_resp.status_code != 200:
            return
        
        types = types_resp.json()
        if not types:
            return
        
        type_id = types[0]["id"]
        
        # Создаём заявку
        start = datetime.now() + timedelta(days=random.randint(5, 30))
        end = start + timedelta(days=random.randint(3, 14))
        
        self.client.post(
            f"{BASE}/requests",
            headers=self.headers,
            json={
                "request_type_id": type_id,
                "comment": f"Нагрузочный тест {datetime.now().strftime('%H:%M:%S')}",
                "start_date": start.strftime("%Y-%m-%d"),
                "end_date": end.strftime("%Y-%m-%d"),
            }
        )
    
    @task(1)
    def get_stats(self):
        """Получение статистики (только для hr и admin)"""
        if not self.headers or self.role not in ["hr", "admin"]:
            return
        self.client.get(f"{BASE}/requests/stats", headers=self.headers)
    
    @task(1)
    def get_admin_users(self):
        """Список пользователей (только для hr и admin)"""
        if not self.headers or self.role not in ["hr", "admin"]:
            return
        self.client.get(f"{BASE}/admin/users", headers=self.headers)
    
    @task(1)
    def get_audit(self):
        """Аудит (только для admin)"""
        if not self.headers or self.role != "admin":
            return
        self.client.get(f"{BASE}/admin/audit", headers=self.headers)
    
    @task(1)
    def get_notifications(self):
        """Уведомления"""
        if self.headers:
            self.client.get(f"{BASE}/notifications", headers=self.headers)