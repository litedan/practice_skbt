# КЭДО

Кадровый электронный документооборот: заявки сотрудников, проверка HR, согласование руководителем.

Стек: Python 3.11+, FastAPI, SQLAlchemy 2.0, PostgreSQL, Alembic, JWT.

## Структура

```
backend/     FastAPI API, модели, миграции
frontend/    UI (пока пусто)
```

Роли определяются должностью (`positions.name`): Работник, HR, Руководитель, Администратор.

Поток заявки: **Создана → На проверке (HR) → На согласовании (руководитель отдела) → Одобрена / Отклонена**.

Две БД: `kedo_main` (бизнес) и `kedo_log` (аудит).

## Запуск backend

Нужны PostgreSQL и две базы: `kedo_main`, `kedo_log`.

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # Linux/macOS

pip install -r requirements.txt
copy .env.example .env          # Windows; Linux: cp .env.example .env
```

В `.env` укажите доступы к БД и `JWT_SECRET_KEY`.

```bash
alembic -x db=main upgrade head
alembic -x db=log upgrade head

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Swagger: http://127.0.0.1:8000/docs  
Health: http://127.0.0.1:8000/health

## API (кратко)

| Метод | Путь |
|-------|------|
| POST | `/api/v1/auth/login`, `/auth/refresh` |
| GET | `/api/v1/users/me` |
| GET/PUT | `/api/v1/users/{id}/private-data` |
| GET/POST/PATCH | `/api/v1/requests` |
| POST/GET | `/api/v1/requests/{id}/files` |
| GET | `/api/v1/notifications` |
| GET | `/api/v1/dictionaries/*` |
| POST | `/api/v1/documents/{id}/sign` (заглушка) |

Авторизация: `Authorization: Bearer <access_token>`.
