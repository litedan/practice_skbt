# KEDO — Кадровый электронный документооборот

Backend API (FastAPI) для личного кабинета сотрудника, HR и руководителя.

## Стек

- Python 3.11+
- FastAPI + Pydantic v2
- SQLAlchemy 2.0 (async) + asyncpg
- Alembic (MainBD + LogBD)
- PostgreSQL 17 (Docker)
- JWT + bcrypt

## Структура

```
practice_skbt/
├── docker-compose.yml       # postgres + postgres_logs + backend
├── backend/
│   ├── Dockerfile
│   ├── docker-entrypoint.sh # миграции + запуск API
│   ├── app/
│   ├── alembic/
│   └── requirements.txt
├── frontend/
└── docs/openapi.yaml
```

## Быстрый старт (Docker — рекомендуется)

Поднимает обе БД и backend одной командой. Миграции применяются автоматически при старте контейнера.

```bash
docker compose up -d --build
```

| Сервис | URL / порт |
|--------|------------|
| API | http://127.0.0.1:8000 |
| Swagger | http://127.0.0.1:8000/docs |
| Health | http://127.0.0.1:8000/health |
| MainBD (с хоста) | `localhost:5434` |
| LogBD (с хоста) | `localhost:5433` |

Логи backend:

```bash
docker compose logs -f backend
```

Остановка:

```bash
docker compose down
```

> MainBD проброшен на **5434**, чтобы не конфликтовать с локальным PostgreSQL на Windows (5432).

## Локальный запуск (без Docker для API)

### 1. Только БД в Docker

```bash
docker compose up -d postgres postgres_logs
```

### 2. Env

```bash
cd backend
copy .env.example .env
```

Для локального uvicorn:

```
MAIN_DB_HOST=localhost
MAIN_DB_PORT=5434
LOG_DB_HOST=localhost
LOG_DB_PORT=5433
```

### 3. Зависимости и миграции

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

alembic -x db=main upgrade head
alembic -c alembic_log.ini -x db=log upgrade head
```

### 4. Запуск

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

## Dev-пользователи

Пароль у всех: **`Password123!`** (один `!` в конце, не `!!`)

| Email | Роль |
|-------|------|
| `employee@kedo.local` | Работник |
| `manager@kedo.local` | Руководитель |
| `hr@kedo.local` | HR |
| `admin@kedo.local` | Администратор |

```http
POST /api/v1/auth/login
Content-Type: application/json

{"email": "hr@kedo.local", "password": "Password123!"}
```

## Роли и права

| | Работник | Руководитель | HR | Админ |
|--|:--------:|:------------:|:--:|:-----:|
| Свои заявки | ✅ | ✅ | ✅ | — |
| Заявки отдела | — | ✅ | ✅ (все) | — |
| Проверка заявок | — | — | ✅ | — |
| Согласование | — | ✅ | — | — |
| ПДн | свои | свои | любые | — |
| Admin / audit | — | — | users list | ✅ |

## Smoke-тест

```bash
cd backend
pip install httpx
python scripts/smoke_api.py
```

## Типичные проблемы

1. **WinError 10054 на 5432** — конфликт с Windows PostgreSQL, используй порт 5434 для MainBD.
2. **`auth_log` does not exist** — не применены миграции LogBD (`alembic -c alembic_log.ini -x db=log upgrade head`).
3. **Backend не стартует в Docker** — `docker compose logs backend`, дождись `healthy` у postgres.

## Секреты

Не коммить `backend/.env`. Для production смени `JWT_SECRET_KEY` в `docker-compose.yml` или через override-файл.
