# -*- coding: utf-8 -*-
from app.client.odoo_client import odoo_client
from app.core.config import settings
from tests.helpers import make_client


def _mock_login_fail(monkeypatch):
    async def fake_call_json(endpoint, params, user_id=None, timeout=10.0):
        return {"status": "error", "message": "Access Denied"}

    monkeypatch.setattr(odoo_client, "call_json", fake_call_json)


async def test_untrusted_proxy_ignores_xff_header(monkeypatch):
    """TRUST_PROXY_HEADERS=False이면 X-Forwarded-For가 달라도 같은 버킷으로 제한된다."""
    _mock_login_fail(monkeypatch)
    monkeypatch.setattr(settings, "TRUST_PROXY_HEADERS", False)

    async with make_client() as client:
        for i in range(15):
            resp = await client.post(
                "/api/v1/auth/login",
                json={"login": "u1", "password": "pw"},
                headers={"X-Forwarded-For": f"198.51.100.{i + 1}"},
            )
            assert resp.status_code == 401
        blocked = await client.post(
            "/api/v1/auth/login",
            json={"login": "u1", "password": "pw"},
            headers={"X-Forwarded-For": "198.51.100.99"},
        )
    assert blocked.status_code == 429
    assert "Retry-After" in blocked.headers


async def test_trusted_proxy_uses_xff_per_bucket(monkeypatch):
    """TRUST_PROXY_HEADERS=True이면 X-Forwarded-For별로 버킷이 분리된다."""
    _mock_login_fail(monkeypatch)
    monkeypatch.setattr(settings, "TRUST_PROXY_HEADERS", True)

    async with make_client() as client:
        for i in range(16):
            resp = await client.post(
                "/api/v1/auth/login",
                json={"login": "u1", "password": "pw"},
                headers={"X-Forwarded-For": f"198.51.101.{i + 1}"},
            )
            assert resp.status_code == 401

        same_ip = {"X-Forwarded-For": "198.51.102.1"}
        for _ in range(15):
            resp = await client.post(
                "/api/v1/auth/login",
                json={"login": "u1", "password": "pw"},
                headers=same_ip,
            )
            assert resp.status_code == 401
        blocked = await client.post(
            "/api/v1/auth/login",
            json={"login": "u1", "password": "pw"},
            headers=same_ip,
        )
    assert blocked.status_code == 429


async def test_trusted_proxy_uses_rightmost_xff_hop(monkeypatch):
    """TRUST_PROXY_HEADERS=True이면 X-Forwarded-For의 마지막(가장 오른쪽) 값으로 버킷을 묶는다."""
    _mock_login_fail(monkeypatch)
    monkeypatch.setattr(settings, "TRUST_PROXY_HEADERS", True)

    async with make_client() as client:
        for _ in range(10):
            resp = await client.post(
                "/api/v1/auth/login",
                json={"login": "u1", "password": "pw"},
                headers={"X-Forwarded-For": "1.2.3.4, 10.0.0.5"},
            )
            assert resp.status_code == 401
        for _ in range(5):
            resp = await client.post(
                "/api/v1/auth/login",
                json={"login": "u1", "password": "pw"},
                headers={"X-Forwarded-For": "9.9.9.9, 10.0.0.5"},
            )
            assert resp.status_code == 401
        blocked = await client.post(
            "/api/v1/auth/login",
            json={"login": "u1", "password": "pw"},
            headers={"X-Forwarded-For": "9.9.9.9, 10.0.0.5"},
        )
    assert blocked.status_code == 429
