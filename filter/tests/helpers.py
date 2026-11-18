# -*- coding: utf-8 -*-
import httpx
from app.main import app
from app.core.security import create_access_token


def auth_headers(addr: str, *, sub: str = "10", is_officer: bool = False) -> dict:
    token = create_access_token({
        "sub": sub,
        "name": "테스트사용자",
        "login": "tester",
        "is_officer": is_officer,
    })
    return {"Authorization": f"Bearer {token}", "X-Forwarded-For": addr}


def make_client() -> httpx.AsyncClient:
    return httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app, raise_app_exceptions=False),
        base_url="http://test",
    )
