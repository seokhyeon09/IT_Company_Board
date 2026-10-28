# -*- coding: utf-8 -*-
from fastapi import HTTPException, status
from app.client.odoo_client import odoo_client
from app.schemas.ticket import (
    TicketResolveDTO,
    TicketRestartDTO,
    TicketUpdateResolutionDTO,
    TicketCloseDTO,
    TicketCancelDTO,
    TicketPendingDTO,
    TicketRateDTO,
    TicketResponseDTO,
)

class WorkflowService:
    """Ticket Workflow and State Transition Orchestration Service"""

    async def resolve_ticket(self, ticket_id: int, dto: TicketResolveDTO, claims: dict) -> TicketResponseDTO:
        if not claims.get("is_officer", False):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Helpdesk officer role required to resolve tickets"
            )
        user_id = int(claims["sub"])
        params = {
            "ticket_id": ticket_id,
            "resolution_note": dto.resolution_note,
            "if_match_write_date": dto.if_match_write_date
        }
        result = await odoo_client.call_json("/api/v1/tickets/resolve", params=params, user_id=user_id)
        return result.get("data", {})

    async def restart_ticket(self, ticket_id: int, dto: TicketRestartDTO, claims: dict) -> TicketResponseDTO:
        user_id = int(claims["sub"])
        params = {"ticket_id": ticket_id, "reason": dto.reason}
        result = await odoo_client.call_json("/api/v1/tickets/restart", params=params, user_id=user_id)
        return result.get("data", {})

    async def update_resolution(self, ticket_id: int, dto: TicketUpdateResolutionDTO, claims: dict) -> TicketResponseDTO:
        if not claims.get("is_officer", False):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Helpdesk officer role required to update resolutions"
            )
        user_id = int(claims["sub"])
        params = {
            "ticket_id": ticket_id,
            "resolution_note": dto.resolution_note,
            "if_match_write_date": dto.if_match_write_date
        }
        result = await odoo_client.call_json("/api/v1/tickets/update-resolution", params=params, user_id=user_id)
        return result.get("data", {})

    async def assign_ticket(self, ticket_id: int, claims: dict) -> TicketResponseDTO:
        if not claims.get("is_officer", False):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Helpdesk officer role required to assign tickets"
            )
        user_id = int(claims["sub"])
        result = await odoo_client.call_json("/api/v1/tickets/assign", params={"ticket_id": ticket_id}, user_id=user_id)
        return result.get("data", {})

    async def start_progress_ticket(self, ticket_id: int, claims: dict) -> TicketResponseDTO:
        if not claims.get("is_officer", False):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Helpdesk officer role required to start progress on tickets"
            )
        user_id = int(claims["sub"])
        result = await odoo_client.call_json("/api/v1/tickets/start-progress", params={"ticket_id": ticket_id}, user_id=user_id)
        return result.get("data", {})

    async def pending_ticket(self, ticket_id: int, dto: TicketPendingDTO, claims: dict) -> TicketResponseDTO:
        if not claims.get("is_officer", False):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Helpdesk officer role required to request pending status"
            )
        user_id = int(claims["sub"])
        result = await odoo_client.call_json(
            "/api/v1/tickets/pending",
            params={"ticket_id": ticket_id, "reason": dto.reason},
            user_id=user_id
        )
        return result.get("data", {})

    async def close_ticket(self, ticket_id: int, dto: TicketCloseDTO, claims: dict) -> TicketResponseDTO:
        if not claims.get("is_officer", False):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Helpdesk officer role required to close tickets"
            )
        user_id = int(claims["sub"])
        result = await odoo_client.call_json(
            "/api/v1/tickets/close",
            params={"ticket_id": ticket_id, "note": dto.note},
            user_id=user_id
        )
        return result.get("data", {})

    async def cancel_ticket(self, ticket_id: int, dto: TicketCancelDTO, claims: dict) -> TicketResponseDTO:
        user_id = int(claims["sub"])
        result = await odoo_client.call_json(
            "/api/v1/tickets/cancel",
            params={"ticket_id": ticket_id, "reason": dto.reason},
            user_id=user_id
        )
        return result.get("data", {})

    async def toggle_faq(self, ticket_id: int, claims: dict) -> TicketResponseDTO:
        if not claims.get("is_officer", False):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Helpdesk officer role required to toggle FAQ status"
            )
        user_id = int(claims["sub"])
        result = await odoo_client.call_json("/api/v1/tickets/toggle-faq", params={"ticket_id": ticket_id}, user_id=user_id)
        return result.get("data", {})

    async def rate_ticket(self, ticket_id: int, dto: TicketRateDTO, claims: dict) -> TicketResponseDTO:
        user_id = int(claims["sub"])
        params = {
            "ticket_id": ticket_id,
            "rating": str(dto.rating),
            "rating_comment": dto.rating_comment,
            "if_match_write_date": dto.if_match_write_date
        }
        result = await odoo_client.call_json("/api/v1/tickets/rate", params=params, user_id=user_id)
        return result.get("data", {})

workflow_service = WorkflowService()
