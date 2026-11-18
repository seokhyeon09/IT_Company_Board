# -*- coding: utf-8 -*-
import httpx
import pytest
from fastapi import HTTPException

from app.client.odoo_client import odoo_client


@pytest.mark.parametrize(
    "err_data,error_message,expected_status",
    [
        (
            {
                "name": "odoo.addons.it_helpdesk.utils.errors.NotFoundError",
                "message": "요청한 리소스가 존재하지 않습니다.",
            },
            "요청한 리소스가 존재하지 않습니다.",
            404,
        ),
        (
            {
                "name": "odoo.exceptions.UserError",
                "message": "제목을 입력해 주세요.",
            },
            "제목을 입력해 주세요.",
            400,
        ),
        (
            {
                "name": "odoo.exceptions.UserError",
                "message": "문의를 찾을 수 없습니다.",
            },
            "문의를 찾을 수 없습니다.",
            404,
        ),
        (
            {
                "name": "",
                "message": "이름이 비어 있는 오류입니다.",
            },
            "이름이 비어 있는 오류입니다.",
            400,
        ),
        (
            {
                "name": None,
                "message": "이름이 None인 오류입니다.",
            },
            "이름이 None인 오류입니다.",
            400,
        ),
        (
            {
                "message": "name 키가 없는 오류입니다.",
            },
            "name 키가 없는 오류입니다.",
            400,
        ),
        (
            {
                "name": 12345,
                "message": "name 형식이 문자열이 아닌 오류입니다.",
            },
            "name 형식이 문자열이 아닌 오류입니다.",
            400,
        ),
    ],
)
async def test_error_mapping_by_exception_class(
    err_data: dict,
    error_message: str,
    expected_status: int,
):
    """NotFoundError 클래스명 기반 404 매핑, 하위 호환, 방어적 name 처리를 검증한다."""
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "jsonrpc": "2.0",
                "id": 1,
                "error": {
                    "code": 200,
                    "message": "Odoo Server Error",
                    "data": err_data,
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
