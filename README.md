# EgyptManagment

Демо-приложение для анализа персонала и продаж в формате **React + FastAPI + PostgreSQL**.

## Структура

- `backend/` — API на FastAPI.
- `frontend/` — SPA на React (Vite).
- `migrations/` — SQL-миграции для PostgreSQL.
- `docker-compose.yml` — запуск всего приложения в Docker.

## Запуск (всё в Docker)

```bash
docker compose up --build
```

После запуска:

- Frontend: `http://localhost:5173`
- Backend health: `http://localhost:8000/health`
- Backend DB health: `http://localhost:8000/api/health/db`
- Postgres: `localhost:5432` (`postgres/postgres`, DB `egypt_management`)
- pgAdmin: `http://localhost:5050` (`admin@local.dev / admin`)

Остановка:

```bash
docker compose down
```

> Начальная миграция `migrations/001_init.sql` автоматически применяется при первом старте Postgres.

## Подключение к БД через pgAdmin

1. Откройте `http://localhost:5050` и войдите: `admin@local.dev / admin`.
2. Добавьте новый Server:
   - **Host**: `postgres`
   - **Port**: `5432`
   - **Maintenance DB**: `egypt_management`
   - **Username**: `postgres`
   - **Password**: `postgres`

## Тестовые учётные данные

- `admin / admin123`
- `manager / manager123`

## API-эндпоинты

- `POST /api/login`
- `GET /api/health/db`
- `GET /api/dashboard`
- `GET /api/employees`
- `GET /api/employees/{employee_id}`
- `GET /api/reports`
- `GET /api/sales-analysis`
- `GET /api/forecast`
- `GET /api/alerts`
- `GET /api/users`
