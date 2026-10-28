# -*- coding: utf-8 -*-
import html
import re
from datetime import datetime, timezone
from typing import Optional
from odoo.exceptions import UserError

def parse_iso_utc(dt_str: str) -> Optional[datetime]:
    """Parse ISO-8601 string into a naive UTC datetime matching Odoo ORM storage."""
    if not dt_str:
        return None
    clean_str = dt_str.strip().replace("Z", "+00:00")
    try:
        dt = datetime.fromisoformat(clean_str)
        if dt.tzinfo is not None:
            dt = dt.astimezone(timezone.utc).replace(tzinfo=None)
        return dt
    except (ValueError, TypeError) as exc:
        raise UserError(f"Invalid datetime format: '{dt_str}'. Expected ISO-8601 UTC format.") from exc

def _safe_html_text(text: Optional[str]) -> str:
    """Escape HTML special characters to prevent Stored XSS while converting line breaks to <br/>."""
    if not text:
        return ""
    escaped = html.escape(str(text).strip())
    return escaped.replace("\r\n", "<br/>").replace("\n", "<br/>")

def _clean_html(raw: Optional[str]) -> str:
    """Strip HTML tags and convert line breaks for clean plain text display."""
    if not raw:
        return ""
    # 1. Unescape HTML entities so tags become real <...>
    text = html.unescape(raw)
    # 2. Convert line breaks
    text = re.sub(r'<br\s*/?>', '\n', text, flags=re.IGNORECASE)
    text = re.sub(r'</p>', '\n', text, flags=re.IGNORECASE)
    # 3. Strip all HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    # 4. Strip residual prefixes and clean whitespace
    text = re.sub(r'^(?:\[(?:추가 재문의|조치 답변|조치 답변 \(수정\)|답변 대기 요청|직권 종결|문의 취소)\]\s*)+', '', text.strip())
    text = text.replace('\xa0', ' ').replace('&nbsp;', ' ')
    return text.strip()

def _extract_thread_content(raw_html: str, markers: list) -> str:
    """Extract clean body text from message tags without html artifacts."""
    if not raw_html:
        return ""
    text = html.unescape(raw_html)
    for m in markers:
        m_un = html.unescape(m)
        if m_un in text:
            parts = text.split(m_un, 1)
            if len(parts) > 1 and parts[1].strip():
                text = parts[1]
    return _clean_html(text)

def _format_datetime_utc(dt_val) -> Optional[str]:
    """Format an Odoo Datetime value to an unambiguous ISO-8601 UTC string ending in 'Z'."""
    if not dt_val:
        return None
    if isinstance(dt_val, str):
        return dt_val.replace(" ", "T") + "Z"
    if hasattr(dt_val, "strftime"):
        return dt_val.strftime("%Y-%m-%dT%H:%M:%SZ")
    return str(dt_val)
