# -*- coding: utf-8 -*-
import pytest

from app.client.odoo_client import odoo_client
from app.core.messages import MSG_OFFICER_REQUIRED
from tests.helpers import auth_headers, make_client


@pytest.mark.parametrize("method,url,body", [
    ("GET", "/api/v1/tickets/10/merge-candidates", None),
    ("POST", "/api/v1/tickets/10/merge", {"target_id": 11, "reason": "중복"}),
])
async def test_merge_employee_forbidden_and_zero_odoo_calls(monkeypatch, method, url, body):
    calls = 0

    async def fake_call_json(*args, **kwargs):
        nonlocal calls
        calls += 1
        return {}

    monkeypatch.setattr(odoo_client, "call_json", fake_call_json)
    async with make_client() as client:
        if method == "GET":
            resp = await client.get(
                url,
                headers=auth_headers(f"10.0.6.1-{url}", sub="21", is_officer=False),
            )
        else:
            resp = await client.post(
                url,
                json=body,
                headers=auth_headers(f"10.0.6.1-{url}", sub="21", is_officer=False),
            )
    assert resp.status_code == 403
    assert resp.json()["detail"] == MSG_OFFICER_REQUIRED
    assert calls == 0


async def test_merge_and_candidates_forwarding(monkeypatch):
    captured = []

    async def fake_call_json(endpoint, params, user_id=None, timeout=10.0):
        captured.append((endpoint, params, user_id))
        if endpoint == "/api/v1/tickets/merge-candidates":
            return {
                "status": "success",
                "data": {
                    "candidates": [
                        {
                            "id": 11,
                            "ticket_number": "TKT-2026-0011",
                            "title": "VPN 접속 오류",
                            "status": "in_progress",
                            "author_name": "김사원",
                            "create_date": "2026-11-18T01:00:00Z",
                            "score": 0.75,
                        }
                    ]
                },
            }
        return {
            "status": "success",
            "data": {
                "id": 10,
                "ticket_number": "TKT-2026-0010",
                "status": "canceled",
                "merged_into_id": 11,
                "merged_into_number": "TKT-2026-0011",
            },
        }

    monkeypatch.setattr(odoo_client, "call_json", fake_call_json)
    hdrs = auth_headers("10.0.6.2", sub="7", is_officer=True)
    async with make_client() as client:
        r_cands = await client.get("/api/v1/tickets/10/merge-candidates?limit=3", headers=hdrs)
        r_merge = await client.post(
            "/api/v1/tickets/10/merge",
            json={"target_id": 11, "reason": "  동일 장애  "},
            headers=hdrs,
        )

    assert r_cands.status_code == 200
    assert r_cands.json()["data"]["candidates"][0]["ticket_number"] == "TKT-2026-0011"
    assert r_merge.status_code == 200
    assert r_merge.json()["data"]["merged_into_number"] == "TKT-2026-0011"
    assert captured == [
        ("/api/v1/tickets/merge-candidates", {"ticket_id": 10, "limit": 3}, 7),
        ("/api/v1/tickets/merge", {"ticket_id": 10, "target_id": 11, "reason": "동일 장애"}, 7),
    ]


@pytest.mark.parametrize("payload", [
    {"target_id": 0},
    {"target_id": -1},
    {"target_id": True},
    {"target_id": 11, "reason": "가" * 501},
    {"target_id": 11, "extra": 1},
])
async def test_merge_dto_validation_422(monkeypatch, payload):
    async def fake_call_json(*args, **kwargs):
        raise AssertionError("Odoo should not be called on 422")

    monkeypatch.setattr(odoo_client, "call_json", fake_call_json)
    async with make_client() as client:
        resp = await client.post(
            "/api/v1/tickets/10/merge",
            json=payload,
            headers=auth_headers("10.0.6.3", sub="7", is_officer=True),
        )
    assert resp.status_code == 422


async def test_ticket_list_and_detail_pass_merge_fields(monkeypatch):
    async def fake_call_json(endpoint, params, user_id=None, timeout=10.0):
        if endpoint == "/api/v1/tickets/list":
            return {
                "status": "success",
                "total": 1,
                "data": [
                    {
                        "id": 10,
                        "ticket_number": "TKT-2026-0010",
                        "title": "원본 문의",
                        "category": "network",
                        "status": "canceled",
                        "priority": "1",
                        "merged_into_id": 11,
                        "merged_into_number": "TKT-2026-0011",
                    }
                ],
            }
        return {
            "status": "success",
            "data": {
                "id": 11,
                "ticket_number": "TKT-2026-0011",
                "title": "대상 문의",
                "category": "network",
                "status": "in_progress",
                "priority": "1",
                "merged_into_id": None,
                "merged_into_number": None,
                "merged_tickets": [
                    {
                        "id": 10,
                        "ticket_number": "TKT-2026-0010",
                        "title": "원본 문의",
                        "status": "canceled",
                        "author_name": "박사원",
                    }
                ],
            },
        }

    monkeypatch.setattr(odoo_client, "call_json", fake_call_json)
    hdrs = auth_headers("10.0.6.4", sub="7", is_officer=True)
    async with make_client() as client:
        r_list = await client.get("/api/v1/tickets", headers=hdrs)
        r_detail = await client.get("/api/v1/tickets/11", headers=hdrs)

    assert r_list.status_code == 200
    assert r_list.json()["data"][0]["merged_into_number"] == "TKT-2026-0011"
    assert r_detail.status_code == 200
    assert r_detail.json()["merged_tickets"][0]["ticket_number"] == "TKT-2026-0010"
