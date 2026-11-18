# -*- coding: utf-8 -*-
import pytest

from app.client.odoo_client import odoo_client
from app.core.messages import MSG_OFFICER_REQUIRED
from tests.helpers import auth_headers, make_client


@pytest.mark.parametrize("url,body", [
    ("/api/v1/tickets/bulk", {"ticket_ids": [1, 2], "action": "start_progress"}),
    ("/api/v1/tickets/10/notes", {"content": "사원 내부 메모 시도"}),
])
async def test_employee_forbidden_and_zero_odoo_calls(monkeypatch, url, body):
    calls = 0

    async def fake_call_json(*args, **kwargs):
        nonlocal calls
        calls += 1
        return {}

    monkeypatch.setattr(odoo_client, "call_json", fake_call_json)
    async with make_client() as client:
        resp = await client.post(
            url,
            json=body,
            headers=auth_headers(f"10.0.5.1-{url}", sub="21", is_officer=False),
        )
    assert resp.status_code == 403
    assert resp.json()["detail"] == MSG_OFFICER_REQUIRED
    assert calls == 0


async def test_bulk_action_forwarding(monkeypatch):
    captured = []

    async def fake_call_json(endpoint, params, user_id=None, timeout=10.0):
        captured.append((endpoint, params, user_id))
        return {
            "status": "success",
            "data": {
                "action": params["action"],
                "total": 2,
                "success_count": 2,
                "fail_count": 0,
                "results": [
                    {"id": 1, "ticket_number": "TKT-1", "ok": True, "message": "처리되었습니다."},
                    {"id": 2, "ticket_number": "TKT-2", "ok": True, "message": "처리되었습니다."},
                ],
            },
        }

    monkeypatch.setattr(odoo_client, "call_json", fake_call_json)
    async with make_client() as client:
        resp = await client.post(
            "/api/v1/tickets/bulk",
            json={
                "ticket_ids": [1, 2, 1],
                "action": "assign",
                "officer_id": 8,
                "reason": "  인계 사유  ",
            },
            headers=auth_headers("10.0.5.2", sub="7", is_officer=True),
        )
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "success"
    assert body["data"]["success_count"] == 2
    assert captured[0] == (
        "/api/v1/tickets/bulk",
        {
            "ticket_ids": [1, 2],
            "action": "assign",
            "officer_id": 8,
            "reason": "인계 사유",
        },
        7,
    )


@pytest.mark.parametrize("payload", [
    {"ticket_ids": [], "action": "start_progress"},
    {"ticket_ids": list(range(1, 52)), "action": "start_progress"},
    {"ticket_ids": [0], "action": "start_progress"},
    {"ticket_ids": [1], "action": "unknown_action"},
    {"ticket_ids": [1], "action": "assign"},
    {"ticket_ids": [1], "action": "close", "note": "가" * 2001},
    {"ticket_ids": [1], "action": "assign", "officer_id": 5, "reason": "나" * 501},
    {"ticket_ids": [1], "action": "start_progress", "extra": 1},
])
async def test_bulk_dto_validation_422(monkeypatch, payload):
    async def fake_call_json(*args, **kwargs):
        raise AssertionError("Odoo should not be called on 422")

    monkeypatch.setattr(odoo_client, "call_json", fake_call_json)
    async with make_client() as client:
        resp = await client.post(
            "/api/v1/tickets/bulk",
            json=payload,
            headers=auth_headers("10.0.5.3", sub="7", is_officer=True),
        )
    assert resp.status_code == 422


async def test_internal_notes_add_and_validation(monkeypatch):
    captured = []

    async def fake_call_json(endpoint, params, user_id=None, timeout=10.0):
        captured.append((endpoint, params, user_id))
        return {
            "status": "success",
            "data": {
                "id": 91,
                "author_id": 70,
                "author_name": "김담당",
                "date": "2026-11-18T02:00:00Z",
                "content": params["content"],
            },
        }

    monkeypatch.setattr(odoo_client, "call_json", fake_call_json)
    hdrs = auth_headers("10.0.5.4", sub="7", is_officer=True)
    async with make_client() as client:
        r_empty = await client.post("/api/v1/tickets/10/notes", json={"content": "   "}, headers=hdrs)
        r_long = await client.post("/api/v1/tickets/10/notes", json={"content": "가" * 2001}, headers=hdrs)
        r_ok = await client.post("/api/v1/tickets/10/notes", json={"content": "  내부 확인 완료  "}, headers=hdrs)

    assert r_empty.status_code == 422
    assert r_long.status_code == 422
    assert r_ok.status_code == 200
    assert r_ok.json()["data"]["content"] == "내부 확인 완료"
    assert captured == [("/api/v1/tickets/notes/add", {"ticket_id": 10, "content": "내부 확인 완료"}, 7)]


async def test_detail_passes_internal_notes_and_absence_passes_open_tickets(monkeypatch):
    async def fake_call_json(endpoint, params, user_id=None, timeout=10.0):
        if endpoint == "/api/v1/tickets/detail":
            return {
                "status": "success",
                "data": {
                    "id": 10,
                    "ticket_number": "TKT-2026-0010",
                    "title": "상세 테스트",
                    "category": "hw",
                    "status": "assigned",
                    "priority": "1",
                    "internal_notes": [
                        {
                            "id": 5,
                            "author_id": 70,
                            "author_name": "김담당",
                            "date": "2026-11-18T02:00:00Z",
                            "content": "담당자 비공개 메모",
                        }
                    ],
                },
            }
        return {
            "status": "success",
            "data": {"is_absent": True, "absent_until": None},
            "open_tickets": [
                {
                    "id": 10,
                    "ticket_number": "TKT-2026-0010",
                    "title": "상세 테스트",
                    "status": "assigned",
                    "priority": "1",
                    "category": "hw",
                }
            ],
            "open_ticket_total": 1,
        }

    monkeypatch.setattr(odoo_client, "call_json", fake_call_json)
    hdrs = auth_headers("10.0.5.5", sub="7", is_officer=True)
    async with make_client() as client:
        r_detail = await client.get("/api/v1/tickets/10", headers=hdrs)
        r_absence = await client.put("/api/v1/officers/me/absence", json={"is_absent": True}, headers=hdrs)

    assert r_detail.status_code == 200
    assert r_detail.json()["internal_notes"][0]["content"] == "담당자 비공개 메모"
    assert r_absence.status_code == 200
    assert r_absence.json()["open_ticket_total"] == 1
    assert r_absence.json()["open_tickets"][0]["ticket_number"] == "TKT-2026-0010"
