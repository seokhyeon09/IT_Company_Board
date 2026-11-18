# -*- coding: utf-8 -*-
from typing import Optional
from urllib.parse import quote
from fastapi import APIRouter, Depends, Query, Response

from app.core.security import get_current_user_claims, require_officer
from app.schemas.report import SlaReportResponseDTO
from app.services.report_service import report_service
from app.utils.csv_export import kst_today_yyyymmdd

router = APIRouter()


@router.get("/sla", response_model=SlaReportResponseDTO)
async def get_sla_report(
    date_from: Optional[str] = Query(None, description="조회 시작일 (YYYY-MM-DD, KST)"),
    date_to: Optional[str] = Query(None, description="조회 종료일 (YYYY-MM-DD, KST)"),
    unit: Optional[str] = Query(None, description="집계 단위 (week 또는 month)"),
    category: Optional[str] = Query(None, description="분야 (hw, sw, network, account, etc)"),
    claims: dict = Depends(get_current_user_claims),
):
    """기간별 SLA 리포트를 조회한다 (담당자/관리자 전용)."""
    user_id = require_officer(claims)
    return await report_service.get_sla_report(
        user_id=user_id,
        date_from=date_from,
        date_to=date_to,
        unit=unit,
        category=category,
    )


@router.get("/sla/export")
async def export_sla_report_csv(
    date_from: Optional[str] = Query(None, description="조회 시작일 (YYYY-MM-DD, KST)"),
    date_to: Optional[str] = Query(None, description="조회 종료일 (YYYY-MM-DD, KST)"),
    unit: Optional[str] = Query(None, description="집계 단위 (week 또는 month)"),
    category: Optional[str] = Query(None, description="분야 (hw, sw, network, account, etc)"),
    claims: dict = Depends(get_current_user_claims),
):
    """기간별 SLA 리포트를 CSV로 내보낸다 (담당자/관리자 전용)."""
    user_id = require_officer(claims)
    csv_bytes = await report_service.export_sla_report_csv(
        user_id=user_id,
        date_from=date_from,
        date_to=date_to,
        unit=unit,
        category=category,
    )
    filename = f"sla-report_{kst_today_yyyymmdd()}.csv"
    encoded = quote(filename)
    headers = {
        "Content-Disposition": f"attachment; filename=\"{filename}\"; filename*=UTF-8''{encoded}",
    }
    return Response(
        content=csv_bytes,
        media_type="text/csv; charset=utf-8",
        headers=headers,
    )
