import re

from services.analytics_service import AnalyticsService


def test_dashboard_uses_employee_risk_distribution(monkeypatch):
    service = AnalyticsService()

    def fake_fetch_all(query, params=()):
        assert "SELECT risk FROM employees" in query
        return [
            {"risk": "Высокий"},
            {"risk": "Средний"},
            {"risk": "Средний"},
            {"risk": "Низкий"},
        ]

    monkeypatch.setattr("services.analytics_service.fetch_all", fake_fetch_all)

    result = service.get_dashboard()

    assert result["totalEmployees"] == 4
    assert result["highRisk"] == 1
    assert result["mediumRisk"] == 2
    assert result["avgRisk"] == 0.59
    assert len(result["trend"]) == 6
    assert len(result["forecast"]) == 6


def test_reports_metrics_shape_and_percent_format(monkeypatch):
    service = AnalyticsService()

    monkeypatch.setattr(
        "services.analytics_service.fetch_all",
        lambda query, params=(): [
            {"risk": "Высокий"},
            {"risk": "Средний"},
            {"risk": "Не прогнозируется"},
            {"risk": "Низкий"},
            {"risk": "Низкий"},
        ],
    )

    result = service.get_reports()

    assert set(result) == {"auc", "accuracy", "tp", "fp", "fn", "tn", "precision", "recall"}
    assert re.match(r"^\d+\.\d%$", result["auc"])
    assert re.match(r"^\d+\.\d%$", result["accuracy"])
    assert 0 <= result["precision"] <= 1
    assert 0 <= result["recall"] <= 1


def test_sales_analysis_fallbacks_for_unknown_filters(monkeypatch):
    service = AnalyticsService()

    monkeypatch.setattr(
        "services.analytics_service.fetch_all",
        lambda query, params=(): [{"risk": "Низкий"}] * 4,
    )

    result = service.get_sales_analysis(category="UNKNOWN", period="UNKNOWN")

    assert result["revenue"].endswith("₽")
    assert result["avgCheck"].endswith("₽")
    assert result["orders"] > 0
    assert result["units"] >= result["orders"]
    assert len(result["topProducts"]) == 3
    assert result["regions"] == ["Москва", "Санкт-Петербург", "Казань"]


def test_forecast_uses_safe_filters_for_unknown_values(monkeypatch):
    service = AnalyticsService()

    monkeypatch.setattr(
        "services.analytics_service.fetch_all",
        lambda query, params=(): [{"risk": "Средний"}] * 2,
    )

    result = service.get_forecast(category="UNKNOWN", period="UNKNOWN")

    assert result["filters"]["category"] == "Продукты питания"
    assert result["filters"]["period"] == "Последующие 30 дней"
    assert len(result["chart"]["revenueHistory"]) == 12
    assert len(result["chart"]["revenueForecast"]) == 4


def test_alerts_generates_warning_and_info_levels(monkeypatch):
    service = AnalyticsService()

    monkeypatch.setattr(
        "services.analytics_service.fetch_all",
        lambda query, params=(): [
            {"risk": "Средний"},
            {"risk": "Низкий"},
            {"risk": "Низкий"},
            {"risk": "Низкий"},
            {"risk": "Низкий"},
            {"risk": "Низкий"},
            {"risk": "Не прогнозируется"},
        ],
    )

    result = service.get_alerts()

    assert result["critical"] == 0
    assert result["warning"] == 1
    assert result["info"] == 1
    assert len(result["items"]) == 2
    assert {item["level"] for item in result["items"]} == {"warning", "info"}
