# -*- coding: utf-8 -*-
from typing import Optional
from fastapi import APIRouter, Depends, Query, Response

from app.core.security import get_current_officer_claims
from app.services.export_service import export_service
from app.utils.csv_export import kst_today_yyyymmdd

router = APIRouter()


@router.get("/export")
async def export_tickets_csv(
    category: Optional[str] = Query(None, description="분류 (hw, sw, network, account, etc)"),
    priority: Optional[str] = Query(None, description="긴급도 (0, 1, 2, 3)"),
    status: Optional[str] = Query(None, description="상태"),
    search: Optional[str] = Query(None, description="검색어"),
    is_faq: Optional[bool] = Query(None, description="FAQ 여부"),
    is_overdue: Optional[bool] = Query(None, description="기한 초과 여부"),
    assigned_to_me: Optional[bool] = Query(None, description="내 담당 문의만 보기"),
    sort_by: Optional[str] = Query("id desc", description="정렬 옵션"),
    claims: dict = Depends(get_current_officer_claims),
):
    """현재 필터 조건의 티켓 목록을 CSV로 내보낸다 (담당자/관리자 전용)."""
    csv_bytes, truncated = await export_service.export_tickets_csv(
        user_id=int(claims["sub"]),
        category=category,
        priority=priority,
        status=status,
        search=search,
        is_faq=is_faq,
        is_overdue=is_overdue,
        assigned_to_me=assigned_to_me,
        sort_by=sort_by,
    )
    filename = f"tickets_{kst_today_yyyymmdd()}.csv"
    headers = {
        "Content-Disposition": f'attachment; filename="{filename}"',
    }
    if truncated:
        headers["X-Export-Truncated"] = "true"
    return Response(
        content=csv_bytes,
        media_type="text/csv; charset=utf-8",
        headers=headers,
    )
