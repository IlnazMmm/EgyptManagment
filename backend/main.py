from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from db import fetch_all, fetch_one
from services import AnalyticsService

app = FastAPI(title="AI Retail Analytics API", version="1.0.0")
analytics_service = AnalyticsService()

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
    return analytics_service.get_dashboard()


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
    return analytics_service.get_reports()


@app.get("/api/sales-analysis")
def sales_analysis(
    category: str = Query(default="Продукты питания"),
    period: str = Query(default="Последующие 30 дней"),
) -> dict:
    return analytics_service.get_sales_analysis(category=category, period=period)


@app.get("/api/forecast")
def forecast(
    category: str = Query(default="Продукты питания"),
    period: str = Query(default="Последующие 30 дней"),
) -> dict:
    return analytics_service.get_forecast(category=category, period=period)


@app.get("/api/alerts")
def alerts() -> dict:
    return analytics_service.get_alerts()


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
