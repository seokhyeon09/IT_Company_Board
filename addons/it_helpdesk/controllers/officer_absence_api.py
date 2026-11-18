# -*- coding: utf-8 -*-
"""담당자 본인 부재 설정 조회/변경 API (담당자/관리자 전용)."""
from datetime import date
from odoo import http, fields
from odoo.exceptions import UserError

from ..utils import verify_gateway_request, ensure_officer, get_current_request

OPEN_TICKET_STATUSES = ('assigned', 'in_progress', 'pending')
OPEN_TICKET_LIMIT = 100


def _serialize_absence(user):
    effective = user._helpdesk_is_absent()
    until = (
        fields.Date.to_string(user.helpdesk_absent_until)
        if effective and user.helpdesk_absent_until
        else None
    )
    return {"is_absent": effective, "absent_until": until}


def _fetch_open_tickets(user):
    ticket_env = get_current_request().env['it.helpdesk.ticket'].with_user(user)
    domain = [
        ('assignee_id', '=', user.id),
        ('status', 'in', OPEN_TICKET_STATUSES),
    ]
    total = ticket_env.search_count(domain)
    records = ticket_env.search_read(
        domain,
        ['id', 'ticket_number', 'title', 'status', 'priority', 'category'],
        order='id desc',
        limit=OPEN_TICKET_LIMIT,
    )
    items = [
        {
            "id": rec["id"],
            "ticket_number": rec["ticket_number"],
            "title": rec["title"],
            "status": rec["status"],
            "priority": rec["priority"],
            "category": rec["category"],
        }
        for rec in records
    ]
    return items, total


class OfficerAbsenceAPIController(http.Controller):
    """Officer Absence Self-Management API"""

    @http.route('/api/v1/officers/me/absence/get', type='json', auth='none', methods=['POST'], csrf=False)
    def get_my_absence(self, **kwargs):
        user = verify_gateway_request()
        ensure_officer(user)
        return {
            "status": "success",
            "data": _serialize_absence(user),
            "open_tickets": [],
            "open_ticket_total": 0,
        }

    @http.route('/api/v1/officers/me/absence/set', type='json', auth='none', methods=['POST'], csrf=False)
    def set_my_absence(self, is_absent=False, absent_until=None, **kwargs):
        user = verify_gateway_request()
        ensure_officer(user)

        absent_flag = bool(is_absent)
        if not absent_flag:
            user.sudo().write({
                "helpdesk_absent": False,
                "helpdesk_absent_until": False,
            })
            return {
                "status": "success",
                "data": _serialize_absence(user),
                "open_tickets": [],
                "open_ticket_total": 0,
            }

        until_val = False
        if absent_until not in (None, False, ""):
            try:
                parsed = date.fromisoformat(str(absent_until).strip())
            except ValueError as exc:
                raise UserError("부재 종료일 형식이 올바르지 않습니다. (YYYY-MM-DD)") from exc
            if parsed < fields.Date.today():
                raise UserError("부재 종료일은 오늘 이후 날짜여야 합니다.")
            until_val = parsed

        user.sudo().write({
            "helpdesk_absent": True,
            "helpdesk_absent_until": until_val,
        })
        absence_data = _serialize_absence(user)
        if absence_data["is_absent"]:
            open_tickets, open_ticket_total = _fetch_open_tickets(user)
        else:
            open_tickets, open_ticket_total = [], 0
        return {
            "status": "success",
            "data": absence_data,
            "open_tickets": open_tickets,
            "open_ticket_total": open_ticket_total,
        }
