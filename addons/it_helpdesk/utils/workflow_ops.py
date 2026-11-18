# -*- coding: utf-8 -*-
"""단건 및 일괄 티켓 워크플로우 공통 실행 유틸."""
import html
from odoo.exceptions import UserError

from .text_utils import _safe_html_text
from .validators import ensure_officer, ensure_assignee_or_admin


def do_assign(ticket, user, target_user, reason=None):
    """담당자 배정 및 인계 실행 (권한 검증 + 상태 전이 + 채터 기록)."""
    ensure_officer(user)
    if not target_user or not target_user.exists():
        raise UserError("지정한 담당자를 찾을 수 없습니다.")

    old_assignee_name = ticket.assignee_name
    ticket.action_assign_to_user(target_user)

    safe_reason = _safe_html_text(reason) if reason else ""
    reason_html = f"<br/>인계 사유: {safe_reason}" if safe_reason else ""
    ticket.message_post(
        body=f'<div data-msg-type="reassign"><b>[담당자 변경]</b> {html.escape(old_assignee_name)} -> {html.escape(target_user.name)}{reason_html}</div>'
    )
    return ticket


def do_start_progress(ticket, user):
    """처리 시작 실행 (권한 검증 + 상태 전이 + 채터 기록)."""
    ensure_officer(user)
    ensure_assignee_or_admin(ticket, user)
    ticket.action_start_progress()
    ticket.message_post(body=f"<b>[처리 시작]</b> 담당자({html.escape(user.name)})가 문의 처리를 시작하였습니다.")
    return ticket


def do_close(ticket, user, note=None):
    """직권 종결 실행 (권한 검증 + 조치 내용 보완 + 상태 전이 + 채터 기록)."""
    ensure_officer(user)
    if note:
        safe_note = _safe_html_text(note)
        ticket.resolution_note = safe_note
    elif not ticket.resolution_note:
        ticket.resolution_note = "담당자 직권 종결 처리"

    ticket.action_close()
    ticket.message_post(body=f"<b>[티켓 종결]</b> IT 담당자({html.escape(user.name)})에 의해 문의가 종결되었습니다.")
    return ticket
