# -*- coding: utf-8 -*-
from app.client.odoo_client import odoo_client
from app.schemas.insight import (
    TicketStatsResponseDTO,
    OfficerStatsResponseDTO,
    OfficerListResponseDTO,
    EmailNotificationListResponseDTO,
    NotificationReadDTO,
    NotificationReadResponseDTO,
)

class InsightService:
    """Dashboard Analytics, Statistics, and Notification Service"""

    async def get_stats(self, user_id: int) -> TicketStatsResponseDTO:
        result = await odoo_client.call_json("/api/v1/tickets/stats", params={}, user_id=user_id)
        return TicketStatsResponseDTO(
            status="success",
            data=result.get("data", {}),
        )

    async def get_officer_stats(self, user_id: int) -> OfficerStatsResponseDTO:
        result = await odoo_client.call_json("/api/v1/tickets/officer-stats", params={}, user_id=user_id)
        return OfficerStatsResponseDTO(
            status="success",
            data=result.get("data", {}),
        )

    async def get_notifications(self, user_id: int, limit: int = 30) -> EmailNotificationListResponseDTO:
        result = await odoo_client.call_json("/api/v1/tickets/notifications", params={"limit": limit}, user_id=user_id)
        return EmailNotificationListResponseDTO(
            status="success",
            total=result.get("total", 0),
            data=result.get("data", []),
        )

    async def mark_notifications_read(self, user_id: int, dto: NotificationReadDTO) -> NotificationReadResponseDTO:
        result = await odoo_client.call_json(
            "/api/v1/tickets/notifications/read",
            params={"notification_ids": dto.notification_ids},
            user_id=user_id,
        )
        return NotificationReadResponseDTO(
            status="success",
            data=result.get("data", {}),
        )

    async def get_officers(self, user_id: int) -> OfficerListResponseDTO:
        result = await odoo_client.call_json("/api/v1/tickets/officers", params={}, user_id=user_id)
        return OfficerListResponseDTO(
            status="success",
            data=result.get("data", []),
        )

insight_service = InsightService()
