# -*- coding: utf-8 -*-
from typing import Optional
from fastapi import APIRouter, Depends, Query, status

from app.core.security import get_current_officer_claims
from app.schemas.reply_template import (
    ReplyTemplateCreateDTO,
    ReplyTemplateDeleteResponseDTO,
    ReplyTemplateListResponseDTO,
    ReplyTemplateResponseDTO,
    ReplyTemplateUpdateDTO,
)
from app.services.reply_template_service import reply_template_service

router = APIRouter()


@router.get("", response_model=ReplyTemplateListResponseDTO)
async def list_reply_templates(
    category: Optional[str] = Query(None, description="분류 (hw, sw, network, account, etc)"),
    claims: dict = Depends(get_current_officer_claims),
):
    """답변 상용구 목록 조회 (담당자/관리자 전용)."""
    return await reply_template_service.list_templates(
        user_id=int(claims["sub"]),
        category=category,
    )


@router.post("", response_model=ReplyTemplateResponseDTO, status_code=status.HTTP_201_CREATED)
async def create_reply_template(
    dto: ReplyTemplateCreateDTO,
    claims: dict = Depends(get_current_officer_claims),
):
    """답변 상용구 생성 (담당자/관리자 전용)."""
    return await reply_template_service.create_template(
        dto=dto,
        user_id=int(claims["sub"]),
    )


@router.put("/{template_id}", response_model=ReplyTemplateResponseDTO)
async def update_reply_template(
    template_id: int,
    dto: ReplyTemplateUpdateDTO,
    claims: dict = Depends(get_current_officer_claims),
):
    """답변 상용구 수정 (본인 것만, 관리자는 전체)."""
    return await reply_template_service.update_template(
        template_id=template_id,
        dto=dto,
        user_id=int(claims["sub"]),
    )


@router.delete("/{template_id}", response_model=ReplyTemplateDeleteResponseDTO)
async def delete_reply_template(
    template_id: int,
    claims: dict = Depends(get_current_officer_claims),
):
    """답변 상용구 삭제 (본인 것만, 관리자는 전체)."""
    return await reply_template_service.delete_template(
        template_id=template_id,
        user_id=int(claims["sub"]),
    )
