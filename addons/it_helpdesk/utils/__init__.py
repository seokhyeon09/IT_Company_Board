# -*- coding: utf-8 -*-
from .text_utils import (
    parse_iso_utc,
    _safe_html_text,
    _clean_html,
    _extract_thread_content,
    _format_datetime_utc,
    is_html_empty,
    _is_html_empty,
)
from .request_context import (
    get_current_request,
    set_mock_request,
)
from .security import (
    GATEWAY_SHARED_SECRET,
    ConcurrencyError,
    verify_gateway_request,
)
from .validators import (
    check_optimistic_lock,
    ensure_officer,
    ensure_assignee_or_admin,
    ensure_author,
    ensure_author_or_officer,
)
from .ticket_serializer import (
    build_sequential_timeline,
    serialize_ticket_summary,
    serialize_ticket_detail,
)
from .related_tickets import find_related_tickets
from .mock_email import build_mock_emails
from .auto_assign import try_auto_assign, create_ticket_with_auto_assign
