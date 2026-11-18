# -*- coding: utf-8 -*-
import csv
import io
import pytest

from app.client.odoo_client import odoo_client
from app.core.messages import (
    MSG_OFFICER_REQUIRED,
    MSG_REPORT_CATEGORY_INVALID,
    MSG_REPORT_DATE_INVALID,
    MSG_REPORT_DATE_ORDER,
    MSG_REPORT_RANGE_EXCEEDED,
    MSG_REPORT_UNIT_INVALID,
)
from app.services.report_service import (
    CATEGORY_HEADERS,
    PRIORITY_HEADERS,
    SERIES_HEADERS,
    build_sla_report_csv_bytes,
)
from app.utils.csv_export import kst_today_yyyymmdd
from tests.helpers import auth_headers, make_client


def _sample_report_data():
    return {
        "range": {"date_from": "2026-11-02", "date_to": "2026-11-18", "unit": "week", "category": "hw"},
        "summary": {
            "created": 5,
            "resolved": 4,
            "on_time": 3,
            "breached": 1,
            "on_time_rate": 75.0,
            "avg_resolution_hours": 2.4,
            "open_now": 2,
            "overdue_now": 1,
            "paused_now": 0,
            "avg_paused_hours": 1.2,
        },
        "series": [
            {
                "period": "2026-11-02",
                "created": 3,
                "resolved": 4,
                "on_time": 3,
                "breached": 1,
                "on_time_rate": 75.0,
                "avg_resolution_hours": 2.4,
            },
            {
                "period": "2026-11-09",
                "created": 2,
                "resolved": 0,
                "on_time": 0,
                "breached": 0,
                "on_time_rate": None,
                "avg_resolution_hours": None,
            },
        ],
        "by_category": [
            {"category": "hw", "label": "하드웨어", "created": 5, "resolved": 4, "on_time_rate": 75.0, "avg_resolution_hours": 2.4},
            {"category": "sw", "label": "소프트웨어", "created": 0, "resolved": 0, "on_time_rate": None, "avg_resolution_hours": None},
        ],
        "by_priority": [
            {"priority": "0", "label": "낮음", "created": 1, "resolved": 1, "on_time_rate": 100.0, "avg_resolution_hours": 1.0},
            {"priority": "3", "label": "긴급", "created": 4, "resolved": 3, "on_time_rate": 66.7, "avg_resolution_hours": 2.9},
        ],
    }


@pytest.mark.parametrize("url", ["/api/v1/reports/sla", "/api/v1/reports/sla/export"])
async def test_reports_forbidden_for_employee(monkeypatch, url):
    calls = 0

    async def fake_call_json(*args, **kwargs):
        nonlocal calls
        calls += 1
        return {}

    monkeypatch.setattr(odoo_client, "call_json", fake_call_json)
    async with make_client() as client:
        resp = await client.get(url, headers=auth_headers(f"10.0.5.1-{url}", sub="21", is_officer=False))
    assert resp.status_code == 403
    assert resp.json()["detail"] == MSG_OFFICER_REQUIRED
    assert calls == 0


async def test_get_sla_report_success_and_forwarding(monkeypatch):
    captured = {}

    async def fake_call_json(endpoint, params, user_id=None, timeout=10.0):
        captured["endpoint"] = endpoint
        captured["params"] = params
        captured["user_id"] = user_id
        return {"status": "success", "data": _sample_report_data()}

    monkeypatch.setattr(odoo_client, "call_json", fake_call_json)
    async with make_client() as client:
        resp = await client.get(
            "/api/v1/reports/sla?date_from=2026-11-02&date_to=2026-11-18&unit=week&category=hw",
            headers=auth_headers("10.0.5.2", sub="7", is_officer=True),
        )

    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "success"
    assert body["data"]["summary"]["on_time_rate"] == 75.0
    assert body["data"]["series"][1]["on_time_rate"] is None
    assert captured == {
        "endpoint": "/api/v1/reports/sla",
        "params": {"date_from": "2026-11-02", "date_to": "2026-11-18", "unit": "week", "category": "hw"},
        "user_id": 7,
    }


@pytest.mark.parametrize(
    "query,expected_detail",
    [
        ("date_from=2026-13-01&date_to=2026-11-18", MSG_REPORT_DATE_INVALID),
        ("date_from=bad-date", MSG_REPORT_DATE_INVALID),
        ("date_from=2026-11-20&date_to=2026-11-18", MSG_REPORT_DATE_ORDER),
        ("date_from=2025-01-01&date_to=2026-01-02", MSG_REPORT_RANGE_EXCEEDED),
        ("unit=day", MSG_REPORT_UNIT_INVALID),
        ("category=unknown", MSG_REPORT_CATEGORY_INVALID),
    ],
)
async def test_get_sla_report_validation_422_korean(monkeypatch, query, expected_detail):
    async def fake_call_json(*args, **kwargs):
        raise AssertionError("Odoo should not be called on 422")

    monkeypatch.setattr(odoo_client, "call_json", fake_call_json)
    async with make_client() as client:
        resp = await client.get(
            f"/api/v1/reports/sla?{query}",
            headers=auth_headers(f"10.0.5.3-{query}", sub="7", is_officer=True),
        )
    assert resp.status_code == 422
    assert resp.json()["detail"] == expected_detail


async def test_export_sla_report_csv_route_and_sections(monkeypatch):
    async def fake_call_json(endpoint, params, user_id=None, timeout=10.0):
        assert endpoint == "/api/v1/reports/sla"
        return {"status": "success", "data": _sample_report_data()}

    monkeypatch.setattr(odoo_client, "call_json", fake_call_json)
    async with make_client() as client:
        resp = await client.get(
            "/api/v1/reports/sla/export?date_from=2026-11-02&date_to=2026-11-18&unit=week",
            headers=auth_headers("10.0.5.4", sub="7", is_officer=True),
        )

    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("text/csv")
    expected_name = f"sla-report_{kst_today_yyyymmdd()}.csv"
    assert f"filename*=UTF-8''{expected_name}" in resp.headers["content-disposition"]
    assert resp.content.startswith(b"\xef\xbb\xbf")

    rows = list(csv.reader(io.StringIO(resp.content.decode("utf-8-sig"), newline="")))
    assert rows[0] == SERIES_HEADERS
    assert rows[1] == ["2026-11-02", "3", "4", "3", "1", "75.0", "2.4"]
    assert rows[2] == ["2026-11-09", "2", "0", "0", "0", "", ""]
    assert rows[3] == []
    assert rows[4] == CATEGORY_HEADERS
    assert rows[5] == ["하드웨어", "5", "4", "75.0", "2.4"]
    assert rows[6] == ["소프트웨어", "0", "0", "", ""]
    assert rows[7] == []
    assert rows[8] == PRIORITY_HEADERS
    assert rows[9] == ["낮음", "1", "1", "100.0", "1.0"]


def test_build_sla_report_csv_formula_defense():
    data = _sample_report_data()
    data["series"][0]["period"] = "=1+1"
    data["by_category"][0]["label"] = "+cmd"
    raw = build_sla_report_csv_bytes(data)
    rows = list(csv.reader(io.StringIO(raw.decode("utf-8-sig"), newline="")))
    assert rows[1][0] == "'=1+1"
    assert rows[5][0] == "'+cmd"
