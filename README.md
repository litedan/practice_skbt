# Кадровый электронный документооборот


## Стек

- Python 3.11+
- FastAPI + Pydantic v2
- SQLAlchemy 2.0 (async) + asyncpg
- Alembic (две БД: MainBD + LogBD)
- PostgreSQL 17 (Docker)
- JWT (access + refresh), bcrypt

## Структура

```
practice_skbt/
├── backend/
│   ├── app/
│   │   ├── api/v1/          # эндпоинты
│   │   ├── core/            # config, DB, RBAC, security
│   │   ├── models/          # MainBD + LogBD
│   │   ├── schemas/
│   │   └── services/
│   ├── alembic/             # миграции main/ и log/
│   ├── scripts/smoke_api.py # smoke-тест по ролям
│   ├── .env.example
│   └── requirements.txt
├── frontend/                
└── docs/openapi.yaml
```

## Базы данных

| Контур | Назначение | Docker-сервис | Порт на хосте |
|--------|------------|---------------|---------------|
| **MainBD** | пользователи, заявки, уведомления | `hr_postgres` | **5434** (не 5432) |
| **LogBD** | audit / auth / sensitive / system logs | `hr_logs_postgres` | **5433** |

> На Windows часто занят порт **5432** локальным PostgreSQL. В `docker-compose` для MainBD используй проброс `"5434:5432"`.

Схема MainBD — канонический DDL в схеме `app` (departments, positions, users, requests, …).

## Быстрый старт

### 1. Docker

```bash
docker compose up -d
```

Убедись, что Postgres healthy, MainBD доступен на `localhost:5434`, LogBD — на `localhost:5433`.

### 2. Backend env

```bash
cd backend
copy .env.example .env   # Windows
# или: cp .env.example .env
```

В `.env` должны быть учётные данные Docker:

```
MAIN_DB_HOST=localhost
MAIN_DB_PORT=5434
MAIN_DB_USER=hr_user
MAIN_DB_PASSWORD=hr_password
MAIN_DB_NAME=hr_db

LOG_DB_HOST=localhost
LOG_DB_PORT=5433
LOG_DB_USER=logs_user
LOG_DB_PASSWORD=logs_password
LOG_DB_NAME=logs_db
```

### 3. Зависимости

=======
## Запуск backend

>>>>>>> a15a5eb167c1b79caf80ce0b0af525602a09ae57
```bash
cd backend
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt
```

### 4. Миграции

```bash
# MainBD
alembic -x db=main upgrade head

# LogBD (отдельный ini — иначе миграции log не находятся)
alembic -c alembic_log.ini -x db=log upgrade head
```

### 5. Запуск API

```bash
cd backend
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

- Swagger: http://127.0.0.1:8000/docs  
- Health: http://127.0.0.1:8000/health  

## Dev-пользователи

Пароль у всех: **`Password123!`**

| Email | Роль |
|-------|------|
| `employee@kedo.local` | Работник |
| `manager@kedo.local` | Руководитель |
| `hr@kedo.local` | HR |
| `admin@kedo.local` | Администратор |

<<<<<<< HEAD
Логин:

```http
POST /api/v1/auth/login
Content-Type: application/json

{"email": "hr@kedo.local", "password": "Password123!"}
```

Домен `.local` поддерживается (стандартный `EmailStr` его отклоняет — в проекте своя валидация).

## Роли и права (кратко)

| | Работник | Руководитель | HR | Админ |
|--|:--------:|:------------:|:--:|:-----:|
| Свои заявки | ✅ | ✅ | ✅ | — |
| Заявки отдела | — | ✅ | ✅ (все) | — |
| Проверка заявок | — | — | ✅ | — |
| Согласование | — | ✅ | — | — |
| ПДн сотрудников | свои | свои | любые | — |
| Admin users / audit | — | — | список users | ✅ + audit + block |

Роль берётся из `positions.name`: Работник / HR / Руководитель / Администратор.

## Основные эндпоинты

| Метод | Путь | Кто |
|-------|------|-----|
| POST | `/api/v1/auth/login` | все |
| POST | `/api/v1/auth/refresh` | все |
| POST | `/api/v1/auth/logout` | auth |
| GET/PATCH | `/api/v1/users/me` | auth |
| POST | `/api/v1/users/me/change-password` | auth |
| GET | `/api/v1/users/{id}` | self / HR / manager (отдел) |
| GET/PUT | `/api/v1/users/{id}/private-data` | self / HR |
| GET/POST/PATCH | `/api/v1/requests` | по RBAC |
| GET | `/api/v1/requests/stats` | HR / manager |
| GET/POST | `/api/v1/requests/{id}/files` | автор / читатели заявки |
| GET | `/api/v1/notifications` | auth |
| GET | `/api/v1/dictionaries/*` | auth |
| GET | `/api/v1/admin/users` | HR / admin |
| PATCH | `/api/v1/admin/users/{id}` | admin |
| GET | `/api/v1/admin/audit` | admin |

Жизненный цикл заявки:

`Создана` → `На проверке` (HR) → `На согласовании` (HR) → `Одобрена` (руководитель) / `Отклонена` → `Закрыта` (HR).

## Smoke-тест

При запущенном API:

```bash
cd backend
pip install httpx   # если ещё нет
python scripts/smoke_api.py
```

Проверяет login всех ролей, создание заявки, переходы HR/manager, stats, admin audit и т.д.

## Типичные проблемы

1. **`ConnectionResetError` / WinError 10054 на 5432**  
   Конфликт с Windows PostgreSQL. Используй порт **5434** для MainBD.

2. **`422` на login с `@kedo.local`**  
   Нужна актуальная версия кода со своей email-валидацией (не `EmailStr`).

3. **`relation "auth_log" does not exist`**  
   Не применены миграции LogBD:
   ```bash
   alembic -c alembic_log.ini -x db=log upgrade head
   ```

4. **`malformed bcrypt hash`**  
   Не используй `passlib` с bcrypt 5.x — в проекте прямой вызов `bcrypt`.

