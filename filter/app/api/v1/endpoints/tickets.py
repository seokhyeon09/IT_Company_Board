# -*- coding: utf-8 -*-
from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from app.core.security import get_current_user_claims
from app.services.ticket_service import ticket_service
from app.schemas.ticket import (
    TicketCreateDTO,
    TicketUpdateDTO,
    TicketResponseDTO,
    TicketDetailResponseDTO,
    TicketListResponseDTO,
)
from app.api.v1.endpoints.ticket_insights import router as insights_router
from app.api.v1.endpoints.ticket_attachments import router as attachments_router
from app.api.v1.endpoints.ticket_workflow import router as workflow_router

router = APIRouter()

# Mount Sub-Routers
# Notice: insights_router handles /stats, /officer-stats, /officers, /notifications
# It must be mounted before /{ticket_id} to prevent path conflict!
router.include_router(insights_router)
router.include_router(attachments_router)
router.include_router(workflow_router)

@router.get("", response_model=TicketListResponseDTO)
async def list_tickets(
    category: Optional[str] = Query(None, description="분류 (hw, sw, network, account, etc)"),
    priority: Optional[str] = Query(None, description="긴급도 (0, 1, 2, 3)"),
    status: Optional[str] = Query(None, description="상태"),
    search: Optional[str] = Query(None, description="검색어"),
    is_faq: Optional[bool] = Query(None, description="FAQ 여부"),
    is_overdue: Optional[bool] = Query(None, description="기한 초과 여부"),
    assigned_to_me: Optional[bool] = Query(None, description="내 담당 문의만 보기"),
    sort_by: Optional[str] = Query("id desc", description="정렬 옵션"),
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    claims: dict = Depends(get_current_user_claims),
):
    """Retrieve tickets with role-based isolation."""
    return await ticket_service.list_tickets(
        user_id=int(claims["sub"]),
        category=category,
        priority=priority,
        status=status,
        search=search,
        is_faq=is_faq,
        is_overdue=is_overdue,
        assigned_to_me=assigned_to_me,
        sort_by=sort_by,
        offset=offset,
        limit=limit,
    )

@router.post("", response_model=TicketResponseDTO, status_code=status.HTTP_201_CREATED)
async def create_ticket(
    dto: TicketCreateDTO,
    claims: dict = Depends(get_current_user_claims),
):
    """Create a new ticket with automatic SLA calculation."""
    return await ticket_service.create_ticket(dto, user_id=int(claims["sub"]))

@router.get("/{ticket_id}", response_model=TicketDetailResponseDTO)
async def get_ticket(
    ticket_id: int,
    claims: dict = Depends(get_current_user_claims),
):
    """Retrieve full details of a single ticket."""
    return await ticket_service.get_detail(ticket_id, user_id=int(claims["sub"]))

@router.post("/{ticket_id}/update", response_model=TicketResponseDTO)
async def update_ticket(
    ticket_id: int,
    dto: TicketUpdateDTO,
    claims: dict = Depends(get_current_user_claims),
):
    """Update a submitted ticket by author."""
    return await ticket_service.update_ticket(ticket_id, dto, user_id=int(claims["sub"]))
