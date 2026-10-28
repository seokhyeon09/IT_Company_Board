# -*- coding: utf-8 -*-
import html
import logging
from odoo import http
from odoo.http import request
from odoo.exceptions import AccessError, UserError

from ..utils import (
    _format_datetime_utc,
    _safe_html_text,
    _clean_html,
    parse_iso_utc,
    ConcurrencyError,
    verify_gateway_request,
    get_current_request,
)

_logger = logging.getLogger(__name__)

class TicketWorkflowAPIController(http.Controller):
    """Ticket Workflow State Transitions, Actions, and Resolutions API"""

    @http.route('/api/v1/tickets/resolve', type='json', auth='none', methods=['POST'], csrf=False)
    def resolve_ticket(self, ticket_id: int, resolution_note: str, if_match_write_date: str = None):
        """티켓 조치 완료 (낙관적 동시성 제어 및 IT 담당자 권한 검증)"""
        user = verify_gateway_request()
        if not (user.has_group('it_helpdesk.group_helpdesk_officer') or user._is_admin()):
            raise AccessError("Only helpdesk officers can resolve tickets.")

        ticket = get_current_request().env['it.helpdesk.ticket'].with_user(user).browse(int(ticket_id))
        if not ticket.exists():
            raise UserError("Ticket not found.")

        is_admin = user._is_admin()
        is_assignee = bool(ticket.assignee_id and ticket.assignee_id.id == user.id)
        if not (is_admin or is_assignee):
            raise AccessError("Only the assigned officer or an administrator can resolve tickets.")

        if if_match_write_date:
            client_dt = parse_iso_utc(if_match_write_date)
            record_dt = ticket.write_date
            is_match = False
            if record_dt and client_dt:
                if client_dt.microsecond == 0 and record_dt.microsecond != 0:
                    is_match = (client_dt.replace(microsecond=0) == record_dt.replace(microsecond=0))
                else:
                    is_match = (client_dt == record_dt)

            if not is_match:
                current_iso = _format_datetime_utc(record_dt)
                raise ConcurrencyError(
                    f"Concurrency Conflict: Ticket '{ticket.ticket_number}' was modified by another transaction. "
                    f"Current write_date is '{current_iso}', but provided if_match was '{if_match_write_date}'.",
                    current_write_date=current_iso
                )

        safe_note = _safe_html_text(resolution_note)
        ticket.resolution_note = safe_note
        if ticket.status == 'submitted':
            ticket.action_assign_to_me()
            ticket.action_start_progress()
        elif ticket.status == 'assigned':
            ticket.action_start_progress()
        ticket.action_resolve()
        ticket.message_post(body=f'<div data-msg-type="resolution"><b>[조치 답변]</b><br/>{safe_note}</div>')

        return {
            "status": "success",
            "data": {
                "id": ticket.id,
                "ticket_number": ticket.ticket_number,
                "status": ticket.status,
                "write_date": _format_datetime_utc(ticket.write_date)
            }
        }

    @http.route('/api/v1/tickets/rate', type='json', auth='none', methods=['POST'], csrf=False)
    def rate_ticket(self, ticket_id: int, rating: str, rating_comment: str = None, if_match_write_date: str = None):
        """요청 직원의 티켓 만족도 평가 및 자동 종결 처리"""
        user = verify_gateway_request()
        ticket = get_current_request().env['it.helpdesk.ticket'].with_user(user).browse(int(ticket_id))
        if not ticket.exists():
            raise UserError("Ticket not found.")

        if ticket.author_id.id != user.id:
            raise AccessError("Only the author can evaluate and rate this ticket.")

        if ticket.status != 'resolved':
            raise UserError("Only resolved tickets can be rated and closed.")

        if str(rating) not in ('1', '2', '3', '4', '5'):
            raise UserError("Rating must be between 1 and 5.")

        ticket.write({
            'rating': str(rating),
            'rating_comment': rating_comment or False
        })
        ticket.action_submit_rating()

        return {
            "status": "success",
            "data": {
                "id": ticket.id,
                "ticket_number": ticket.ticket_number,
                "status": ticket.status,
                "rating": ticket.rating,
                "rating_comment": ticket.rating_comment,
                "write_date": _format_datetime_utc(ticket.write_date)
            }
        }

    @http.route('/api/v1/tickets/toggle-faq', type='json', auth='none', methods=['POST'], csrf=False)
    def toggle_faq(self, ticket_id: int):
        """IT 담당자의 사내 FAQ 지식창고 추천/해제 토글"""
        user = verify_gateway_request()
        if not (user.has_group('it_helpdesk.group_helpdesk_officer') or user._is_admin()):
            raise AccessError("Only helpdesk officers can manage FAQ tickets.")

        ticket = get_current_request().env['it.helpdesk.ticket'].with_user(user).browse(int(ticket_id))
        if not ticket.exists():
            raise UserError("Ticket not found.")

        ticket.action_toggle_faq()

        return {
            "status": "success",
            "data": {
                "id": ticket.id,
                "ticket_number": ticket.ticket_number,
                "is_faq": ticket.is_faq,
                "write_date": _format_datetime_utc(ticket.write_date)
            }
        }

    @http.route('/api/v1/tickets/restart', type='json', auth='none', methods=['POST'], csrf=False)
    def restart_ticket(self, ticket_id: int, reason: str = None):
        """직원의 추가 문의 (재문의: 답변대기, 해결완료, 종결 건 재개)"""
        user = verify_gateway_request()
        ticket = get_current_request().env['it.helpdesk.ticket'].with_user(user).browse(int(ticket_id))
        if not ticket.exists():
            raise UserError("Ticket not found.")

        is_officer = user.has_group('it_helpdesk.group_helpdesk_officer') or user._is_admin()
        if not is_officer and ticket.author_id.id != user.id:
            raise AccessError("Only the author can request a follow-up inquiry.")

        if ticket.status not in ('pending', 'resolved'):
            raise UserError("Only pending or resolved tickets can be restarted. Closed tickets cannot be reopened by inquiry.")

        was_pending = (ticket.status == 'pending')
        ticket.action_restart_ticket()
        if reason and str(reason).strip():
            safe_reason = _safe_html_text(reason)
            if was_pending:
                ticket.message_post(body=f'<div data-msg-type="pending_response"><b>[답변 대기 회신]</b><br/>{safe_reason}</div>')
            else:
                ticket.message_post(body=f'<div data-msg-type="inquiry"><b>[추가 재문의]</b><br/>{safe_reason}</div>')

        return {
            "status": "success",
            "data": {
                "id": ticket.id,
                "ticket_number": ticket.ticket_number,
                "status": ticket.status,
                "write_date": _format_datetime_utc(ticket.write_date)
            }
        }

    @http.route('/api/v1/tickets/update-resolution', type='json', auth='none', methods=['POST'], csrf=False)
    def update_resolution(self, ticket_id: int, resolution_note: str, if_match_write_date: str = None):
        """IT 담당자의 조치 내용(답변) 수정 (낙관적 동시성 제어 적용)"""
        user = verify_gateway_request()
        if not (user.has_group('it_helpdesk.group_helpdesk_officer') or user._is_admin()):
            raise AccessError("Only helpdesk officers can update resolution notes.")

        ticket = get_current_request().env['it.helpdesk.ticket'].with_user(user).browse(int(ticket_id))
        if not ticket.exists():
            raise UserError("Ticket not found.")

        is_admin = user._is_admin()
        is_assignee = bool(ticket.assignee_id and ticket.assignee_id.id == user.id)
        if not (is_admin or is_assignee):
            raise AccessError("Only the assigned officer or an administrator can update resolution notes.")

        if if_match_write_date:
            client_dt = parse_iso_utc(if_match_write_date)
            record_dt = ticket.write_date
            is_match = False
            if record_dt and client_dt:
                if client_dt.microsecond == 0 and record_dt.microsecond != 0:
                    is_match = (client_dt.replace(microsecond=0) == record_dt.replace(microsecond=0))
                else:
                    is_match = (client_dt == record_dt)

            if not is_match:
                current_iso = _format_datetime_utc(record_dt)
                raise ConcurrencyError(
                    f"Concurrency Conflict: Ticket '{ticket.ticket_number}' was modified by another transaction. "
                    f"Current write_date is '{current_iso}', but provided if_match was '{if_match_write_date}'.",
                    current_write_date=current_iso
                )

        clean_note = str(resolution_note).strip()
        if not clean_note or len(clean_note) < 5:
            raise UserError("Resolution note must be at least 5 characters.")

        old_note = ticket.resolution_note or ""
        old_preview = _clean_html(old_note)
        safe_clean_note = _safe_html_text(clean_note)
        safe_old_preview = html.escape(old_preview)
        ticket.resolution_note = safe_clean_note

        latest_res_msg = False
        for msg in ticket.message_ids.sorted(key=lambda m: m.id, reverse=True):
            body = msg.body or ""
            if 'data-msg-type="resolution"' in body or "IT 담당자 조치 내용:" in body:
                latest_res_msg = msg
                break

        if latest_res_msg:
            latest_res_msg.sudo().write({
                'body': f'<div data-msg-type="resolution"><b>[조치 답변]</b><br/>{safe_clean_note}</div>'
            })
        else:
            ticket.message_post(body=f'<div data-msg-type="resolution"><b>[조치 답변]</b><br/>{safe_clean_note}</div>')

        ticket.message_post(
            body=(
                f'<b>[답변 내용 수정 이력]</b><br/>'
                f'<span style="color:#64748b; text-decoration:line-through;">[수정 전] {safe_old_preview}</span><br/>'
                f'<span style="color:#059669; font-weight:bold;">[수정 후] {safe_clean_note}</span>'
            )
        )

        return {
            "status": "success",
            "data": {
                "id": ticket.id,
                "ticket_number": ticket.ticket_number,
                "resolution_note": ticket.resolution_note,
                "status": ticket.status,
                "write_date": _format_datetime_utc(ticket.write_date)
            }
        }

    @http.route('/api/v1/tickets/assign', type='json', auth='none', methods=['POST'], csrf=False)
    def assign_ticket(self, ticket_id: int, assignee_id: int = None, reason: str = None):
        """IT 담당자 티켓 배정 및 인계 (시작 전 자유 인계 / 시작 후 본인 및 관리자만 인계 + 사유 필수)"""
        req_env = get_current_request().env
        user = verify_gateway_request()
        if not (user.has_group('it_helpdesk.group_helpdesk_officer') or user._is_admin()):
            raise AccessError("Only helpdesk officers can assign tickets.")

        ticket = req_env['it.helpdesk.ticket'].with_user(user).browse(int(ticket_id))
        if not ticket.exists():
            raise UserError("Ticket not found.")

        if ticket.status in ('resolved', 'closed', 'canceled'):
            raise UserError("이미 완료되거나 종결된 티켓은 담당자를 변경할 수 없습니다.")

        old_assignee = ticket.assignee_id
        is_admin = user._is_admin()

        if assignee_id and int(assignee_id) != user.id:
            target_user = req_env['res.users'].sudo().browse(int(assignee_id))
            if not target_user.exists():
                raise UserError("Target officer not found.")
            if not (target_user.has_group('it_helpdesk.group_helpdesk_officer') or target_user._is_admin()):
                raise UserError("Designated user is not an IT officer.")
        else:
            target_user = user

        if old_assignee and old_assignee.id == target_user.id:
            return {
                "status": "success",
                "data": {
                    "id": ticket.id,
                    "ticket_number": ticket.ticket_number,
                    "status": ticket.status,
                    "assignee_id": ticket.assignee_id.id,
                    "assignee_name": ticket.assignee_name,
                    "write_date": _format_datetime_utc(ticket.write_date)
                }
            }

        # 상태별 가로채기 방지 락 (시작 후에는 원 담당자 본인 및 관리자만 인계 가능)
        if old_assignee and ticket.status in ('in_progress', 'pending'):
            is_current_assignee = (old_assignee.id == user.id)
            if not (is_admin or is_current_assignee):
                raise AccessError("처리 중인 티켓은 원 담당자 본인 또는 관리자만 변경(인계)할 수 있습니다.")

        # 담당자 변경 시 관리자 포함 사유 필수 체크
        clean_reason = str(reason).strip() if reason else ""
        if old_assignee and not clean_reason:
            raise UserError("담당자 변경(인계) 사유를 반드시 입력해야 합니다.")

        safe_reason = _safe_html_text(clean_reason) if clean_reason else "사유 미기재"

        # 실제 담당자 배정 실행
        ticket.action_assign_to_user(target_user)

        # 타임라인 메시지 발행
        if old_assignee:
            post_msg = ticket.message_post(
                body=(
                    f'<div data-msg-type="reassign" data-old-user-id="{old_assignee.id}" data-new-user-id="{target_user.id}">'
                    f'<b>[담당자 변경]</b><br/>'
                    f'{html.escape(user.name)}님이 담당자를 '
                    f'<b>{html.escape(old_assignee.name)}</b> 담당자에서 '
                    f'<b>{html.escape(target_user.name)}</b> 담당자(으)로 변경하였습니다.<br/>'
                    f'<b>변경 사유:</b> {safe_reason}'
                    f'</div>'
                ),
                subtype_xmlid='mail.mt_note',
            )
        else:
            if target_user.id == user.id:
                post_msg = ticket.message_post(
                    body=f"<b>[담당자 배정]</b><br/>{html.escape(user.name)} 담당자가 본인에게 문의를 배정하였습니다.",
                    subtype_xmlid='mail.mt_note',
                )
            else:
                post_msg = ticket.message_post(
                    body=f"<b>[담당자 배정]</b><br/>{html.escape(user.name)} 담당자가 {html.escape(target_user.name)} 담당자에게 문의를 지정 배정하였습니다.",
                    subtype_xmlid='mail.mt_note',
                )

        # 변경 조작자 본인의 알림함에는 자동 읽음 처리
        if post_msg:
            req_env['it.helpdesk.notification.read'].sudo().create({
                'user_id': user.id,
                'notification_id': f"{ticket.id}-msg-{post_msg.id}-s",
            })

        return {
            "status": "success",
            "data": {
                "id": ticket.id,
                "ticket_number": ticket.ticket_number,
                "status": ticket.status,
                "assignee_id": ticket.assignee_id.id if ticket.assignee_id else None,
                "assignee_name": ticket.assignee_name,
                "write_date": _format_datetime_utc(ticket.write_date)
            }
        }

    @http.route('/api/v1/tickets/start-progress', type='json', auth='none', methods=['POST'], csrf=False)
    def start_progress_ticket(self, ticket_id: int):
        """IT 담당자 처리 시작 (assigned 또는 pending -> in_progress)"""
        user = verify_gateway_request()
        if not (user.has_group('it_helpdesk.group_helpdesk_officer') or user._is_admin()):
            raise AccessError("Only helpdesk officers can change ticket status.")

        ticket = get_current_request().env['it.helpdesk.ticket'].with_user(user).browse(int(ticket_id))
        if not ticket.exists():
            raise UserError("Ticket not found.")

        is_admin = user._is_admin()
        is_assignee = bool(ticket.assignee_id and ticket.assignee_id.id == user.id)
        if not (is_admin or is_assignee):
            raise AccessError("Only the assigned officer or an administrator can start progress on this ticket.")

        ticket.action_start_progress()

        return {
            "status": "success",
            "data": {
                "id": ticket.id,
                "ticket_number": ticket.ticket_number,
                "status": ticket.status,
                "write_date": _format_datetime_utc(ticket.write_date)
            }
        }

    @http.route('/api/v1/tickets/pending', type='json', auth='none', methods=['POST'], csrf=False)
    def pending_ticket(self, ticket_id: int, reason: str = None):
        """IT 담당자 답변 대기 요청 (in_progress -> pending, 사유 기록)"""
        user = verify_gateway_request()
        if not (user.has_group('it_helpdesk.group_helpdesk_officer') or user._is_admin()):
            raise AccessError("Only helpdesk officers can set ticket to pending.")

        ticket = get_current_request().env['it.helpdesk.ticket'].with_user(user).browse(int(ticket_id))
        if not ticket.exists():
            raise UserError("Ticket not found.")

        is_admin = user._is_admin()
        is_assignee = bool(ticket.assignee_id and ticket.assignee_id.id == user.id)
        if not (is_admin or is_assignee):
            raise AccessError("Only the assigned officer or an administrator can request pending response.")

        ticket.action_pending()
        clean_reason = str(reason).strip() if reason and str(reason).strip() else "추가 정보 및 확인 요청"
        safe_reason = _safe_html_text(clean_reason)
        ticket.write({'pending_reason': clean_reason})
        safe_officer_name = html.escape(user.name)
        ticket.message_post(body=f'<div data-msg-type="pending_request"><b>[답변 대기 요청]</b><br/>담당자({safe_officer_name}): {safe_reason}</div>')

        return {
            "status": "success",
            "data": {
                "id": ticket.id,
                "ticket_number": ticket.ticket_number,
                "status": ticket.status,
                "pending_reason": ticket.pending_reason,
                "write_date": _format_datetime_utc(ticket.write_date)
            }
        }

    @http.route('/api/v1/tickets/close', type='json', auth='none', methods=['POST'], csrf=False)
    def close_ticket(self, ticket_id: int, note: str = None):
        """IT 담당자 직권 종결 처리"""
        user = verify_gateway_request()
        if not (user.has_group('it_helpdesk.group_helpdesk_officer') or user._is_admin()):
            raise AccessError("Only helpdesk officers can close tickets.")

        ticket = get_current_request().env['it.helpdesk.ticket'].with_user(user).browse(int(ticket_id))
        if not ticket.exists():
            raise UserError("Ticket not found.")

        is_admin = user._is_admin()
        is_assignee = bool(ticket.assignee_id and ticket.assignee_id.id == user.id)
        if not (is_admin or is_assignee):
            raise AccessError("Only the assigned officer or an administrator can close tickets.")

        if note and str(note).strip():
            safe_note = _safe_html_text(note)
            ticket.resolution_note = safe_note
        elif not ticket.resolution_note or not _clean_html(ticket.resolution_note).strip():
            safe_note = "IT 담당자에 의해 직권 종결 처리되었습니다."
            ticket.resolution_note = safe_note
        else:
            safe_note = _clean_html(ticket.resolution_note)

        ticket.action_close()
        safe_user_name = html.escape(user.name)
        ticket.message_post(body=f"<b>[직권 종결]</b><br/>IT 담당자({safe_user_name})에 의해 문의가 최종 종결되었습니다.<br/>종결 사유: {safe_note}")

        return {
            "status": "success",
            "data": {
                "id": ticket.id,
                "ticket_number": ticket.ticket_number,
                "status": ticket.status,
                "write_date": _format_datetime_utc(ticket.write_date)
            }
        }

    @http.route('/api/v1/tickets/cancel', type='json', auth='none', methods=['POST'], csrf=False)
    def cancel_ticket(self, ticket_id: int, reason: str = None):
        """요청 직원 또는 IT 담당자의 문의 취소"""
        user = verify_gateway_request()
        ticket = get_current_request().env['it.helpdesk.ticket'].with_user(user).browse(int(ticket_id))
        if not ticket.exists():
            raise UserError("Ticket not found.")

        is_officer = user.has_group('it_helpdesk.group_helpdesk_officer') or user._is_admin()
        if not is_officer and ticket.author_id.id != user.id:
            raise AccessError("Only the author or helpdesk officers can cancel this ticket.")

        ticket.action_cancel()
        safe_reason = _safe_html_text(reason) if reason and str(reason).strip() else "사유 미기재"
        safe_user_name = html.escape(user.name)
        ticket.message_post(body=f"<b>[문의 취소]</b><br/>취소자: {safe_user_name}<br/>취소 사유: {safe_reason}")

        return {
            "status": "success",
            "data": {
                "id": ticket.id,
                "ticket_number": ticket.ticket_number,
                "status": ticket.status,
                "write_date": _format_datetime_utc(ticket.write_date)
            }
        }
