# -*- coding: utf-8 -*-
from typing import Optional
from app.client.odoo_client import odoo_client
from app.schemas.ticket import (
    TicketCreateDTO,
    TicketUpdateDTO,
    TicketResponseDTO,
    TicketDetailResponseDTO,
    TicketListResponseDTO,
)
from app.schemas.attachment import AttachmentUploadDTO, AttachmentDTO, AttachmentDetailDTO
from app.schemas.insight import (
    TicketStatsResponseDTO,
    OfficerStatsResponseDTO,
    OfficerListResponseDTO,
    EmailNotificationListResponseDTO,
    NotificationReadDTO,
    NotificationReadResponseDTO,
)
from app.services.attachment_service import attachment_service
from app.services.insight_service import insight_service

class TicketService:
    """Core Ticket Query and Management Service"""

    async def list_tickets(
        self,
        user_id: int,
        category: Optional[str] = None,
        priority: Optional[str] = None,
        status: Optional[str] = None,
        search: Optional[str] = None,
        is_faq: Optional[bool] = None,
        is_overdue: Optional[bool] = None,
        assigned_to_me: Optional[bool] = None,
        sort_by: Optional[str] = "id desc",
        offset: int = 0,
        limit: int = 50,
    ) -> TicketListResponseDTO:
        params = {
            "category": category,
            "priority": priority,
            "status": status,
            "search": search,
            "is_faq": is_faq,
            "is_overdue": is_overdue,
            "assigned_to_me": assigned_to_me,
            "sort_by": sort_by,
            "offset": offset,
            "limit": limit,
        }
        result = await odoo_client.call_json("/api/v1/tickets/list", params=params, user_id=user_id)
        return TicketListResponseDTO(
            status="success",
            total=result.get("total", 0),
            data=result.get("data", []),
        )

    async def get_detail(self, ticket_id: int, user_id: int) -> TicketDetailResponseDTO:
        result = await odoo_client.call_json(
            "/api/v1/tickets/detail",
            params={"ticket_id": ticket_id},
            user_id=user_id,
        )
        return result.get("data", {})

    async def create_ticket(self, dto: TicketCreateDTO, user_id: int) -> TicketResponseDTO:
        params = dto.model_dump()
        result = await odoo_client.call_json("/api/v1/tickets/create", params=params, user_id=user_id)
        return result.get("data", {})

    async def update_ticket(self, ticket_id: int, dto: TicketUpdateDTO, user_id: int) -> TicketResponseDTO:
        params = {"ticket_id": ticket_id, **dto.model_dump(exclude_unset=True)}
        result = await odoo_client.call_json("/api/v1/tickets/update", params=params, user_id=user_id)
        return result.get("data", {})

    # Facade delegation for backward compatibility
    async def get_stats(self, user_id: int) -> TicketStatsResponseDTO:
        return await insight_service.get_stats(user_id)

    async def get_officer_stats(self, user_id: int) -> OfficerStatsResponseDTO:
        return await insight_service.get_officer_stats(user_id)

    async def get_notifications(self, user_id: int, limit: int = 30) -> EmailNotificationListResponseDTO:
        return await insight_service.get_notifications(user_id, limit)

    async def mark_notifications_read(self, user_id: int, dto: NotificationReadDTO) -> NotificationReadResponseDTO:
        return await insight_service.mark_notifications_read(user_id, dto)

    async def get_officers(self, user_id: int) -> OfficerListResponseDTO:
        return await insight_service.get_officers(user_id)

    async def upload_attachment(self, ticket_id: int, dto: AttachmentUploadDTO, user_id: int) -> AttachmentDTO:
        return await attachment_service.upload_attachment(ticket_id, dto, user_id)

    async def get_attachment(self, ticket_id: int, attachment_id: int, user_id: int) -> AttachmentDetailDTO:
        return await attachment_service.get_attachment(ticket_id, attachment_id, user_id)

ticket_service = TicketService()
