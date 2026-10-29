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

def test_ticket_rate_dto_validation():
    """만족도 평가 DTO 유효성 검증 (1~5 별점, 500자 이하 코멘트)"""
    from app.schemas.ticket import TicketRateDTO
    # 정상 별점
    rate_ok = TicketRateDTO(rating="5", rating_comment="친절한 조치 감사합니다.")
    assert rate_ok.rating == "5"

    # 유효하지 않은 별점 (0 또는 6 또는 문자)
    with pytest.raises(ValidationError):
        TicketRateDTO(rating="0")
    with pytest.raises(ValidationError):
        TicketRateDTO(rating="6")
    with pytest.raises(ValidationError):
        TicketRateDTO(rating="최고")

def test_ticket_resolve_dto_validation():
    """조치 완료 DTO 유효성 검증 (최소 5자 이상 조치 노트)"""
    from app.schemas.ticket import TicketResolveDTO
    resolve_ok = TicketResolveDTO(resolution_note="하드웨어 부품 교체 완료")
    assert resolve_ok.resolution_note == "하드웨어 부품 교체 완료"

    # 5자 미만 실패
    with pytest.raises(ValidationError):
        TicketResolveDTO(resolution_note="완료")

def test_odoo_false_to_none_normalization():
    """Odoo의 False 직렬화 값이 Pydantic DTO에서 None으로 안전 변환되는지 검증"""
    from app.schemas.ticket import TicketDetailResponseDTO
    raw_data = {
        "id": 100,
        "ticket_number": "TKT-2026-9999",
        "title": "테스트 티켓",
        "category": "hw",
        "status": "submitted",
        "priority": "1",
        "content": False,          # Odoo boolean False
        "resolution_note": False,  # Odoo boolean False
        "author_name": False,      # Odoo boolean False
        "rating_comment": False,   # Odoo boolean False
    }
    dto = TicketDetailResponseDTO(**raw_data)
    assert dto.content is None
    assert dto.resolution_note is None
    assert dto.author_name is None
    assert dto.rating_comment is None


def test_officer_stats_mttr_dto():
    """담당자 통계 응답 DTO에 MTTR(평균 해결 시간) 필드가 정상 직렬화되는지 검증"""
    from app.schemas.insight import OfficerStatsResponseDTO
    payload = {
        "status": "success",
        "data": {
            "officers": [
                {
                    "officer_id": 2,
                    "officer_name": "김담당",
                    "officer_email": "officer@test.com",
                    "total_assigned": 5,
                    "resolved_count": 3,
                    "avg_resolution_hours": 2.4,
                    "resolved_measured_count": 3,
                }
            ],
            "category_breakdown": [
                {"category": "hw", "label": "하드웨어", "count": 2, "percentage": 40.0, "avg_resolution_hours": 1.8}
            ],
            "overall_avg_resolution_hours": 2.4,
        },
    }
    parsed = OfficerStatsResponseDTO(**payload)
    assert parsed.data.overall_avg_resolution_hours == 2.4
    assert parsed.data.officers[0].avg_resolution_hours == 2.4
    assert parsed.data.officers[0].resolved_measured_count == 3
    assert parsed.data.category_breakdown[0].avg_resolution_hours == 1.8
