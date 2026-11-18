# -*- coding: utf-8 -*-
from fastapi import APIRouter, Depends, Query

from app.core.security import get_current_officer_claims
from app.schemas.merge import (
    MergeCandidatesResponseDTO,
    TicketMergeRequestDTO,
    TicketMergeResponseDTO,
)
from app.services.merge_service import merge_service

router = APIRouter()


@router.get("/{ticket_id}/merge-candidates", response_model=MergeCandidatesResponseDTO)
async def get_merge_candidates(
    ticket_id: int,
    limit: int = Query(5, ge=1, le=20),
    claims: dict = Depends(get_current_officer_claims),
):
    """중복 문의 병합 후보 목록 조회 (담당자/관리자 전용)."""
    return await merge_service.get_candidates(
        ticket_id=ticket_id,
        user_id=int(claims["sub"]),
        limit=limit,
    )


@router.post("/{ticket_id}/merge", response_model=TicketMergeResponseDTO)
async def merge_ticket(
    ticket_id: int,
    dto: TicketMergeRequestDTO,
    claims: dict = Depends(get_current_officer_claims),
):
    """중복 문의를 대상 문의로 병합 (담당자/관리자 전용)."""
    return await merge_service.merge_ticket(
        ticket_id=ticket_id,
        dto=dto,
        user_id=int(claims["sub"]),
    )
