# -*- coding: utf-8 -*-
from tests.helpers import make_client


async def test_cors_exposes_export_headers():
    """프론트(다른 origin)가 CSV 내보내기 응답 헤더를 읽을 수 있어야 한다."""
    async with make_client() as client:
        resp = await client.get(
            "/health",
            headers={"Origin": "http://localhost:3000", "X-Forwarded-For": "10.9.9.1"},
        )
    exposed = resp.headers.get("access-control-expose-headers", "").lower()
    assert "x-export-truncated" in exposed
    assert "content-disposition" in exposed
