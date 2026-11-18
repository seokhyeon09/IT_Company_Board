# -*- coding: utf-8 -*-
"""티켓 목록 CSV 직렬화, KST 변환 및 수식 주입 방어 순수 유틸."""
from __future__ import annotations

import csv
import io
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from app.core.labels import CATEGORY_LABELS, PRIORITY_LABELS, STATUS_LABELS

KST = timezone(timedelta(hours=9))
FORMULA_PREFIXES = ("=", "+", "-", "@", "\t", "\r")

CSV_HEADERS = [
    "티켓번호",
    "제목",
    "분류",
    "상태",
    "긴급도",
    "작성자",
    "담당자",
    "접수일시",
    "SLA기한",
    "기한초과",
    "최초해결일시",
    "해결소요시간(시간)",
    "만족도",
    "FAQ",
]


def sanitize_csv_cell(value: Any) -> str:
    """엑셀 수식 주입(=, +, -, @, 탭, CR 시작)을 방어하기 위해 앞에 작은따옴표를 붙인다."""
    text = "" if value is None else str(value)
    if text and text[0] in FORMULA_PREFIXES:
        return f"'{text}"
    return text


def parse_utc_datetime(raw: Any) -> Optional[datetime]:
    """ISO-8601 또는 Odoo 일시 문자열을 UTC aware datetime으로 파싱한다."""
    if raw in (None, False, ""):
        return None
    if isinstance(raw, datetime):
        return raw.replace(tzinfo=timezone.utc) if raw.tzinfo is None else raw.astimezone(timezone.utc)
    if not isinstance(raw, str):
        return None
    cleaned = raw.strip()
    if not cleaned:
        return None
    if cleaned.endswith("Z"):
        cleaned = f"{cleaned[:-1]}+00:00"
    try:
        dt = datetime.fromisoformat(cleaned)
    except ValueError:
        return None
    return dt.replace(tzinfo=timezone.utc) if dt.tzinfo is None else dt.astimezone(timezone.utc)


def format_kst_datetime(raw: Any) -> str:
    """UTC 일시를 한국 표준시(UTC+9) 'YYYY-MM-DD HH:MM' 문자열로 변환한다."""
    dt = parse_utc_datetime(raw)
    if dt is None:
        return ""
    return dt.astimezone(KST).strftime("%Y-%m-%d %H:%M")


def compute_resolution_hours_str(create_raw: Any, first_resolved_raw: Any) -> str:
    """접수일시와 최초해결일시 차이(시간, 소수 1자리)를 문자열로 반환한다."""
    created = parse_utc_datetime(create_raw)
    resolved = parse_utc_datetime(first_resolved_raw)
    if created is None or resolved is None:
        return ""
    hours = max(0.0, (resolved - created).total_seconds() / 3600.0)
    return f"{round(hours, 1):.1f}"


def kst_today_yyyymmdd(now_utc: Optional[datetime] = None) -> str:
    """한국 날짜 기준 YYYYMMDD 문자열을 반환한다."""
    dt = now_utc or datetime.now(timezone.utc)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(KST).strftime("%Y%m%d")


def _extract_relation_name(val: Any) -> str:
    if isinstance(val, (list, tuple)) and len(val) >= 2:
        return "" if val[1] in (None, False) else str(val[1])
    if isinstance(val, str):
        return val
    return ""


def _format_rating(val: Any) -> str:
    if val in (None, False, "", "0", 0):
        return ""
    return str(val)


def _format_ticket_row(ticket: Dict[str, Any]) -> List[str]:
    cat_raw = "" if ticket.get("category") in (None, False) else str(ticket.get("category"))
    status_raw = "" if ticket.get("status") in (None, False) else str(ticket.get("status"))
    prio_raw = "" if ticket.get("priority") in (None, False) else str(ticket.get("priority"))

    author = _extract_relation_name(ticket.get("author_id")) or (
        "" if ticket.get("author_name") in (None, False) else str(ticket.get("author_name"))
    )
    assignee = _extract_relation_name(ticket.get("assignee_id")) or (
        "" if ticket.get("assignee_name") in (None, False) else str(ticket.get("assignee_name"))
    )

    cells = [
        "" if ticket.get("ticket_number") in (None, False) else str(ticket.get("ticket_number")),
        "" if ticket.get("title") in (None, False) else str(ticket.get("title")),
        CATEGORY_LABELS.get(cat_raw, cat_raw),
        STATUS_LABELS.get(status_raw, status_raw),
        PRIORITY_LABELS.get(prio_raw, prio_raw),
        author,
        assignee,
        format_kst_datetime(ticket.get("create_date")),
        format_kst_datetime(ticket.get("deadline")),
        "Y" if ticket.get("is_overdue") else "N",
        format_kst_datetime(ticket.get("first_resolved_date")),
        compute_resolution_hours_str(ticket.get("create_date"), ticket.get("first_resolved_date")),
        _format_rating(ticket.get("rating")),
        "Y" if ticket.get("is_faq") else "N",
    ]
    return [sanitize_csv_cell(cell) for cell in cells]


def build_ticket_csv_bytes(tickets: List[Dict[str, Any]]) -> bytes:
    """티켓 목록을 UTF-8 BOM 및 CRLF(\\r\\n)가 적용된 CSV 바이트로 직렬화한다."""
    buf = io.StringIO(newline="")
    writer = csv.writer(buf, lineterminator="\r\n", quoting=csv.QUOTE_MINIMAL)
    writer.writerow(CSV_HEADERS)
    for ticket in tickets:
        writer.writerow(_format_ticket_row(ticket))
    return b"\xef\xbb\xbf" + buf.getvalue().encode("utf-8")
