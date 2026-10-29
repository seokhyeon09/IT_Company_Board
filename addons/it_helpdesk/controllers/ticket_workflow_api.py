# -*- coding: utf-8 -*-
import html
import logging
from odoo import http
from odoo.exceptions import AccessError, UserError

from ..utils import (
    _format_datetime_utc,
    _safe_html_text,
    verify_gateway_request,
    get_current_request,
    check_optimistic_lock,
    ensure_officer,
    ensure_assignee_or_admin,
    ensure_author,
    ensure_author_or_officer,
)

_logger = logging.getLogger(__name__)


def _get_ticket(ticket_id: int, user):
    ticket = get_current_request().env['it.helpdesk.ticket'].with_user(user).browse(int(ticket_id))
    if not ticket.exists():
        raise UserError("Ticket not found.")
    return ticket


def _workflow_res(ticket, **kwargs):
    data = {
        "id": ticket.id,
        "ticket_number": ticket.ticket_number,
        "status": ticket.status,
        "write_date": _format_datetime_utc(ticket.write_date),
    }
    data.update(kwargs)
    return {"status": "success", "data": data}


class TicketWorkflowAPIController(http.Controller):
    """Ticket Workflow State Transitions, Actions, and Resolutions API"""

    @http.route('/api/v1/tickets/resolve', type='json', auth='none', methods=['POST'], csrf=False)
    def resolve_ticket(self, ticket_id: int, resolution_note: str, if_match_write_date: str = None):
        """티켓 조치 완료 (낙관적 동시성 제어 및 IT 담당자 권한 검증)"""
        user = verify_gateway_request()
        ensure_officer(user)
        ticket = _get_ticket(ticket_id, user)
        ensure_assignee_or_admin(ticket, user)
        check_optimistic_lock(ticket, if_match_write_date)

        safe_note = _safe_html_text(resolution_note)
        ticket.resolution_note = safe_note
        if ticket.status == 'submitted':
            ticket.action_assign_to_me()
            ticket.action_start_progress()
        elif ticket.status == 'assigned':
            ticket.action_start_progress()
        ticket.action_resolve()
        ticket.message_post(body=f'<div data-msg-type="resolution"><b>[조치 답변]</b><br/>{safe_note}</div>')
        return _workflow_res(ticket)

    @http.route('/api/v1/tickets/rate', type='json', auth='none', methods=['POST'], csrf=False)
    def rate_ticket(self, ticket_id: int, rating: str, rating_comment: str = None, if_match_write_date: str = None):
        """요청 직원의 티켓 만족도 평가 및 자동 종결 처리"""
        user = verify_gateway_request()
        ticket = _get_ticket(ticket_id, user)
        ensure_author(ticket, user)
        check_optimistic_lock(ticket, if_match_write_date)

        ticket.rating = str(rating)
        ticket.rating_comment = (rating_comment or "").strip()
        ticket.action_submit_rating()
        return _workflow_res(ticket, rating=ticket.rating, rating_comment=ticket.rating_comment)

    @http.route('/api/v1/tickets/restart', type='json', auth='none', methods=['POST'], csrf=False)
    def restart_ticket(self, ticket_id: int, reason: str = None):
        """해결완료 후 추가 문의 또는 답변대기 회신"""
        user = verify_gateway_request()
        ticket = _get_ticket(ticket_id, user)
        ensure_author_or_officer(ticket, user)

        safe_reason = _safe_html_text(reason) if reason else ""
        was_pending = ticket.status == 'pending'
        ticket.action_restart_ticket()

        if safe_reason:
            msg_type = "pending_response" if was_pending else "inquiry"
            tag = "[답변 대기 회신]" if was_pending else "[추가 재문의]"
            ticket.message_post(body=f'<div data-msg-type="{msg_type}"><b>{tag}</b><br/>{safe_reason}</div>')
        return _workflow_res(ticket)

    @http.route('/api/v1/tickets/update-resolution', type='json', auth='none', methods=['POST'], csrf=False)
    def update_resolution(self, ticket_id: int, resolution_note: str, if_match_write_date: str = None):
        """최신 조치 내용 수정"""
        user = verify_gateway_request()
        ensure_officer(user)
        ticket = _get_ticket(ticket_id, user)
        ensure_assignee_or_admin(ticket, user)
        check_optimistic_lock(ticket, if_match_write_date)

        safe_note = _safe_html_text(resolution_note)
        ticket.resolution_note = safe_note
        ticket.message_post(body=f'<div data-msg-type="resolution"><b>[조치 답변 (수정)]</b><br/>{safe_note}</div>')
        return _workflow_res(ticket, resolution_note=ticket.resolution_note)

    @http.route('/api/v1/tickets/assign', type='json', auth='none', methods=['POST'], csrf=False)
    def assign_ticket(self, ticket_id: int, assignee_id: int = None, reason: str = None):
        """담당자 배정 및 인계"""
        user = verify_gateway_request()
        ensure_officer(user)
        req_env = get_current_request().env
        ticket = _get_ticket(ticket_id, user)

        target_user = req_env['res.users'].browse(int(assignee_id)) if assignee_id else user
        if not target_user.exists():
            raise UserError("Target officer user not found.")

        old_assignee_name = ticket.assignee_name
        ticket.action_assign_to_user(target_user)

        safe_reason = _safe_html_text(reason) if reason else ""
        reason_html = f"<br/>인계 사유: {safe_reason}" if safe_reason else ""
        ticket.message_post(
            body=f'<div data-msg-type="reassign"><b>[담당자 변경]</b> {html.escape(old_assignee_name)} -> {html.escape(target_user.name)}{reason_html}</div>'
        )
        return _workflow_res(ticket, assignee_id=ticket.assignee_id.id, assignee_name=ticket.assignee_name)

    @http.route('/api/v1/tickets/start-progress', type='json', auth='none', methods=['POST'], csrf=False)
    def start_progress_ticket(self, ticket_id: int):
        """처리 시작"""
        user = verify_gateway_request()
        ensure_officer(user)
        ticket = _get_ticket(ticket_id, user)
        ensure_assignee_or_admin(ticket, user)
        ticket.action_start_progress()
        ticket.message_post(body=f"<b>[처리 시작]</b> 담당자({html.escape(user.name)})가 문의 처리를 시작하였습니다.")
        return _workflow_res(ticket)

    @http.route('/api/v1/tickets/pending', type='json', auth='none', methods=['POST'], csrf=False)
    def pending_ticket(self, ticket_id: int, reason: str = None):
        """답변 대기 요청"""
        user = verify_gateway_request()
        ensure_officer(user)
        ticket = _get_ticket(ticket_id, user)
        ensure_assignee_or_admin(ticket, user)

        safe_reason = _safe_html_text(reason) if reason else ""
        ticket.pending_reason = safe_reason
        ticket.action_pending()
        reason_display = safe_reason or "사원 추가 확인 요청"
        ticket.message_post(body=f'<div data-msg-type="pending_request"><b>[답변 대기 요청]</b><br/>{reason_display}</div>')
        return _workflow_res(ticket, pending_reason=ticket.pending_reason)

    @http.route('/api/v1/tickets/close', type='json', auth='none', methods=['POST'], csrf=False)
    def close_ticket(self, ticket_id: int, note: str = None):
        """직권 종결 처리"""
        user = verify_gateway_request()
        ensure_officer(user)
        ticket = _get_ticket(ticket_id, user)

        if note:
            safe_note = _safe_html_text(note)
            ticket.resolution_note = safe_note
        elif not ticket.resolution_note:
            ticket.resolution_note = "담당자 직권 종결 처리"

        ticket.action_close()
        ticket.message_post(body=f"<b>[티켓 종결]</b> IT 담당자({html.escape(user.name)})에 의해 문의가 종결되었습니다.")
        return _workflow_res(ticket)

    @http.route('/api/v1/tickets/cancel', type='json', auth='none', methods=['POST'], csrf=False)
    def cancel_ticket(self, ticket_id: int, reason: str = None):
        """문의 취소"""
        user = verify_gateway_request()
        ticket = _get_ticket(ticket_id, user)
        ensure_author_or_officer(ticket, user)

        safe_reason = _safe_html_text(reason) if reason else ""
        ticket.action_cancel()
        cancel_msg = "<b>[문의 취소]</b> 사용자에 의해 문의가 취소되었습니다."
        if safe_reason:
            cancel_msg += f"<br/>취소 사유: {safe_reason}"
        ticket.message_post(body=cancel_msg)
        return _workflow_res(ticket)

    @http.route('/api/v1/tickets/toggle-faq', type='json', auth='none', methods=['POST'], csrf=False)
    def toggle_faq(self, ticket_id: int):
        """FAQ 추천 토글"""
        user = verify_gateway_request()
        ensure_officer(user)
        ticket = _get_ticket(ticket_id, user)
        ticket.action_toggle_faq()
        return {
            "status": "success",
            "data": {
                "id": ticket.id,
                "ticket_number": ticket.ticket_number,
                "is_faq": ticket.is_faq,
                "write_date": _format_datetime_utc(ticket.write_date),
            }
        }
