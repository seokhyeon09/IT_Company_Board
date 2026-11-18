# -*- coding: utf-8 -*-
"""티켓 일괄 처리 API (담당자/관리자 전용)."""
from odoo import http
from odoo.exceptions import AccessError, UserError

from ..utils import (
    verify_gateway_request,
    get_current_request,
    ensure_officer,
    do_assign,
    do_start_progress,
    do_close,
)
from ..utils.auto_assign import pick_officer

VALID_BULK_ACTIONS = ('assign', 'assign_auto', 'start_progress', 'close')
MAX_BULK_TICKETS = 50


def _normalize_ticket_ids(ticket_ids):
    if not isinstance(ticket_ids, list) or not ticket_ids:
        raise UserError("선택된 문의가 없습니다.")
    unique_ids = []
    seen = set()
    for raw_id in ticket_ids:
        if isinstance(raw_id, bool) or not isinstance(raw_id, int) or raw_id <= 0:
            raise UserError("선택된 문의 ID가 올바르지 않습니다.")
        if raw_id not in seen:
            seen.add(raw_id)
            unique_ids.append(raw_id)
    if len(unique_ids) > MAX_BULK_TICKETS:
        raise UserError("한 번에 최대 50건까지 처리할 수 있습니다.")
    return unique_ids


class TicketBulkAPIController(http.Controller):
    """Bulk Ticket Workflow Actions API"""

    @http.route('/api/v1/tickets/bulk', type='json', auth='none', methods=['POST'], csrf=False)
    def bulk_action(self, ticket_ids=None, action=None, officer_id=None, reason=None, note=None, **kwargs):
        """선택한 여러 티켓에 대해 일괄 배정, 처리 시작, 직권 종결을 수행한다."""
        user = verify_gateway_request()
        ensure_officer(user)

        if action not in VALID_BULK_ACTIONS:
            raise UserError("지원하지 않는 일괄 작업입니다.")

        unique_ids = _normalize_ticket_ids(ticket_ids)
        req_env = get_current_request().env

        target_user = None
        if action == 'assign':
            if not officer_id or isinstance(officer_id, bool):
                raise UserError("지정한 담당자를 찾을 수 없습니다.")
            target_user = req_env['res.users'].browse(int(officer_id))
            if not target_user.exists():
                raise UserError("지정한 담당자를 찾을 수 없습니다.")

        ticket_env = req_env['it.helpdesk.ticket'].with_user(user)
        results = []

        for tid in unique_ids:
            ticket = ticket_env.browse(tid)
            if not ticket.exists():
                results.append({
                    "id": tid,
                    "ticket_number": None,
                    "ok": False,
                    "message": "문의를 찾을 수 없습니다.",
                })
                continue

            ticket_number = ticket.ticket_number
            try:
                with req_env.cr.savepoint():
                    res_msg = self._apply_single(
                        ticket, user, req_env, action, target_user, reason, note
                    )
                results.append({
                    "id": tid,
                    "ticket_number": ticket_number,
                    "ok": True,
                    "message": res_msg,
                })
            except (UserError, AccessError) as exc:
                ticket.invalidate_recordset()
                results.append({
                    "id": tid,
                    "ticket_number": ticket_number,
                    "ok": False,
                    "message": str(exc),
                })

        success_count = sum(1 for r in results if r["ok"])
        return {
            "status": "success",
            "data": {
                "action": action,
                "total": len(results),
                "success_count": success_count,
                "fail_count": len(results) - success_count,
                "results": results,
            },
        }

    def _apply_single(self, ticket, user, req_env, action, target_user, reason, note):
        if action == 'assign':
            if (
                ticket.assignee_id
                and ticket.assignee_id.id == target_user.id
                and ticket.status not in ('resolved', 'closed', 'canceled')
            ):
                return "이미 해당 담당자에게 배정되어 있습니다."
            do_assign(ticket, user, target_user, reason=reason)
            return "처리되었습니다."

        if action == 'assign_auto':
            picked = pick_officer(req_env, ticket.category)
            if not picked:
                raise UserError("자동으로 배정할 수 있는 담당자가 없습니다.")
            if (
                ticket.assignee_id
                and ticket.assignee_id.id == picked.id
                and ticket.status not in ('resolved', 'closed', 'canceled')
            ):
                return "이미 해당 담당자에게 배정되어 있습니다."
            do_assign(ticket, user, picked, reason=reason)
            return "처리되었습니다."

        if action == 'start_progress':
            do_start_progress(ticket, user)
            return "처리되었습니다."

        do_close(ticket, user, note=note)
        return "처리되었습니다."
