from dataclasses import dataclass

from db import fetch_all


@dataclass(frozen=True)
class RiskStats:
    total: int
    high: int
    medium: int
    low: int
    avg: float


class AnalyticsService:
    risk_scores = {
        "Высокий": 0.9,
        "Средний": 0.6,
        "Низкий": 0.25,
        "Не прогнозируется": 0.1,
    }

    forecast_base = {
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

    period_points = {"Последующие 30 дней": 12, "Последующие 14 дней": 8, "Последующие 7 дней": 6}

    def get_dashboard(self) -> dict:
        stats = self._employees_risk_stats()
        trend, forecast = self._build_turnover_trend(stats)
        return {
            "totalEmployees": stats.total,
            "highRisk": stats.high,
            "mediumRisk": stats.medium,
            "avgRisk": stats.avg,
            "trend": trend,
            "forecast": forecast,
        }

    def get_reports(self) -> dict:
        stats = self._employees_risk_stats()
        total = max(stats.total, 1)
        risky_total = stats.high + stats.medium

        tp = round(risky_total * 0.78)
        fn = max(0, risky_total - tp)
        safe_total = max(0, total - risky_total)
        fp = max(1, round(safe_total * 0.12)) if safe_total else 0
        tn = max(0, safe_total - fp)

        precision = tp / (tp + fp) if (tp + fp) else 0
        recall = tp / (tp + fn) if (tp + fn) else 0
        auc = min(0.99, 0.72 + stats.avg * 0.3)
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

    def get_sales_analysis(self, category: str, period: str) -> dict:
        category_data, points_count = self._get_series(category, period)
        revenue_history = category_data["revenue"][:points_count]
        orders_history = category_data["orders"][:points_count]

        revenue_value = sum(revenue_history)
        orders_value = sum(orders_history)
        avg_check = round(revenue_value / orders_value) if orders_value else 0
        units = round(orders_value * 1.95)

        risk_stats = self._employees_risk_stats()
        returns_ratio = 0.035 + risk_stats.avg * 0.02
        returns = round(units * returns_ratio)
        conversion = min(12.0, 2.8 + risk_stats.avg * 4 + (orders_value / max(points_count, 1)) / 180)

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

        selected_category = category if category in self.forecast_base else "Продукты питания"
        return {
            "revenue": f"{self._format_compact(revenue_value)} ₽",
            "orders": orders_value,
            "units": units,
            "returns": returns,
            "avgCheck": f"{self._format_compact(avg_check)} ₽",
            "conversion": f"{conversion:.1f}%",
            "topProducts": top_products,
            "regions": region_by_category[selected_category],
        }

    def get_forecast(self, category: str, period: str) -> dict:
        category_data, points_count = self._get_series(category, period)

        revenue_history = category_data["revenue"][:points_count]
        orders_history = category_data["orders"][:points_count]

        horizon = 4
        revenue_forecast = [round(v) for v in self._linear_regression_forecast(revenue_history, horizon)]
        orders_forecast = [round(v) for v in self._linear_regression_forecast(orders_history, horizon)]

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

        safe_category = category if category in self.forecast_base else "Продукты питания"
        safe_period = period if period in self.period_points else "Последующие 30 дней"

        return {
            "filters": {
                "category": safe_category,
                "period": safe_period,
                "categories": list(self.forecast_base.keys()),
                "periods": list(self.period_points.keys()),
            },
            "kpis": {
                "revenue": {"value": f"{self._format_compact(revenue_value)} ₽", "delta": f"{revenue_delta:+.0f}%"},
                "orders": {"value": self._format_compact(orders_value), "delta": f"{orders_delta:+.0f}%"},
                "avgCheck": {"value": f"{self._format_compact(avg_check)} ₽", "delta": f"{avg_check_delta:+.0f}%"},
            },
            "chart": {
                "labels": labels,
                "revenueHistory": revenue_history,
                "revenueForecast": revenue_forecast,
                "ordersHistory": orders_history,
                "ordersForecast": orders_forecast,
            },
        }

    def get_alerts(self) -> dict:
        stats = self._employees_risk_stats()

        items = []
        if stats.high:
            items.append(
                {
                    "level": "critical",
                    "title": "Найдено сотрудников с высоким риском ухода",
                    "description": f"Требуется план удержания для {stats.high} сотрудник(ов).",
                }
            )
        if stats.medium:
            items.append(
                {
                    "level": "warning",
                    "title": "Повышенный риск в команде",
                    "description": f"У {stats.medium} сотрудник(ов) средний риск ухода.",
                }
            )
        if stats.avg < 0.3:
            items.append(
                {
                    "level": "info",
                    "title": "Стабильная ситуация",
                    "description": "Средний риск по команде находится в безопасной зоне.",
                }
            )

        return {
            "critical": sum(1 for item in items if item["level"] == "critical"),
            "warning": sum(1 for item in items if item["level"] == "warning"),
            "info": sum(1 for item in items if item["level"] == "info"),
            "items": items,
        }

    def _employees_risk_stats(self) -> RiskStats:
        rows = fetch_all("SELECT risk FROM employees")
        total = len(rows)
        high = sum(1 for row in rows if row["risk"] == "Высокий")
        medium = sum(1 for row in rows if row["risk"] == "Средний")
        low = sum(1 for row in rows if row["risk"] == "Низкий")
        scored = [self.risk_scores.get(row["risk"], 0.2) for row in rows]
        avg_risk = round(sum(scored) / len(scored), 2) if scored else 0
        return RiskStats(total=total, high=high, medium=medium, low=low, avg=avg_risk)

    def _build_turnover_trend(self, stats: RiskStats) -> tuple[list[int], list[int]]:
        base = max(4, stats.total)

        trend = [
            max(1, round(base * 0.15 + stats.high * 2 + stats.medium * 0.8)),
            max(1, round(base * 0.16 + stats.high * 2.1 + stats.medium * 0.85)),
            max(1, round(base * 0.14 + stats.high * 1.9 + stats.medium * 0.75)),
            max(1, round(base * 0.17 + stats.high * 2.2 + stats.medium * 0.9)),
            max(1, round(base * 0.16 + stats.high * 2.0 + stats.medium * 0.85 + stats.low * 0.2)),
            max(1, round(base * 0.18 + stats.high * 2.3 + stats.medium * 0.95 + stats.low * 0.2)),
        ]
        forecast = [max(1, round(v)) for v in self._linear_regression_forecast([float(v) for v in trend], 6)]
        return trend, forecast

    def _get_series(self, category: str, period: str) -> tuple[dict, int]:
        selected_category = category if category in self.forecast_base else "Продукты питания"
        selected_period = period if period in self.period_points else "Последующие 30 дней"
        return self.forecast_base[selected_category], self.period_points[selected_period]

    @staticmethod
    def _linear_regression_forecast(values: list[float], horizon: int) -> list[float]:
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

    @staticmethod
    def _format_compact(value: int) -> str:
        return f"{value:,}".replace(",", " ")
