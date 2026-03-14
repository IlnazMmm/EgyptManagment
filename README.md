# EgyptManagment

Демо-приложение для анализа персонала и продаж в формате **React + FastAPI + PostgreSQL**.

## Структура

- `backend/` — API на FastAPI.
- `frontend/` — SPA на React (Vite).
- `migrations/` — SQL-миграции для PostgreSQL.
- `docker-compose.yml` — запуск всего приложения в Docker.
- `.env.example` — пример переменных окружения (чувствительные данные вынесены в `.env`).

## Настройка переменных окружения

```bash
cp .env.example .env
```

При необходимости измените значения в `.env`:
- `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`
- `PGADMIN_DEFAULT_EMAIL`, `PGADMIN_DEFAULT_PASSWORD`
- `DATABASE_URL`

## Запуск (всё в Docker)

```bash
docker compose up --build
```

После запуска:

- Frontend: `http://localhost:5173`
- Backend health: `http://localhost:8000/health`
- Backend DB health: `http://localhost:8000/api/health/db`
- Postgres: `localhost:5432` (параметры из `.env`)
- pgAdmin: `http://localhost:5050` (параметры из `.env`)

Остановка:

```bash
docker compose down
```

> Начальная миграция `migrations/001_init.sql` автоматически применяется при первом старте Postgres.

## Подключение к БД через pgAdmin

1. Откройте `http://localhost:5050` и войдите под учётными данными из `.env`.
2. Добавьте новый Server:
   - **Host**: `${POSTGRES_HOST}` (в Docker-сети обычно `postgres`)
   - **Port**: `${POSTGRES_PORT}`
   - **Maintenance DB**: `${POSTGRES_DB}`
   - **Username**: `${POSTGRES_USER}`
   - **Password**: `${POSTGRES_PASSWORD}`

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
