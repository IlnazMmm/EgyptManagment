from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from db import fetch_all, fetch_one


def _linear_regression_forecast(values: list[float], horizon: int) -> list[float]:
    """Simple OLS linear regression forecast without external dependencies."""
    n = len(values)
    if n < 2:
        return [values[-1] if values else 0.0 for _ in range(horizon)]

    x_mean = (n - 1) / 2
    y_mean = sum(values) / n

    numerator = sum((i - x_mean) * (v - y_mean) for i, v in enumerate(values))
    denominator = sum((i - x_mean) ** 2 for i in range(n))
    slope = numerator / denominator if denominator else 0.0
    intercept = y_mean - slope * x_mean

    forecast = []
    for x in range(n, n + horizon):
        forecast.append(max(0.0, intercept + slope * x))
    return forecast


def _format_compact(value: int) -> str:
    return f"{value:,}".replace(",", " ")


RISK_SCORES = {
    "Высокий": 0.9,
    "Средний": 0.6,
    "Низкий": 0.25,
    "Не прогнозируется": 0.1,
}


def _build_turnover_trend(stats: dict) -> tuple[list[int], list[int]]:
    base = max(4, stats["total"])
    high = stats["high"]
    medium = stats["medium"]
    low = stats["low"]

    trend = [
        max(1, round(base * 0.15 + high * 2 + medium * 0.8)),
        max(1, round(base * 0.16 + high * 2.1 + medium * 0.85)),
        max(1, round(base * 0.14 + high * 1.9 + medium * 0.75)),
        max(1, round(base * 0.17 + high * 2.2 + medium * 0.9)),
        max(1, round(base * 0.16 + high * 2.0 + medium * 0.85 + low * 0.2)),
        max(1, round(base * 0.18 + high * 2.3 + medium * 0.95 + low * 0.2)),
    ]
    forecast = [max(1, round(v)) for v in _linear_regression_forecast([float(v) for v in trend], 6)]
    return trend, forecast


def _employees_risk_stats() -> dict:
    rows = fetch_all("SELECT risk FROM employees")
    total = len(rows)
    high = sum(1 for row in rows if row["risk"] == "Высокий")
    medium = sum(1 for row in rows if row["risk"] == "Средний")
    low = sum(1 for row in rows if row["risk"] == "Низкий")
    scored = [RISK_SCORES.get(row["risk"], 0.2) for row in rows]
    avg_risk = round(sum(scored) / len(scored), 2) if scored else 0
    return {"total": total, "high": high, "medium": medium, "low": low, "avg": avg_risk}


FORECAST_BASE = {
    "Продукты питания": {
        "revenue": [420000, 380000, 480000, 700000, 520000, 850000, 610000, 980000, 640000, 720000, 1020000, 690000],
        "orders": [220, 210, 245, 300, 265, 345, 288, 372, 304, 322, 390, 336],
    },
    "Напитки": {
        "revenue": [360000, 330000, 420000, 620000, 470000, 760000, 540000, 820000, 560000, 620000, 900000, 610000],
        "orders": [190, 182, 210, 268, 236, 315, 255, 340, 268, 284, 352, 292],
    },
    "Бытовая химия": {
        "revenue": [300000, 280000, 360000, 520000, 430000, 640000, 470000, 700000, 500000, 560000, 760000, 540000],
        "orders": [155, 148, 182, 232, 205, 270, 221, 292, 226, 241, 308, 250],
    },
}

PERIOD_POINTS = {"Последующие 30 дней": 12, "Последующие 14 дней": 8, "Последующие 7 дней": 6}

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
    stats = _employees_risk_stats()
    trend, forecast_values = _build_turnover_trend(stats)

    return {
        "totalEmployees": stats["total"],
        "highRisk": stats["high"],
        "mediumRisk": stats["medium"],
        "avgRisk": stats["avg"],
        "trend": trend,
        "forecast": forecast_values,
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
    stats = _employees_risk_stats()
    total = max(stats["total"], 1)
    risky_total = stats["high"] + stats["medium"]

    tp = round(risky_total * 0.78)
    fn = max(0, risky_total - tp)
    safe_total = max(0, total - risky_total)
    fp = max(1, round(safe_total * 0.12)) if safe_total else 0
    tn = max(0, safe_total - fp)

    precision = tp / (tp + fp) if (tp + fp) else 0
    recall = tp / (tp + fn) if (tp + fn) else 0
    auc = min(0.99, 0.72 + stats["avg"] * 0.3)
    accuracy = (tp + tn) / total

    return {
        "auc": f"{auc * 100:.1f}%",
        "accuracy": f"{accuracy * 100:.1f}%",
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "tn": tn,
        "precision": round(precision, 3),
        "recall": round(recall, 3),
    }


@app.get("/api/sales-analysis")
def sales_analysis(
    category: str = Query(default="Продукты питания"),
    period: str = Query(default="Последующие 30 дней"),
) -> dict:
    category_data = FORECAST_BASE.get(category, FORECAST_BASE["Продукты питания"])
    points_count = PERIOD_POINTS.get(period, PERIOD_POINTS["Последующие 30 дней"])

    revenue_history = category_data["revenue"][:points_count]
    orders_history = category_data["orders"][:points_count]

    revenue_value = sum(revenue_history)
    orders_value = sum(orders_history)
    avg_check = round(revenue_value / orders_value) if orders_value else 0
    units = round(orders_value * 1.95)

    risk_stats = _employees_risk_stats()
    returns_ratio = 0.035 + risk_stats["avg"] * 0.02
    returns = round(units * returns_ratio)
    conversion = min(12.0, 2.8 + risk_stats["avg"] * 4 + (orders_value / max(points_count, 1)) / 180)

    ranked_products = [
        ("Йогурт клубничный", revenue_history[-1] * 1.08),
        ("Чипсы картофельные", revenue_history[-2] * 1.03 if len(revenue_history) > 1 else revenue_history[-1]),
        ("Орехи миндаль", revenue_history[-3] * 0.98 if len(revenue_history) > 2 else revenue_history[-1]),
        ("Сок апельсиновый", revenue_history[-1] * 0.96),
    ]
    top_products = [item[0] for item in sorted(ranked_products, key=lambda p: p[1], reverse=True)[:3]]

    region_by_category = {
        "Продукты питания": ["Москва", "Санкт-Петербург", "Казань"],
        "Напитки": ["Екатеринбург", "Новосибирск", "Нижний Новгород"],
        "Бытовая химия": ["Ростов-на-Дону", "Самара", "Москва"],
    }

    return {
        "revenue": f"{_format_compact(revenue_value)} ₽",
        "orders": orders_value,
        "units": units,
        "returns": returns,
        "avgCheck": f"{_format_compact(avg_check)} ₽",
        "conversion": f"{conversion:.1f}%",
        "topProducts": top_products,
        "regions": region_by_category.get(category, region_by_category["Продукты питания"]),
    }


@app.get("/api/forecast")
def forecast(
    category: str = Query(default="Продукты питания"),
    period: str = Query(default="Последующие 30 дней"),
) -> dict:
    category_data = FORECAST_BASE.get(category, FORECAST_BASE["Продукты питания"])
    points_count = PERIOD_POINTS.get(period, PERIOD_POINTS["Последующие 30 дней"])

    revenue_history = category_data["revenue"][:points_count]
    orders_history = category_data["orders"][:points_count]

    horizon = 4
    revenue_forecast = [round(v) for v in _linear_regression_forecast(revenue_history, horizon)]
    orders_forecast = [round(v) for v in _linear_regression_forecast(orders_history, horizon)]

    revenue_value = sum(revenue_forecast)
    orders_value = sum(orders_forecast)
    avg_check = round(revenue_value / orders_value) if orders_value else 0

    first_revenue_avg = sum(revenue_history[: len(revenue_history) // 2]) / max(1, len(revenue_history) // 2)
    second_revenue_avg = sum(revenue_history[len(revenue_history) // 2 :]) / max(1, len(revenue_history) - len(revenue_history) // 2)
    revenue_delta = ((second_revenue_avg - first_revenue_avg) / first_revenue_avg * 100) if first_revenue_avg else 0

    first_orders_avg = sum(orders_history[: len(orders_history) // 2]) / max(1, len(orders_history) // 2)
    second_orders_avg = sum(orders_history[len(orders_history) // 2 :]) / max(1, len(orders_history) - len(orders_history) // 2)
    orders_delta = ((second_orders_avg - first_orders_avg) / first_orders_avg * 100) if first_orders_avg else 0

    avg_check_history = [round(r / o) if o else 0 for r, o in zip(revenue_history, orders_history)]
    avg_check_delta = 0
    if len(avg_check_history) > 1 and avg_check_history[0] != 0:
        avg_check_delta = ((avg_check_history[-1] - avg_check_history[0]) / avg_check_history[0]) * 100

    labels = [
        "5 апр",
        "8 апр",
        "10 апр",
        "12 апр",
        "16 апр",
        "18 апр",
        "22 апр",
        "25 апр",
        "27 апр",
        "30 апр",
        "2 мая",
        "5 мая",
    ][:points_count]

    return {
        "filters": {
            "category": category,
            "period": period,
            "categories": list(FORECAST_BASE.keys()),
            "periods": list(PERIOD_POINTS.keys()),
        },
        "kpis": {
            "revenue": {"value": f"{_format_compact(revenue_value)} ₽", "delta": f"{revenue_delta:+.0f}%"},
            "orders": {"value": _format_compact(orders_value), "delta": f"{orders_delta:+.0f}%"},
            "avgCheck": {"value": f"{_format_compact(avg_check)} ₽", "delta": f"{avg_check_delta:+.0f}%"},
        },
        "chart": {
            "labels": labels,
            "revenueHistory": revenue_history,
            "revenueForecast": revenue_forecast,
            "ordersHistory": orders_history,
            "ordersForecast": orders_forecast,
        },
    }


@app.get("/api/alerts")
def alerts() -> dict:
    stats = _employees_risk_stats()

    items = []
    if stats["high"]:
        items.append(
            {
                "level": "critical",
                "title": "Найдено сотрудников с высоким риском ухода",
                "description": f"Требуется план удержания для {stats['high']} сотрудник(ов).",
            }
        )
    if stats["medium"]:
        items.append(
            {
                "level": "warning",
                "title": "Повышенный риск в команде",
                "description": f"У {stats['medium']} сотрудник(ов) средний риск ухода.",
            }
        )
    if stats["avg"] < 0.3:
        items.append(
            {
                "level": "info",
                "title": "Стабильная ситуация",
                "description": "Средний риск по команде находится в безопасной зоне.",
            }
        )

    critical = sum(1 for item in items if item["level"] == "critical")
    warning = sum(1 for item in items if item["level"] == "warning")
    info = sum(1 for item in items if item["level"] == "info")

    return {
        "critical": critical,
        "warning": warning,
        "info": info,
        "items": items,
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
