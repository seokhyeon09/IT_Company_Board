# -*- coding: utf-8 -*-
import httpx
import pytest
from fastapi import HTTPException

from app.client.odoo_client import odoo_client


@pytest.mark.parametrize(
    "error_name,error_message,expected_status",
    [
        ("odoo.exceptions.UserError", "문의를 찾을 수 없습니다.", 404),
        ("odoo.exceptions.UserError", "제목을 입력해 주세요.", 400),
        ("odoo.exceptions.UserError", "Ticket not found.", 404),
    ],
)
async def test_user_error_korean_and_english_status_mapping(
    error_name: str,
    error_message: str,
    expected_status: int,
):
    """한글/영문 UserError 메시지에 따라 404 또는 400 HTTPException으로 매핑된다."""
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "jsonrpc": "2.0",
                "id": 1,
                "error": {
                    "code": 200,
                    "message": "Odoo Server Error",
                    "data": {
                        "name": error_name,
                        "message": error_message,
                    },
                },
            },
        )

    prev_client = odoo_client._client
    mock_client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    odoo_client._client = mock_client
    try:
        with pytest.raises(HTTPException) as exc_info:
            await odoo_client.call_json("/api/v1/tickets/detail", {"ticket_id": 999}, user_id=7)
    finally:
        await mock_client.aclose()
        odoo_client._client = prev_client

    assert exc_info.value.status_code == expected_status
    assert exc_info.value.detail == error_message
