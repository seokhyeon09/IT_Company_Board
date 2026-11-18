# -*- coding: utf-8 -*-
from fastapi import APIRouter, Depends

from app.core.security import get_current_officer_claims
from app.schemas.absence import OfficerAbsenceResponseDTO, OfficerAbsenceUpdateDTO
from app.services.absence_service import absence_service

router = APIRouter()


@router.get("/me/absence", response_model=OfficerAbsenceResponseDTO)
async def get_my_absence(
    claims: dict = Depends(get_current_officer_claims),
):
    """담당자 본인 부재 상태 조회 (담당자/관리자 전용)."""
    return await absence_service.get_my_absence(user_id=int(claims["sub"]))


@router.put("/me/absence", response_model=OfficerAbsenceResponseDTO)
async def update_my_absence(
    dto: OfficerAbsenceUpdateDTO,
    claims: dict = Depends(get_current_officer_claims),
):
    """담당자 본인 부재 상태 변경 (담당자/관리자 전용)."""
    return await absence_service.update_my_absence(dto=dto, user_id=int(claims["sub"]))
