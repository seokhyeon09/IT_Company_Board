# -*- coding: utf-8 -*-
from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status
from app.core.security import get_current_user_claims
from app.client.odoo_client import odoo_client
from app.schemas.ticket import (
    TicketCreateDTO,
    TicketResolveDTO,
    TicketRestartDTO,
    TicketUpdateResolutionDTO,
    TicketCloseDTO,
    TicketCancelDTO,
    TicketUpdateDTO,
    AttachmentDTO,
    AttachmentDetailDTO,
    AttachmentUploadDTO,
    TicketRateDTO,
    TicketResponseDTO,
    TicketDetailResponseDTO,
    TicketListResponseDTO,
    TicketStatsResponseDTO
)

router = APIRouter()

@router.get("", response_model=TicketListResponseDTO)
async def list_tickets(
    category: Optional[str] = Query(None, description="분류 (hw, sw, network, account, etc)"),
    priority: Optional[str] = Query(None, description="긴급도 (0, 1, 2, 3)"),
    status: Optional[str] = Query(None, description="상태"),
    search: Optional[str] = Query(None, description="검색어"),
    is_faq: Optional[bool] = Query(None, description="FAQ 여부"),
    is_overdue: Optional[bool] = Query(None, description="기한 초과 여부"),
    sort_by: Optional[str] = Query("id desc", description="정렬 옵션 (id desc, id asc, deadline asc, priority desc, write_date desc)"),
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    claims: dict = Depends(get_current_user_claims),
):
    """Retrieve tickets with role-based isolation (regular users see own + FAQ, officers see all)."""
    user_id = int(claims["sub"])
    params = {
        "category": category,
        "priority": priority,
        "status": status,
        "search": search,
        "is_faq": is_faq,
        "is_overdue": is_overdue,
        "sort_by": sort_by,
        "offset": offset,
        "limit": limit,
    }
    result = await odoo_client.call_json("/api/v1/tickets/list", params=params, user_id=user_id)
    return TicketListResponseDTO(
        status="success",
        total=result.get("total", 0),
        data=result.get("data", [])
    )

@router.post("", response_model=TicketResponseDTO, status_code=status.HTTP_201_CREATED)
async def create_ticket(
    dto: TicketCreateDTO,
    claims: dict = Depends(get_current_user_claims),
):
    """Create a new ticket with automatic SLA calculation and authentic author binding."""
    user_id = int(claims["sub"])
    params = dto.model_dump()
    result = await odoo_client.call_json("/api/v1/tickets/create", params=params, user_id=user_id)
    return result.get("data", {})

@router.get("/stats", response_model=TicketStatsResponseDTO)
async def get_ticket_stats(
    claims: dict = Depends(get_current_user_claims),
):
    """Retrieve ticket metrics (total, waiting, in_progress, resolved, overdue)."""
    user_id = int(claims["sub"])
    result = await odoo_client.call_json("/api/v1/tickets/stats", params={}, user_id=user_id)
    return TicketStatsResponseDTO(
        status="success",
        data=result.get("data", {})
    )

@router.get("/{ticket_id}", response_model=TicketDetailResponseDTO)
async def get_ticket(
    ticket_id: int,
    claims: dict = Depends(get_current_user_claims),
):
    """Retrieve full details of a single ticket."""
    user_id = int(claims["sub"])
    result = await odoo_client.call_json("/api/v1/tickets/detail", params={"ticket_id": ticket_id}, user_id=user_id)
    return result.get("data", {})

@router.post("/{ticket_id}/resolve")
async def resolve_ticket(
    ticket_id: int,
    dto: TicketResolveDTO,
    claims: dict = Depends(get_current_user_claims),
):
    """Resolve an IT ticket (Restricted to Helpdesk Officers, Optimistic Concurrency Protected)."""
    if not claims.get("is_officer", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only IT Helpdesk Officers are authorized to resolve tickets"
        )
    user_id = int(claims["sub"])
    params = {
        "ticket_id": ticket_id,
        "resolution_note": dto.resolution_note,
        "if_match_write_date": dto.if_match_write_date,
    }
    result = await odoo_client.call_json("/api/v1/tickets/resolve", params=params, user_id=user_id)
    return result

@router.post("/{ticket_id}/rate")
async def rate_ticket(
    ticket_id: int,
    dto: TicketRateDTO,
    claims: dict = Depends(get_current_user_claims),
):
    """Rate a resolved IT ticket and close it (Restricted to ticket author)."""
    user_id = int(claims["sub"])
    params = {
        "ticket_id": ticket_id,
        "rating": dto.rating,
        "rating_comment": dto.rating_comment,
        "if_match_write_date": dto.if_match_write_date,
    }
    result = await odoo_client.call_json("/api/v1/tickets/rate", params=params, user_id=user_id)
    return result

@router.post("/{ticket_id}/toggle-faq")
async def toggle_faq(
    ticket_id: int,
    claims: dict = Depends(get_current_user_claims),
):
    """Toggle FAQ recommendation status (Restricted to IT Helpdesk Officers)."""
    if not claims.get("is_officer", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only IT Helpdesk Officers are authorized to manage FAQ tickets"
        )
    user_id = int(claims["sub"])
    params = {"ticket_id": ticket_id}
    result = await odoo_client.call_json("/api/v1/tickets/toggle-faq", params=params, user_id=user_id)
    return result

@router.post("/{ticket_id}/restart")
async def restart_ticket(
    ticket_id: int,
    dto: TicketRestartDTO,
    claims: dict = Depends(get_current_user_claims),
):
    """Employee follow-up inquiry (Restarts ticket to in_progress)."""
    user_id = int(claims["sub"])
    params = {
        "ticket_id": ticket_id,
        "reason": dto.reason,
    }
    result = await odoo_client.call_json("/api/v1/tickets/restart", params=params, user_id=user_id)
    return result

@router.post("/{ticket_id}/update-resolution")
async def update_resolution(
    ticket_id: int,
    dto: TicketUpdateResolutionDTO,
    claims: dict = Depends(get_current_user_claims),
):
    """Update resolution note (Restricted to IT Helpdesk Officers, Optimistic Concurrency Protected)."""
    if not claims.get("is_officer", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only IT Helpdesk Officers are authorized to update resolution notes"
        )
    user_id = int(claims["sub"])
    params = {
        "ticket_id": ticket_id,
        "resolution_note": dto.resolution_note,
        "if_match_write_date": dto.if_match_write_date,
    }
    result = await odoo_client.call_json("/api/v1/tickets/update-resolution", params=params, user_id=user_id)
    return result

@router.post("/{ticket_id}/assign")
async def assign_ticket(
    ticket_id: int,
    claims: dict = Depends(get_current_user_claims),
):
    """Assign ticket to current IT Helpdesk Officer."""
    if not claims.get("is_officer", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only IT Helpdesk Officers are authorized to assign tickets"
        )
    user_id = int(claims["sub"])
    result = await odoo_client.call_json("/api/v1/tickets/assign", params={"ticket_id": ticket_id}, user_id=user_id)
    return result

@router.post("/{ticket_id}/start-progress")
async def start_progress_ticket(
    ticket_id: int,
    claims: dict = Depends(get_current_user_claims),
):
    """Transition ticket status to in_progress (Restricted to IT Helpdesk Officers)."""
    if not claims.get("is_officer", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only IT Helpdesk Officers are authorized to update ticket status"
        )
    user_id = int(claims["sub"])
    result = await odoo_client.call_json("/api/v1/tickets/start-progress", params={"ticket_id": ticket_id}, user_id=user_id)
    return result

@router.post("/{ticket_id}/pending")
async def pending_ticket(
    ticket_id: int,
    claims: dict = Depends(get_current_user_claims),
):
    """Transition ticket status to pending (Restricted to IT Helpdesk Officers)."""
    if not claims.get("is_officer", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only IT Helpdesk Officers are authorized to set ticket to pending"
        )
    user_id = int(claims["sub"])
    result = await odoo_client.call_json("/api/v1/tickets/pending", params={"ticket_id": ticket_id}, user_id=user_id)
    return result

@router.post("/{ticket_id}/close")
async def close_ticket(
    ticket_id: int,
    dto: TicketCloseDTO,
    claims: dict = Depends(get_current_user_claims),
):
    """Close ticket authoritatively (Restricted to IT Helpdesk Officers)."""
    if not claims.get("is_officer", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only IT Helpdesk Officers are authorized to close tickets"
        )
    user_id = int(claims["sub"])
    params = {"ticket_id": ticket_id, "note": dto.note}
    result = await odoo_client.call_json("/api/v1/tickets/close", params=params, user_id=user_id)
    return result

@router.post("/{ticket_id}/cancel")
async def cancel_ticket(
    ticket_id: int,
    dto: TicketCancelDTO,
    claims: dict = Depends(get_current_user_claims),
):
    """Cancel ticket (Author or IT Helpdesk Officers)."""
    user_id = int(claims["sub"])
    params = {"ticket_id": ticket_id, "reason": dto.reason}
    result = await odoo_client.call_json("/api/v1/tickets/cancel", params=params, user_id=user_id)
    return result

@router.post("/{ticket_id}/update", response_model=TicketResponseDTO)
async def update_ticket(
    ticket_id: int,
    dto: TicketUpdateDTO,
    claims: dict = Depends(get_current_user_claims),
):
    """Update ticket content when in submitted (waiting) status (Author or IT Officers)."""
    user_id = int(claims["sub"])
    params = {"ticket_id": ticket_id, **dto.model_dump(exclude_unset=True)}
    result = await odoo_client.call_json("/api/v1/tickets/update", params=params, user_id=user_id)
    return result.get("data", {})

@router.post("/{ticket_id}/attachments", response_model=AttachmentDTO, status_code=status.HTTP_201_CREATED)
async def upload_attachment(
    ticket_id: int,
    dto: AttachmentUploadDTO,
    claims: dict = Depends(get_current_user_claims),
):
    """Upload Base64 attachment to ticket (Author or IT Officers)."""
    user_id = int(claims["sub"])
    params = {
        "ticket_id": ticket_id,
        "name": dto.name,
        "datas": dto.datas,
        "mimetype": dto.mimetype,
    }
    result = await odoo_client.call_json("/api/v1/tickets/upload-attachment", params=params, user_id=user_id)
    return result.get("data", {})

@router.get("/{ticket_id}/attachments/{attachment_id}", response_model=AttachmentDetailDTO)
async def get_attachment(
    ticket_id: int,
    attachment_id: int,
    claims: dict = Depends(get_current_user_claims),
):
    """Retrieve single attachment with Base64 data (Author or IT Officers)."""
    user_id = int(claims["sub"])
    params = {"ticket_id": ticket_id, "attachment_id": attachment_id}
    result = await odoo_client.call_json("/api/v1/tickets/get-attachment", params=params, user_id=user_id)
    return result.get("data", {})
