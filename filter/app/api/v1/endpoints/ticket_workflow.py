# -*- coding: utf-8 -*-
from typing import Optional
from fastapi import APIRouter, Depends
from app.core.security import get_current_user_claims
from app.services import workflow_service
from app.schemas.workflow import (
    TicketResolveDTO,
    TicketRestartDTO,
    TicketUpdateResolutionDTO,
    TicketAssignDTO,
    TicketPendingDTO,
    TicketCloseDTO,
    TicketCancelDTO,
    TicketRateDTO,
)

router = APIRouter()

@router.post("/{ticket_id}/resolve")
async def resolve_ticket(
    ticket_id: int,
    dto: TicketResolveDTO,
    claims: dict = Depends(get_current_user_claims),
):
    """Resolve an IT ticket (Officer restricted, Optimistic concurrency guarded)."""
    return await workflow_service.resolve_ticket(ticket_id, dto, claims)

@router.post("/{ticket_id}/restart")
async def restart_ticket(
    ticket_id: int,
    dto: Optional[TicketRestartDTO] = None,
    claims: dict = Depends(get_current_user_claims),
):
    """Restart a ticket for follow-up inquiry."""
    dto = dto or TicketRestartDTO()
    return await workflow_service.restart_ticket(ticket_id, dto, claims)

@router.post("/{ticket_id}/update-resolution")
async def update_resolution(
    ticket_id: int,
    dto: TicketUpdateResolutionDTO,
    claims: dict = Depends(get_current_user_claims),
):
    """Update existing resolution notes."""
    return await workflow_service.update_resolution(ticket_id, dto, claims)

@router.post("/{ticket_id}/assign")
async def assign_ticket(
    ticket_id: int,
    dto: Optional[TicketAssignDTO] = None,
    claims: dict = Depends(get_current_user_claims),
):
    """Assign ticket to self or designated officer."""
    return await workflow_service.assign_ticket(ticket_id, claims, dto=dto)

@router.post("/{ticket_id}/assign-self")
async def assign_self(
    ticket_id: int,
    claims: dict = Depends(get_current_user_claims),
):
    """Assign ticket to current login officer."""
    return await workflow_service.assign_ticket(ticket_id, claims, dto=None)

@router.post("/{ticket_id}/start-progress")
async def start_progress_ticket(
    ticket_id: int,
    claims: dict = Depends(get_current_user_claims),
):
    """Start progress on an assigned or pending ticket."""
    return await workflow_service.start_progress_ticket(ticket_id, claims)

@router.post("/{ticket_id}/pending")
async def pending_ticket(
    ticket_id: int,
    dto: Optional[TicketPendingDTO] = None,
    claims: dict = Depends(get_current_user_claims),
):
    """Request employee additional response (status -> pending)."""
    dto = dto or TicketPendingDTO()
    return await workflow_service.pending_ticket(ticket_id, dto, claims)

@router.post("/{ticket_id}/reply-pending")
async def reply_pending_ticket(
    ticket_id: int,
    dto: Optional[TicketRestartDTO] = None,
    claims: dict = Depends(get_current_user_claims),
):
    """Reply to pending request by author (status -> in_progress)."""
    dto = dto or TicketRestartDTO()
    return await workflow_service.restart_ticket(ticket_id, dto, claims)

@router.post("/{ticket_id}/close")
async def close_ticket(
    ticket_id: int,
    dto: Optional[TicketCloseDTO] = None,
    claims: dict = Depends(get_current_user_claims),
):
    """Force close a ticket by officer."""
    dto = dto or TicketCloseDTO()
    return await workflow_service.close_ticket(ticket_id, dto, claims)

@router.post("/{ticket_id}/cancel")
async def cancel_ticket(
    ticket_id: int,
    dto: Optional[TicketCancelDTO] = None,
    claims: dict = Depends(get_current_user_claims),
):
    """Cancel ticket inquiry by author or officer."""
    dto = dto or TicketCancelDTO()
    return await workflow_service.cancel_ticket(ticket_id, dto, claims)

@router.post("/{ticket_id}/toggle-faq")
async def toggle_faq(
    ticket_id: int,
    claims: dict = Depends(get_current_user_claims),
):
    """Toggle FAQ recommendation."""
    return await workflow_service.toggle_faq(ticket_id, claims)

@router.post("/{ticket_id}/rate")
async def rate_ticket(
    ticket_id: int,
    dto: TicketRateDTO,
    claims: dict = Depends(get_current_user_claims),
):
    """Rate resolved ticket by author."""
    return await workflow_service.rate_ticket(ticket_id, dto, claims)
