# -*- coding: utf-8 -*-
from fastapi import APIRouter, Depends, HTTPException, Query, status
from app.core.security import get_current_user_claims
from app.services.insight_service import insight_service
from app.schemas.insight import (
    TicketStatsResponseDTO,
    OfficerStatsResponseDTO,
    OfficerListResponseDTO,
    EmailNotificationListResponseDTO,
    NotificationReadDTO,
    NotificationReadResponseDTO,
)

router = APIRouter()

@router.get("/stats", response_model=TicketStatsResponseDTO)
async def get_ticket_stats(
    claims: dict = Depends(get_current_user_claims),
):
    """Retrieve ticket metrics (total, waiting, in_progress, resolved, overdue)."""
    return await insight_service.get_stats(user_id=int(claims["sub"]))

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
    return await insight_service.get_officer_stats(user_id=int(claims["sub"]))

@router.get("/notifications", response_model=EmailNotificationListResponseDTO)
async def get_mock_notifications(
    limit: int = Query(30, ge=1, le=50),
    claims: dict = Depends(get_current_user_claims),
):
    """Retrieve mock email dispatch logs for the current user."""
    return await insight_service.get_notifications(user_id=int(claims["sub"]), limit=limit)

@router.post("/notifications/read", response_model=NotificationReadResponseDTO)
async def mark_notifications_read(
    dto: NotificationReadDTO,
    claims: dict = Depends(get_current_user_claims),
):
    """Mark email notifications as read (persisted to backend database)."""
    return await insight_service.mark_notifications_read(user_id=int(claims["sub"]), dto=dto)

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
    return await insight_service.get_officers(user_id=int(claims["sub"]))
