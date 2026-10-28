# -*- coding: utf-8 -*-
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from app.core.security import get_current_user_claims
from app.services import ticket_service, workflow_service
from app.schemas.ticket import (
    TicketAssignDTO,
    TicketCreateDTO,
    TicketResolveDTO,
    TicketRestartDTO,
    TicketUpdateResolutionDTO,
    TicketCloseDTO,
    TicketCancelDTO,
    TicketPendingDTO,
    TicketUpdateDTO,
    AttachmentDTO,
    AttachmentDetailDTO,
    AttachmentUploadDTO,
    TicketRateDTO,
    TicketResponseDTO,
    TicketDetailResponseDTO,
    TicketListResponseDTO,
    TicketStatsResponseDTO,
    OfficerStatsResponseDTO,
    OfficerListResponseDTO,
    EmailNotificationListResponseDTO,
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

@router.get("/stats", response_model=TicketStatsResponseDTO)
async def get_ticket_stats(
    claims: dict = Depends(get_current_user_claims),
):
    """Retrieve ticket metrics (total, waiting, in_progress, resolved, overdue)."""
    return await ticket_service.get_stats(user_id=int(claims["sub"]))

@router.get("/officer-stats", response_model=OfficerStatsResponseDTO)
async def get_officer_stats(
    claims: dict = Depends(get_current_user_claims),
):
    """Retrieve officer performance and category breakdown statistics (Officer only)."""
    if not claims.get("is_officer", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Helpdesk officer role required to view officer statistics",
        )
    return await ticket_service.get_officer_stats(user_id=int(claims["sub"]))

@router.get("/notifications", response_model=EmailNotificationListResponseDTO)
async def get_mock_notifications(
    limit: int = Query(30, ge=1, le=50),
    claims: dict = Depends(get_current_user_claims),
):
    """Retrieve mock email dispatch logs for the current user."""
    return await ticket_service.get_notifications(user_id=int(claims["sub"]), limit=limit)

@router.get("/officers", response_model=OfficerListResponseDTO)
async def get_officers(
    claims: dict = Depends(get_current_user_claims),
):
    """Retrieve active IT officers list for ticket assignment."""
    if not claims.get("is_officer", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Helpdesk officer role required to view officers list",
        )
    return await ticket_service.get_officers(user_id=int(claims["sub"]))

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
    """Cancel ticket inquiry by author or officer."""
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

@router.post("/{ticket_id}/attachments", response_model=AttachmentDTO, status_code=status.HTTP_201_CREATED)
async def upload_attachment(
    ticket_id: int,
    dto: AttachmentUploadDTO,
    claims: dict = Depends(get_current_user_claims),
):
    """Upload Base64 attachment for a ticket."""
    return await ticket_service.upload_attachment(ticket_id, dto, user_id=int(claims["sub"]))

@router.get("/{ticket_id}/attachments/{attachment_id}", response_model=AttachmentDetailDTO)
async def get_attachment(
    ticket_id: int,
    attachment_id: int,
    claims: dict = Depends(get_current_user_claims),
):
    """Retrieve Base64 attachment data."""
    return await ticket_service.get_attachment(ticket_id, attachment_id, user_id=int(claims["sub"]))
