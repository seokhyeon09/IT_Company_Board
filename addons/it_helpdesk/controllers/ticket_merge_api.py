# -*- coding: utf-8 -*-
"""중복 문의 병합 및 후보 추천 API (담당자/관리자 전용)."""
from odoo import http
from odoo.exceptions import UserError

from ..utils import (
    check_optimistic_lock,
    ensure_officer,
    find_merge_candidates,
    get_current_request,
    merge_tickets,
    verify_gateway_request,
)


def _parse_positive_id(raw_id, error_msg: str) -> int:
    if raw_id is None or isinstance(raw_id, bool):
        raise UserError(error_msg)
    try:
        val = int(raw_id)
    except (TypeError, ValueError) as exc:
        raise UserError(error_msg) from exc
    if val <= 0:
        raise UserError(error_msg)
    return val


class TicketMergeAPIController(http.Controller):
    """Duplicate Ticket Merge and Candidate Suggestion API"""

    @http.route('/api/v1/tickets/merge', type='json', auth='none', methods=['POST'], csrf=False)
    def merge_ticket(
        self,
        ticket_id=None,
        target_id=None,
        reason=None,
        if_match_write_date=None,
        **kwargs,
    ):
        """중복 문의를 대상 문의에 병합한다."""
        user = verify_gateway_request()
        ensure_officer(user)

        src_id = _parse_positive_id(ticket_id, "문의를 찾을 수 없습니다.")
        tgt_id = _parse_positive_id(target_id, "병합 대상 문의를 찾을 수 없습니다.")

        req_env = get_current_request().env
        ticket_env = req_env['it.helpdesk.ticket'].with_user(user)
        source = ticket_env.browse(src_id)
        if not source.exists():
            raise UserError("문의를 찾을 수 없습니다.")
        target = ticket_env.browse(tgt_id)
        if not target.exists():
            raise UserError("병합 대상 문의를 찾을 수 없습니다.")

        check_optimistic_lock(source, if_match_write_date)
        merge_tickets(user, source, target, reason=reason)

        return {
            "status": "success",
            "data": {
                "id": source.id,
                "ticket_number": source.ticket_number,
                "status": source.status,
                "merged_into_id": source.merged_into_id.id if source.merged_into_id else None,
                "merged_into_number": source.merged_into_id.ticket_number if source.merged_into_id else None,
            },
        }

    @http.route('/api/v1/tickets/merge-candidates', type='json', auth='none', methods=['POST'], csrf=False)
    def get_merge_candidates(self, ticket_id=None, limit=5, **kwargs):
        """유사 제목 기준 병합 후보 목록을 추천한다."""
        user = verify_gateway_request()
        ensure_officer(user)

        src_id = _parse_positive_id(ticket_id, "문의를 찾을 수 없습니다.")
        req_env = get_current_request().env
        ticket = req_env['it.helpdesk.ticket'].with_user(user).browse(src_id)
        if not ticket.exists():
            raise UserError("문의를 찾을 수 없습니다.")

        candidates = find_merge_candidates(user, ticket, limit=limit)
        return {
            "status": "success",
            "data": {
                "candidates": candidates,
            },
        }
