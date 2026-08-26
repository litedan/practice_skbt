Кадровый электронный документооборот

MVP-приложение: FastAPI backend + React (`frontmain`) + две PostgreSQL (MainBD / LogBD).

## Стек

- Python 3.12 / FastAPI / SQLAlchemy 2 (async) / Alembic / JWT
- React + Vite (`frontmain/`)
- PostgreSQL 17 (Docker)

## Структура

```
practice_skbt/
├── docker-compose.yml   # postgres + postgres_logs + backend + frontend
├── backend/
├── frontmain/           # React UI (в Docker)
├── frontend/           
└── docs/
```
## Подключение к БД

Клонируем репозиторий

```bash
git clone https://github.com/KrylovArseniy/BD_practice.git
cd BD_practice
```

Запускаем контейнер

```bash
docker compose up -d
```

Важно: Этот репозиторий поднимает две БД:

hr_postgres на порту 5434 (MainDB)

hr_logs_postgres на порту 5433 (LogDB)

## Запуск приложения

```bash
docker compose up -d --build
```

| Сервис | URL |
|--------|-----|
| Frontend | http://127.0.0.1:5173 |
| API / Swagger | http://127.0.0.1:8000/docs |
| Health | http://127.0.0.1:8000/health |
| MainBD (с хоста) | `localhost:5434` |
| LogBD (с хоста) | `localhost:5433` |

Миграции и seed выполняются при старте backend автоматически.

Логи:

```bash
docker compose logs -f backend
docker compose logs -f frontend
```

Остановка (данные в volumes сохраняются):

```bash
docker compose down
```


## Dev-пользователи

Пароль у всех: **`Password123!`** (один `!`)

| Email | Роль |
|-------|------|
| `employee@kedo.local` | Работник |
| `manager@kedo.local` | Руководитель |
| `hr@kedo.local` | HR |
| `admin@kedo.local` | Администратор |

В UI: открыть http://127.0.0.1:5173 → логин с одним из email выше.