# EgyptManagment

Демо-приложение для анализа персонала и продаж в формате **React + FastAPI**.

## Структура

- `backend/` — API на FastAPI с mock-данными.
- `frontend/` — SPA на React (Vite) с экранами:
  - Авторизация
  - Панель управления
  - Сотрудники
  - Карточка сотрудника
  - Отчёты
  - Анализ продаж
  - Прогнозирование
  - Алерты
  - Пользователи
- `docker-compose.yml` — запуск всего приложения в Docker.

## Запуск (всё в Docker)

```bash
docker compose up --build
```

После запуска:

- Frontend: `http://localhost:5173`
- Backend health: `http://localhost:8000/health`

Остановка:

```bash
docker compose down
```

## Тестовые учётные данные

- `admin / admin123`
- `manager / manager123`

## Локальный запуск без Docker (опционально)

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev -- --host 0.0.0.0 --port 5173
```

## API-эндпоинты

- `POST /api/login`
- `GET /api/dashboard`
- `GET /api/employees`
- `GET /api/employees/{employee_id}`
- `GET /api/reports`
- `GET /api/sales-analysis`
- `GET /api/forecast`
- `GET /api/alerts`
- `GET /api/users`
