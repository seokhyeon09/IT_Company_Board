# -*- coding: utf-8 -*-
import pytest
from pydantic import ValidationError
from app.core.security import create_access_token, decode_access_token, generate_hmac_headers
from app.schemas.ticket import TicketCreateDTO, TicketPriorityEnum, TicketCategoryEnum

def test_pydantic_priority_coercion():
    """우선순위 한글, 영문, 숫자 입력 시 '0', '1', '2', '3' 문자열로 자동 변환 검증"""
    dto1 = TicketCreateDTO(title="네트워크 장애", category=TicketCategoryEnum.NETWORK, content="인터넷이 안돼요", priority="긴급")
    assert dto1.priority == TicketPriorityEnum.URGENT
    assert dto1.priority.value == "3"

    dto2 = TicketCreateDTO(title="모니터 고장", category=TicketCategoryEnum.HW, content="모니터 깜빡임", priority=2)
    assert dto2.priority == TicketPriorityEnum.HIGH
    assert dto2.priority.value == "2"

def test_pydantic_extra_forbid():
    """허용되지 않은 필드(매스 어사인먼트) 주입 시 검증 실패 검증"""
    with pytest.raises(ValidationError):
        TicketCreateDTO(
            title="정상 제목",
            category=TicketCategoryEnum.SW,
            content="정상 내용",
            deadline="2099-01-01T00:00:00Z", # Extra forbidden field!
        )

def test_jwt_token_encode_decode():
    """JWT 토큰 생성 및 클레임 복원 검증"""
    claims = {"sub": "42", "name": "홍길동", "is_officer": True}
    token = create_access_token(claims)
    decoded = decode_access_token(token)
    assert decoded["sub"] == "42"
    assert decoded["name"] == "홍길동"
    assert decoded["is_officer"] is True

def test_hmac_signature_generation():
    """HMAC 서명 헤더 생성 포맷 검증"""
    headers = generate_hmac_headers(user_id=42, method="POST", path="/api/v1/tickets/list", body=b"test")
    assert headers["X-Gateway-User-Id"] == "42"
    assert "X-Gateway-Timestamp" in headers
    assert len(headers["X-Gateway-Signature"]) == 64
