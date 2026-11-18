# -*- coding: utf-8 -*-
from fastapi import APIRouter, Depends

from app.core.security import get_current_officer_claims
from app.schemas.bulk import BulkTicketResponseDTO, TicketBulkRequestDTO
from app.schemas.note import InternalNoteCreateDTO, InternalNoteResponseDTO
from app.services.bulk_note_service import bulk_note_service

router = APIRouter()


@router.post("/bulk", response_model=BulkTicketResponseDTO)
async def bulk_ticket_action(
    dto: TicketBulkRequestDTO,
    claims: dict = Depends(get_current_officer_claims),
):
    """티켓 일괄 처리 (담당자/관리자 전용)."""
    return await bulk_note_service.bulk_action(dto=dto, user_id=int(claims["sub"]))


@router.post("/{ticket_id}/notes", response_model=InternalNoteResponseDTO)
async def add_internal_note(
    ticket_id: int,
    dto: InternalNoteCreateDTO,
    claims: dict = Depends(get_current_officer_claims),
):
    """티켓 담당자 전용 내부 메모 추가 (사원 비노출)."""
    return await bulk_note_service.add_internal_note(
        ticket_id=ticket_id,
        dto=dto,
        user_id=int(claims["sub"]),
    )
