# -*- coding: utf-8 -*-
import csv
import io
import re
from datetime import date
from typing import Any, Dict, List, Optional, Tuple

from fastapi import HTTPException

from app.client.odoo_client import odoo_client
from app.core.labels import CATEGORY_LABELS
from app.core.messages import (
    MSG_REPORT_CATEGORY_INVALID,
    MSG_REPORT_DATE_INVALID,
    MSG_REPORT_DATE_ORDER,
    MSG_REPORT_RANGE_EXCEEDED,
    MSG_REPORT_UNIT_INVALID,
)
from app.schemas.report import SlaReportResponseDTO
from app.utils.csv_export import sanitize_csv_cell

_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
VALID_UNITS = ("week", "month")
MAX_RANGE_DAYS = 366

SERIES_HEADERS = [
    "기간 시작일",
    "접수",
    "해결",
    "기한 내 해결",
    "기한 초과 해결",
    "SLA 준수율(%)",
    "평균 해결시간(시간)",
]
CATEGORY_HEADERS = ["분야", "접수", "해결", "SLA 준수율(%)", "평균 해결시간(시간)"]
PRIORITY_HEADERS = ["긴급도", "접수", "해결", "SLA 준수율(%)", "평균 해결시간(시간)"]


def _parse_date_422(raw: str) -> date:
    if not _DATE_RE.match(raw):
        raise HTTPException(status_code=422, detail=MSG_REPORT_DATE_INVALID)
    try:
        return date.fromisoformat(raw)
    except ValueError as exc:
        raise HTTPException(
            status_code=422, detail=MSG_REPORT_DATE_INVALID
        ) from exc


def validate_report_params(
    date_from: Optional[str],
    date_to: Optional[str],
    unit: Optional[str],
    category: Optional[str],
) -> Tuple[Optional[str], Optional[str], Optional[str], Optional[str]]:
    d_from = _parse_date_422(date_from) if date_from is not None else None
    d_to = _parse_date_422(date_to) if date_to is not None else None

    if d_from is not None and d_to is not None:
        if d_from > d_to:
            raise HTTPException(status_code=422, detail=MSG_REPORT_DATE_ORDER)
        if (d_to - d_from).days + 1 > MAX_RANGE_DAYS:
            raise HTTPException(status_code=422, detail=MSG_REPORT_RANGE_EXCEEDED)

    if unit is not None and unit not in VALID_UNITS:
        raise HTTPException(status_code=422, detail=MSG_REPORT_UNIT_INVALID)

    cat_val = None if category in (None, "") else category
    if cat_val is not None and cat_val not in CATEGORY_LABELS:
        raise HTTPException(status_code=422, detail=MSG_REPORT_CATEGORY_INVALID)

    return date_from, date_to, unit, cat_val


def _csv_cell(val: Any) -> str:
    if val is None:
        return ""
    return sanitize_csv_cell(val)


def build_sla_report_csv_bytes(data: Dict[str, Any]) -> bytes:
    """기간별 SLA 리포트 데이터를 3개 섹션(시리즈/분야별/긴급도별) CSV 바이트로 직렬화한다."""
    buf = io.StringIO(newline="")
    writer = csv.writer(buf, lineterminator="\r\n", quoting=csv.QUOTE_MINIMAL)

    writer.writerow(SERIES_HEADERS)
    for row in data.get("series", []):
        writer.writerow([
            _csv_cell(row.get("period")),
            _csv_cell(row.get("created")),
            _csv_cell(row.get("resolved")),
            _csv_cell(row.get("on_time")),
            _csv_cell(row.get("breached")),
            _csv_cell(row.get("on_time_rate")),
            _csv_cell(row.get("avg_resolution_hours")),
        ])

    writer.writerow([])
    writer.writerow(CATEGORY_HEADERS)
    for row in data.get("by_category", []):
        writer.writerow([
            _csv_cell(row.get("label")),
            _csv_cell(row.get("created")),
            _csv_cell(row.get("resolved")),
            _csv_cell(row.get("on_time_rate")),
            _csv_cell(row.get("avg_resolution_hours")),
        ])

    writer.writerow([])
    writer.writerow(PRIORITY_HEADERS)
    for row in data.get("by_priority", []):
        writer.writerow([
            _csv_cell(row.get("label")),
            _csv_cell(row.get("created")),
            _csv_cell(row.get("resolved")),
            _csv_cell(row.get("on_time_rate")),
            _csv_cell(row.get("avg_resolution_hours")),
        ])

    return b"\xef\xbb\xbf" + buf.getvalue().encode("utf-8")


class ReportService:
    """기간별 SLA 리포트 조회 및 CSV 내보내기 서비스."""

    async def _fetch_raw_report(
        self,
        user_id: int,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        unit: Optional[str] = None,
        category: Optional[str] = None,
    ) -> Dict[str, Any]:
        v_from, v_to, v_unit, v_cat = validate_report_params(date_from, date_to, unit, category)
        params = {
            "date_from": v_from,
            "date_to": v_to,
            "unit": v_unit,
            "category": v_cat,
        }
        result = await odoo_client.call_json(
            "/api/v1/reports/sla",
            params=params,
            user_id=user_id,
            timeout=30.0,
        )
        return result.get("data", {})

    async def get_sla_report(
        self,
        user_id: int,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        unit: Optional[str] = None,
        category: Optional[str] = None,
    ) -> SlaReportResponseDTO:
        data = await self._fetch_raw_report(user_id, date_from, date_to, unit, category)
        return SlaReportResponseDTO(status="success", data=data)

    async def export_sla_report_csv(
        self,
        user_id: int,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        unit: Optional[str] = None,
        category: Optional[str] = None,
    ) -> bytes:
        data = await self._fetch_raw_report(user_id, date_from, date_to, unit, category)
        return build_sla_report_csv_bytes(data)


report_service = ReportService()
