# -*- coding: utf-8 -*-
"""담당자 내부 메모 API (담당자/관리자 전용, 사원 비노출)."""
from odoo import http
from odoo.exceptions import UserError

from ..utils import (
    _format_datetime_utc,
    _safe_html_text,
    verify_gateway_request,
    get_current_request,
    ensure_officer,
)

MAX_INTERNAL_NOTE_LENGTH = 2000


class TicketNoteAPIController(http.Controller):
    """Officer Internal Note API"""

    @http.route('/api/v1/tickets/notes/add', type='json', auth='none', methods=['POST'], csrf=False)
    def add_internal_note(self, ticket_id=None, content=None, **kwargs):
        """티켓에 담당자/관리자 전용 내부 메모를 추가한다."""
        user = verify_gateway_request()
        ensure_officer(user)

        if not ticket_id or isinstance(ticket_id, bool):
            raise UserError("문의를 찾을 수 없습니다.")

        req_env = get_current_request().env
        ticket = req_env['it.helpdesk.ticket'].with_user(user).browse(int(ticket_id))
        if not ticket.exists():
            raise UserError("문의를 찾을 수 없습니다.")

        clean = str(content).strip() if content is not None else ""
        if not clean:
            raise UserError("내용을 입력해 주세요.")
        if len(clean) > MAX_INTERNAL_NOTE_LENGTH:
            raise UserError("메모는 최대 2000자까지 입력할 수 있습니다.")

        safe = _safe_html_text(clean)
        msg = ticket.message_post(
            body=f'<div data-msg-type="internal_note"><b>[내부 메모]</b><br/>{safe}</div>',
            subtype_xmlid='mail.mt_note',
        )

        return {
            "status": "success",
            "data": {
                "id": msg.id,
                "author_id": msg.author_id.id if msg.author_id else None,
                "author_name": msg.author_id.name if msg.author_id else user.name,
                "date": _format_datetime_utc(msg.date),
                "content": clean,
            },
        }
