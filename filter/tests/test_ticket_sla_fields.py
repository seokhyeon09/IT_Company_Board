# -*- coding: utf-8 -*-
from app.client.odoo_client import odoo_client
from tests.helpers import auth_headers, make_client


async def test_ticket_detail_passes_sla_pause_fields(monkeypatch):
    async def fake_call_json(endpoint, params, user_id=None, timeout=10.0):
        assert endpoint == "/api/v1/tickets/detail"
        assert params == {"ticket_id": 42}
        return {
            "status": "success",
            "data": {
                "id": 42,
                "ticket_number": "TKT-2026-0042",
                "title": "모니터 깜빡임",
                "content": "<p>화면이 간헐적으로 꺼집니다.</p>",
                "category": "hw",
                "status": "pending",
                "priority": "2",
                "deadline": "2026-11-19T12:00:00Z",
                "is_overdue": False,
                "sla_state": "paused",
                "sla_paused_at": "2026-11-18T10:00:00Z",
                "sla_paused_seconds": 3600,
                "assignee_name": "김담당",
                "is_faq": False,
            },
        }

    monkeypatch.setattr(odoo_client, "call_json", fake_call_json)
    async with make_client() as client:
        resp = await client.get(
            "/api/v1/tickets/42",
            headers=auth_headers("10.0.9.1", sub="7", is_officer=True),
        )
    assert resp.status_code == 200
    body = resp.json()
    assert body["sla_state"] == "paused"
    assert body["is_overdue"] is False
    assert body["sla_paused_at"] == "2026-11-18T10:00:00Z"
    assert body["sla_paused_seconds"] == 3600
