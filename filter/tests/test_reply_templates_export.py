# -*- coding: utf-8 -*-
import csv
import io
from datetime import date, datetime, timedelta, timezone
import pytest

from app.client.odoo_client import odoo_client
from app.core.messages import MSG_ABSENT_UNTIL_PAST, MSG_OFFICER_REQUIRED
from app.utils.csv_export import (
    CSV_HEADERS,
    build_ticket_csv_bytes,
    compute_resolution_hours_str,
    format_kst_datetime,
    kst_today_yyyymmdd,
    sanitize_csv_cell,
)
from tests.helpers import auth_headers, make_client


@pytest.mark.parametrize("method,url,body", [
    ("GET", "/api/v1/reply-templates", None),
    ("POST", "/api/v1/reply-templates", {"name": "제목", "category": "hw", "body": "본문"}),
    ("PUT", "/api/v1/reply-templates/1", {"name": "제목", "category": "", "body": "본문"}),
    ("DELETE", "/api/v1/reply-templates/1", None),
    ("GET", "/api/v1/officers/me/absence", None),
    ("PUT", "/api/v1/officers/me/absence", {"is_absent": True, "absent_until": None}),
    ("GET", "/api/v1/tickets/export", None),
])
async def test_employee_forbidden_on_new_endpoints(monkeypatch, method, url, body):
    calls = 0

    async def fake_call_json(*args, **kwargs):
        nonlocal calls
        calls += 1
        return {}

    monkeypatch.setattr(odoo_client, "call_json", fake_call_json)
    async with make_client() as client:
        resp = await client.request(
            method, url, json=body,
            headers=auth_headers(f"10.0.2.1-{method}-{url}", sub="21", is_officer=False),
        )
    assert resp.status_code == 403
    assert resp.json()["detail"] == MSG_OFFICER_REQUIRED
    assert calls == 0


@pytest.mark.parametrize("payload", [
    {"name": "", "category": "", "body": "본문"},
    {"name": "   ", "category": "", "body": "본문"},
    {"name": "가" * 61, "category": "", "body": "본문"},
    {"name": "제목", "category": "", "body": ""},
    {"name": "제목", "category": "", "body": "   "},
    {"name": "제목", "category": "", "body": "나" * 3001},
    {"name": "제목", "category": "invalid", "body": "본문"},
    {"name": "제목", "category": "hw", "body": "본문", "extra_field": 1},
])
async def test_reply_template_dto_422(monkeypatch, payload):
    async def fake_call_json(*args, **kwargs):
        raise AssertionError("Odoo should not be called on 422")

    monkeypatch.setattr(odoo_client, "call_json", fake_call_json)
    async with make_client() as client:
        resp = await client.post(
            "/api/v1/reply-templates", json=payload,
            headers=auth_headers("10.0.2.2", sub="7", is_officer=True),
        )
    assert resp.status_code == 422


async def test_reply_template_crud_forwarding(monkeypatch):
    calls = []

    async def fake_call_json(endpoint, params, user_id=None, timeout=10.0):
        calls.append((endpoint, params, user_id))
        item = {
            "id": 5, "name": "안내문", "category": "hw",
            "body": "본문 내용", "is_mine": True, "write_date": "2026-11-18T01:00:00Z",
        }
        if endpoint.endswith("/list"):
            return {"status": "success", "data": [item]}
        if endpoint.endswith("/delete"):
            return {"status": "success"}
        return {"status": "success", "data": item}

    monkeypatch.setattr(odoo_client, "call_json", fake_call_json)
    hdrs = auth_headers("10.0.2.3", sub="7", is_officer=True)
    async with make_client() as client:
        r_list = await client.get("/api/v1/reply-templates?category=hw", headers=hdrs)
        r_post = await client.post("/api/v1/reply-templates", json={"name": "  안내문  ", "category": "hw", "body": "  본문 내용  "}, headers=hdrs)
        r_put = await client.put("/api/v1/reply-templates/5", json={"name": "안내문", "category": "", "body": "수정 본문"}, headers=hdrs)
        r_del = await client.delete("/api/v1/reply-templates/5", headers=hdrs)

    assert (r_list.status_code, r_post.status_code, r_put.status_code, r_del.status_code) == (200, 201, 200, 200)
    assert r_del.json() == {"status": "success"}
    assert calls[0] == ("/api/v1/reply-templates/list", {"category": "hw"}, 7)
    assert calls[1] == ("/api/v1/reply-templates/create", {"name": "안내문", "category": "hw", "body": "본문 내용"}, 7)
    assert calls[2] == ("/api/v1/reply-templates/update", {"template_id": 5, "name": "안내문", "category": "", "body": "수정 본문"}, 7)
    assert calls[3] == ("/api/v1/reply-templates/delete", {"template_id": 5}, 7)


async def test_absence_endpoints_and_officers_dto(monkeypatch):
    captured = []
    today = date.today()
    past_str = (today - timedelta(days=1)).isoformat()
    future_str = (today + timedelta(days=3)).isoformat()

    async def fake_call_json(endpoint, params, user_id=None, timeout=10.0):
        captured.append((endpoint, params, user_id))
        if endpoint == "/api/v1/tickets/officers":
            return {"status": "success", "data": [{"id": 7, "name": "김담당", "login": "off", "is_absent": True, "absent_until": future_str}]}
        return {"status": "success", "data": {"is_absent": params.get("is_absent", True), "absent_until": params.get("absent_until")}}

    monkeypatch.setattr(odoo_client, "call_json", fake_call_json)
    hdrs = auth_headers("10.0.2.4", sub="7", is_officer=True)
    async with make_client() as client:
        r_past = await client.put("/api/v1/officers/me/absence", json={"is_absent": True, "absent_until": past_str}, headers=hdrs)
        r_extra = await client.put("/api/v1/officers/me/absence", json={"is_absent": True, "user_id": 99}, headers=hdrs)
        r_clear = await client.put("/api/v1/officers/me/absence", json={"is_absent": False, "absent_until": future_str}, headers=hdrs)
        r_get = await client.get("/api/v1/officers/me/absence", headers=hdrs)
        r_off = await client.get("/api/v1/tickets/officers", headers=hdrs)

    assert r_past.status_code == 400 and r_past.json()["detail"] == MSG_ABSENT_UNTIL_PAST
    assert r_extra.status_code == 422
    assert r_clear.status_code == 200 and r_clear.json()["data"] == {"is_absent": False, "absent_until": None}
    assert captured[0] == ("/api/v1/officers/me/absence/set", {"is_absent": False, "absent_until": None}, 7)
    assert r_get.status_code == 200 and captured[1] == ("/api/v1/officers/me/absence/get", {}, 7)
    assert r_off.status_code == 200
    assert r_off.json()["data"][0]["is_absent"] is True
    assert r_off.json()["data"][0]["absent_until"] == future_str


async def test_export_csv_route_headers_and_content(monkeypatch):
    async def fake_call_json(endpoint, params, user_id=None, timeout=10.0):
        assert endpoint == "/api/v1/tickets/export" and user_id == 7 and params["category"] == "hw"
        return {
            "status": "success",
            "total": 5001,
            "data": [{
                "id": 1, "ticket_number": "TKT-2026-0001", "title": '=cmd,"인용"\n다음줄',
                "category": "hw", "status": "in_progress", "priority": "2",
                "author_id": [10, "홍길동"], "assignee_id": [7, "김담당"], "assignee_name": "김담당",
                "create_date": "2026-11-18T00:30:00Z", "deadline": "2026-11-19T00:30:00Z",
                "is_overdue": True, "first_resolved_date": "2026-11-18T03:00:00Z",
                "rating": "0", "is_faq": False,
            }],
        }

    monkeypatch.setattr(odoo_client, "call_json", fake_call_json)
    async with make_client() as client:
        resp = await client.get(
            "/api/v1/tickets/export?category=hw",
            headers=auth_headers("10.0.2.5", sub="7", is_officer=True),
        )

    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("text/csv") and "charset=utf-8" in resp.headers["content-type"]
    assert resp.headers["content-disposition"] == f'attachment; filename="tickets_{kst_today_yyyymmdd()}.csv"'
    assert resp.headers.get("x-export-truncated") == "true"
    assert resp.content.startswith(b"\xef\xbb\xbf") and b"\r\n" in resp.content

    rows = list(csv.reader(io.StringIO(resp.content.decode("utf-8-sig"), newline="")))
    assert rows[0] == CSV_HEADERS
    assert rows[1] == [
        "TKT-2026-0001", '\'=cmd,"인용"\n다음줄', "하드웨어", "처리중", "높음",
        "홍길동", "김담당", "2026-11-18 09:30", "2026-11-19 09:30", "Y",
        "2026-11-18 12:00", "2.5", "", "N",
    ]


async def test_export_csv_not_truncated_when_under_limit(monkeypatch):
    async def fake_call_json(endpoint, params, user_id=None, timeout=10.0):
        return {"status": "success", "total": 1, "data": []}

    monkeypatch.setattr(odoo_client, "call_json", fake_call_json)
    async with make_client() as client:
        resp = await client.get("/api/v1/tickets/export", headers=auth_headers("10.0.2.6", sub="7", is_officer=True))
    assert resp.status_code == 200
    assert "x-export-truncated" not in resp.headers


def test_csv_export_pure_helpers():
    for prefix in ("=", "+", "-", "@", "\t", "\r"):
        assert sanitize_csv_cell(f"{prefix}1+1") == f"'{prefix}1+1"
    assert sanitize_csv_cell("정상 텍스트") == "정상 텍스트"
    assert format_kst_datetime("2026-11-18T16:45:00Z") == "2026-11-19 01:45"
    assert format_kst_datetime(False) == ""
    assert compute_resolution_hours_str("2026-11-18T00:00:00Z", "2026-11-18T01:30:00Z") == "1.5"
    assert compute_resolution_hours_str("2026-11-18T00:00:00Z", None) == ""
    assert kst_today_yyyymmdd(datetime(2026, 11, 18, 16, 0, tzinfo=timezone.utc)) == "20261119"
    raw = build_ticket_csv_bytes([{
        "ticket_number": "TKT-1", "title": "a,b", "category": "etc",
        "status": "closed", "priority": "0", "rating": "5", "is_faq": True,
    }])
    assert raw.startswith(b"\xef\xbb\xbf")
    parsed = list(csv.reader(io.StringIO(raw.decode("utf-8-sig"), newline="")))
    assert parsed[1][1:5] == ["a,b", "기타", "종결", "낮음"]
    assert parsed[1][12:14] == ["5", "Y"]
