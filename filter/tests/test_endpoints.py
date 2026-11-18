# -*- coding: utf-8 -*-
from datetime import timedelta
import httpx
import pytest

from app.main import app
from app.client.odoo_client import odoo_client
from app.core.messages import (
    MSG_AUTH_INVALID,
    MSG_BACKEND_ERROR,
    MSG_BACKEND_UNAVAILABLE,
    MSG_INTERNAL_ERROR,
    MSG_LOGIN_FAILED,
    MSG_OFFICER_REQUIRED,
)
from app.core.security import create_access_token


def _ip(addr: str) -> dict:
    return {"X-Forwarded-For": addr}


def _auth_headers(addr: str, *, sub: str = "10", is_officer: bool = False) -> dict:
    token = create_access_token({
        "sub": sub,
        "name": "테스트사용자",
        "login": "tester",
        "is_officer": is_officer,
    })
    return {"Authorization": f"Bearer {token}", "X-Forwarded-For": addr}


def _make_client() -> httpx.AsyncClient:
    return httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app, raise_app_exceptions=False),
        base_url="http://test",
    )


async def test_login_success(monkeypatch):
    async def fake_call_json(endpoint, params, user_id=None, timeout=10.0):
        assert endpoint == "/api/v1/auth/login"
        return {
            "status": "success",
            "data": {
                "uid": 7,
                "name": "김담당",
                "login": "officer01",
                "is_officer": True,
                "is_manager": False,
                "is_admin": False,
            },
        }

    monkeypatch.setattr(odoo_client, "call_json", fake_call_json)
    async with _make_client() as client:
        resp = await client.post(
            "/api/v1/auth/login",
            json={"login": "officer01", "password": "pw"},
            headers=_ip("10.0.1.1"),
        )
    assert resp.status_code == 200
    body = resp.json()
    assert body["access_token"]
    assert body["user"]["is_officer"] is True


async def test_login_failure_hides_odoo_message(monkeypatch):
    async def fake_call_json(endpoint, params, user_id=None, timeout=10.0):
        return {"status": "error", "message": "Access Denied"}

    monkeypatch.setattr(odoo_client, "call_json", fake_call_json)
    async with _make_client() as client:
        resp = await client.post(
            "/api/v1/auth/login",
            json={"login": "unknown", "password": "wrong"},
            headers=_ip("10.0.1.2"),
        )
    assert resp.status_code == 401
    assert resp.json()["detail"] == MSG_LOGIN_FAILED
    assert "Access Denied" not in resp.text


async def test_tickets_requires_token():
    async with _make_client() as client:
        resp = await client.get("/api/v1/tickets", headers=_ip("10.0.1.3"))
    assert resp.status_code in (401, 403)
    assert not (200 <= resp.status_code < 300)


@pytest.mark.parametrize("token_mode", ["forged", "expired"])
async def test_invalid_or_expired_token_returns_401_korean(token_mode):
    if token_mode == "forged":
        token = "forged.jwt.token"
    else:
        token = create_access_token({"sub": "10"}, expires_delta=timedelta(minutes=-5))

    headers = {"Authorization": f"Bearer {token}", "X-Forwarded-For": f"10.0.1.4-{token_mode}"}
    async with _make_client() as client:
        resp = await client.get("/api/v1/tickets", headers=headers)
    assert resp.status_code == 401
    assert resp.json()["detail"] == MSG_AUTH_INVALID
    assert resp.headers.get("www-authenticate") == "Bearer"


async def test_officer_stats_forbidden_for_employee(monkeypatch):
    calls = 0

    async def fake_call_json(*args, **kwargs):
        nonlocal calls
        calls += 1
        return {}

    monkeypatch.setattr(odoo_client, "call_json", fake_call_json)
    async with _make_client() as client:
        resp = await client.get(
            "/api/v1/tickets/officer-stats",
            headers=_auth_headers("10.0.1.5", sub="21", is_officer=False),
        )
    assert resp.status_code == 403
    assert resp.json()["detail"] == MSG_OFFICER_REQUIRED
    assert calls == 0


async def test_list_tickets_forwards_params_and_user_id(monkeypatch):
    captured = {}

    async def fake_call_json(endpoint, params, user_id=None, timeout=10.0):
        captured["endpoint"] = endpoint
        captured["params"] = params
        captured["user_id"] = user_id
        return {
            "status": "success",
            "total": 1,
            "data": [
                {
                    "id": 101,
                    "ticket_number": "TKT-2026-0101",
                    "title": "VPN 접속 오류",
                    "category": "network",
                    "status": "in_progress",
                    "priority": "2",
                    "is_overdue": False,
                    "sla_state": "normal",
                    "assignee_name": "김담당",
                    "is_faq": False,
                }
            ],
        }

    monkeypatch.setattr(odoo_client, "call_json", fake_call_json)
    async with _make_client() as client:
        resp = await client.get(
            "/api/v1/tickets?status=in_progress&search=VPN&offset=0&limit=12",
            headers=_auth_headers("10.0.1.6", sub="7", is_officer=True),
        )
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] == 1
    assert body["data"][0]["ticket_number"] == "TKT-2026-0101"
    assert captured["endpoint"] == "/api/v1/tickets/list"
    assert captured["user_id"] == 7
    assert captured["params"]["status"] == "in_progress"
    assert captured["params"]["search"] == "VPN"
    assert captured["params"]["limit"] == 12


async def test_unhandled_exception_hides_internal_detail(monkeypatch):
    async def explode(*args, **kwargs):
        raise RuntimeError("secret-internal-detail")

    monkeypatch.setattr(odoo_client, "call_json", explode)
    async with _make_client() as client:
        resp = await client.get(
            "/api/v1/tickets",
            headers=_auth_headers("10.0.1.7", sub="7", is_officer=True),
        )
    assert resp.status_code == 500
    assert "secret-internal-detail" not in resp.text
    body = resp.json()
    assert body["detail"] == MSG_INTERNAL_ERROR
    assert body["error"]["code"] == "INTERNAL_SERVER_ERROR"
    assert body["error"]["message"] == MSG_INTERNAL_ERROR


@pytest.mark.parametrize(
    "case,expected_status,expected_detail",
    [
        ("connect_error", 503, MSG_BACKEND_UNAVAILABLE),
        ("http_500", 502, MSG_BACKEND_ERROR),
        ("jsonrpc_access_error", 403, "접근 권한이 없습니다."),
        ("http_409", 409, "이미 수정된 티켓입니다."),
    ],
)
async def test_odoo_client_error_mapping(case, expected_status, expected_detail):
    def handler(request: httpx.Request) -> httpx.Response:
        if case == "connect_error":
            raise httpx.ConnectError("connection refused", request=request)
        if case == "http_500":
            return httpx.Response(500, text="Internal Server Error")
        if case == "jsonrpc_access_error":
            return httpx.Response(
                200,
                json={
                    "jsonrpc": "2.0",
                    "id": 1,
                    "error": {
                        "code": 200,
                        "message": "Odoo Server Error",
                        "data": {"name": "odoo.exceptions.AccessError", "message": "접근 권한이 없습니다."},
                    },
                },
            )
        return httpx.Response(409, json={"error": {"data": {"message": "이미 수정된 티켓입니다."}}})

    prev_client = odoo_client._client
    mock_client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    odoo_client._client = mock_client
    try:
        async with _make_client() as client:
            resp = await client.get(
                "/api/v1/tickets",
                headers=_auth_headers(f"10.0.1.8-{case}", sub="7", is_officer=True),
            )
    finally:
        await mock_client.aclose()
        odoo_client._client = prev_client

    assert resp.status_code == expected_status
    assert resp.json()["detail"] == expected_detail


async def test_login_rate_limit_blocks_16th_request(monkeypatch):
    async def fake_call_json(*args, **kwargs):
        return {"status": "error", "message": "Access Denied"}

    monkeypatch.setattr(odoo_client, "call_json", fake_call_json)
    headers = _ip("10.0.1.99")
    async with _make_client() as client:
        for _ in range(15):
            r = await client.post("/api/v1/auth/login", json={"login": "u1", "password": "pw"}, headers=headers)
            assert r.status_code == 401
        blocked = await client.post("/api/v1/auth/login", json={"login": "u1", "password": "pw"}, headers=headers)
    assert blocked.status_code == 429
    assert "Retry-After" in blocked.headers
