# -*- coding: utf-8 -*-
from fastapi import APIRouter, Depends, status
from app.core.security import get_current_user_claims
from app.services.attachment_service import attachment_service
from app.schemas.attachment import AttachmentDTO, AttachmentDetailDTO, AttachmentUploadDTO

router = APIRouter()

@router.post("/{ticket_id}/attachments", response_model=AttachmentDTO, status_code=status.HTTP_201_CREATED)
async def upload_attachment(
    ticket_id: int,
    dto: AttachmentUploadDTO,
    claims: dict = Depends(get_current_user_claims),
):
    """Upload Base64 attachment for a ticket."""
    return await attachment_service.upload_attachment(ticket_id, dto, user_id=int(claims["sub"]))

@router.get("/{ticket_id}/attachments/{attachment_id}", response_model=AttachmentDetailDTO)
async def get_attachment(
    ticket_id: int,
    attachment_id: int,
    claims: dict = Depends(get_current_user_claims),
):
    """Retrieve Base64 attachment data."""
    return await attachment_service.get_attachment(ticket_id, attachment_id, user_id=int(claims["sub"]))
