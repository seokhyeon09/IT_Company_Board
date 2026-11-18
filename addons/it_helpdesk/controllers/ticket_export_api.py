# -*- coding: utf-8 -*-
"""티켓 목록 CSV 내보내기용 데이터 조회 API (담당자/관리자 전용)."""
from odoo import http

from ..utils import (
    _format_datetime_utc,
    verify_gateway_request,
    get_current_request,
    ensure_officer,
    ALLOWED_SORTS,
    build_ticket_domain,
)
from .ticket_query_api import LIST_FIELDS

EXPORT_FIELDS = LIST_FIELDS + ['first_resolved_date']
MAX_EXPORT_LIMIT = 5000


class TicketExportAPIController(http.Controller):
    """Ticket Export Data API for Gateway CSV Generation"""

    @http.route('/api/v1/tickets/export', type='json', auth='none', methods=['POST'], csrf=False)
    def export_tickets(
        self,
        category=None,
        priority=None,
        status=None,
        search=None,
        is_faq=None,
        is_overdue=None,
        assigned_to_me=None,
        sort_by=None,
        limit=MAX_EXPORT_LIMIT,
        **kwargs,
    ):
        req_env = get_current_request().env
        user = verify_gateway_request()
        ensure_officer(user)

        ticket_env = req_env['it.helpdesk.ticket'].with_user(user)
        domain = build_ticket_domain(
            user, category, priority, status, search, is_faq, is_overdue, assigned_to_me
        )
        order_clause = ALLOWED_SORTS.get(sort_by, 'id desc') if sort_by else 'id desc'
        safe_limit = min(max(1, int(limit or MAX_EXPORT_LIMIT)), MAX_EXPORT_LIMIT)

        tickets = ticket_env.search_read(
            domain,
            EXPORT_FIELDS,
            limit=safe_limit,
            order=order_clause,
        )
        for t in tickets:
            t['deadline'] = _format_datetime_utc(t.get('deadline'))
            t['create_date'] = _format_datetime_utc(t.get('create_date'))
            t['write_date'] = _format_datetime_utc(t.get('write_date'))
            t['first_resolved_date'] = _format_datetime_utc(t.get('first_resolved_date'))

        total_count = ticket_env.search_count(domain)
        return {"status": "success", "data": tickets, "total": total_count}
