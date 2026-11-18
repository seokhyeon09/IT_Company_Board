# -*- coding: utf-8 -*-
"""담당자 본인 부재 설정 조회/변경 API (담당자/관리자 전용)."""
from datetime import date
from odoo import http, fields
from odoo.exceptions import UserError

from ..utils import verify_gateway_request, ensure_officer


def _serialize_absence(user):
    effective = user._helpdesk_is_absent()
    until = (
        fields.Date.to_string(user.helpdesk_absent_until)
        if effective and user.helpdesk_absent_until
        else None
    )
    return {"is_absent": effective, "absent_until": until}


class OfficerAbsenceAPIController(http.Controller):
    """Officer Absence Self-Management API"""

    @http.route('/api/v1/officers/me/absence/get', type='json', auth='none', methods=['POST'], csrf=False)
    def get_my_absence(self, **kwargs):
        user = verify_gateway_request()
        ensure_officer(user)
        return {"status": "success", "data": _serialize_absence(user)}

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
            return {"status": "success", "data": _serialize_absence(user)}

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
        return {"status": "success", "data": _serialize_absence(user)}
