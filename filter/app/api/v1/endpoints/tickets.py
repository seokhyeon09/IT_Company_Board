# -*- coding: utf-8 -*-
from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status
from app.core.security import get_current_user_claims
from app.client.odoo_client import odoo_client
from app.schemas.ticket import (
    TicketCreateDTO,
    TicketResolveDTO,
    TicketResponseDTO,
    TicketDetailResponseDTO,
    TicketListResponseDTO
)

router = APIRouter()

@router.get("", response_model=TicketListResponseDTO)
async def list_tickets(
    category: Optional[str] = Query(None, description="분류 (hw, sw, network, account, etc)"),
    priority: Optional[str] = Query(None, description="긴급도 (0, 1, 2, 3)"),
    status: Optional[str] = Query(None, description="상태"),
    search: Optional[str] = Query(None, description="검색어"),
    is_faq: Optional[bool] = Query(None, description="FAQ 여부"),
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
