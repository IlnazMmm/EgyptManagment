from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="AI Retail Analytics API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class LoginRequest(BaseModel):
    username: str
    password: str


MOCK_USERS = [
    {"id": 1, "name": "Администратор Системы", "email": "admin@x5ingroup.ru", "role": "Администратор", "status": "Активен"},
    {"id": 2, "name": "Менеджер Продаж", "email": "manager@x5ingroup.ru", "role": "Менеджер", "status": "Активен"},
]

EMPLOYEES = [
    {"id": "EMP006", "name": "Albert Flores", "position": "Senior Accountant", "department": "Finance", "risk": "Низкий"},
    {"id": "EMP014", "name": "Annette Black", "position": "QA Engineer", "department": "IT", "risk": "Не прогнозируется"},
    {"id": "EMP012", "name": "Bessie Cooper", "position": "Team Lead", "department": "Customer Service", "risk": "Не прогнозируется"},
    {"id": "EMP010", "name": "Cameron Williamson", "position": "DevOps Engineer", "department": "IT", "risk": "Низкий"},
]


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/api/login")
def login(payload: LoginRequest) -> dict:
    credentials = {
        "admin": "admin123",
        "manager": "manager123",
    }
    if payload.username in credentials and credentials[payload.username] == payload.password:
        return {
            "token": "mock-jwt-token",
            "username": payload.username,
            "dashboardPath": "/dashboard",
        }
    raise HTTPException(status_code=401, detail="Неверные учетные данные")


@app.get("/api/dashboard")
def dashboard() -> dict:
    return {
        "totalEmployees": 15,
        "highRisk": 0,
        "mediumRisk": 12,
        "avgRisk": 0.48,
        "trend": [12, 15, 11, 18, 14, 16],
        "forecast": [11, 14, 13, 17, 15, 17],
    }


@app.get("/api/employees")
def get_employees() -> dict:
    return {"items": EMPLOYEES}


@app.get("/api/employees/{employee_id}")
def get_employee(employee_id: str) -> dict:
    employee = next((e for e in EMPLOYEES if e["id"] == employee_id), None)
    if not employee:
        raise HTTPException(status_code=404, detail="Сотрудник не найден")
    return {
        **employee,
        "age": 40,
        "experience": "7 лет 0 мес",
        "salary": "$95,000",
        "engagement": "88%",
        "performance": "92%",
        "workHours": "38 hrs",
        "factors": [
            {"name": "Satisfaction Score", "value": 0.12},
            {"name": "Work Hours Per Week", "value": 0.08},
            {"name": "Last Evaluation", "value": 0.06},
            {"name": "Salary", "value": 0.04},
        ],
    }


@app.get("/api/reports")
def reports() -> dict:
    return {
        "auc": "89.0%",
        "accuracy": "84.0%",
        "tp": 85,
        "fp": 12,
        "fn": 11,
        "tn": 142,
    }


@app.get("/api/sales-analysis")
def sales_analysis() -> dict:
    return {
        "revenue": "1 250 000 ₽",
        "orders": 6420,
        "units": 12350,
        "returns": 320,
        "avgCheck": "195 ₽",
        "conversion": "4.8%",
        "topProducts": ["Йогурт клубничный", "Чипсы картофельные", "Орехи миндаль"],
        "regions": ["Москва", "Санкт-Петербург", "Екатеринбург"],
    }


@app.get("/api/forecast")
def forecast() -> dict:
    return {
        "period": "30 дней",
        "kpis": {
            "revenue": {"value": "1 250 000 ₽", "delta": "+12%"},
            "orders": {"value": "6 420", "delta": "+15%"},
            "avgCheck": {"value": "195 ₽", "delta": "-8%"},
        },
    }


@app.get("/api/alerts")
def alerts() -> dict:
    return {
        "critical": 0,
        "warning": 0,
        "info": 0,
        "items": [],
    }


@app.get("/api/users")
def users() -> dict:
    return {"items": MOCK_USERS}
