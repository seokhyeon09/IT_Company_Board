# -*- coding: utf-8 -*-
from app.client.odoo_client import odoo_client
from app.schemas.attachment import AttachmentDTO, AttachmentDetailDTO, AttachmentUploadDTO

class AttachmentService:
    """Ticket Attachment Management Service"""

    async def upload_attachment(self, ticket_id: int, dto: AttachmentUploadDTO, user_id: int) -> AttachmentDTO:
        params = {
            "ticket_id": ticket_id,
            "name": dto.name,
            "datas": dto.datas,
            "mimetype": dto.mimetype,
        }
        result = await odoo_client.call_json("/api/v1/tickets/upload-attachment", params=params, user_id=user_id)
        return result.get("data", {})

    async def get_attachment(self, ticket_id: int, attachment_id: int, user_id: int) -> AttachmentDetailDTO:
        params = {
            "ticket_id": ticket_id,
            "attachment_id": attachment_id,
        }
        result = await odoo_client.call_json("/api/v1/tickets/get-attachment", params=params, user_id=user_id)
        return result.get("data", {})

attachment_service = AttachmentService()
