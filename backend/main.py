from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from db import fetch_all, fetch_one

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


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/api/health/db")
def db_health() -> dict:
    row = fetch_one("SELECT 1 AS ok")
    return {"status": "ok", "db": row["ok"] == 1}


@app.post("/api/login")
def login(payload: LoginRequest) -> dict:
    row = fetch_one(
        "SELECT username FROM app_users WHERE username = %s AND password = %s",
        (payload.username, payload.password),
    )
    if row:
        return {
            "token": "mock-jwt-token",
            "username": row["username"],
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
    rows = fetch_all(
        """
        SELECT employee_id AS id, full_name AS name, position, department, risk
        FROM employees
        ORDER BY employee_id
        """
    )
    return {"items": rows}


@app.get("/api/employees/{employee_id}")
def get_employee(employee_id: str) -> dict:
    employee = fetch_one(
        """
        SELECT
          employee_id AS id,
          full_name AS name,
          position,
          department,
          risk,
          age,
          experience,
          salary,
          engagement,
          performance,
          work_hours AS "workHours"
        FROM employees
        WHERE employee_id = %s
        """,
        (employee_id,),
    )
    if not employee:
        raise HTTPException(status_code=404, detail="Сотрудник не найден")

    factors = fetch_all(
        """
        SELECT factor_name AS name, factor_value AS value
        FROM employee_factors
        WHERE employee_id = %s
        ORDER BY factor_value DESC
        """,
        (employee_id,),
    )

    return {**employee, "factors": factors}


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
    rows = fetch_all(
        """
        SELECT id, full_name AS name, email, role, status, username
        FROM app_users
        ORDER BY id
        """
    )
    return {"items": rows}
