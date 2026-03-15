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
- Elasticsearch: `http://localhost:9200`
- Kibana: `http://localhost:5601`

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

## Логирование в стиле ELK

В проект добавлена централизованная схема логирования для backend и frontend:

- Backend пишет структурированные JSON-логи (stdout + Elasticsearch индекс `egypt-logs-YYYY.MM.DD`).
- Frontend отправляет клиентские ошибки и события в `POST /api/logs/frontend`.
- Kibana читает логи из Elasticsearch для поиска и построения дашбордов.

### Что уже логируется

- Все HTTP-запросы backend (метод, путь, статус, длительность, IP).
- Ошибки backend с traceback.
- Ошибки frontend: `window.onerror`, `unhandledrejection`.
- Ошибки API-запросов и события входа из frontend.

### Быстрый старт в Kibana

1. Откройте `http://localhost:5601`.
2. Перейдите в **Stack Management → Data Views**.
3. Создайте Data View с шаблоном `egypt-logs-*`.
4. Используйте поле времени `@timestamp`.
