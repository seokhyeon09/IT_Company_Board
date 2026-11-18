# -*- coding: utf-8 -*-
import os
import html
import logging
from odoo import http
from odoo.http import request
from odoo.exceptions import AccessError, UserError

from ..utils import (
    _format_datetime_utc,
    verify_gateway_request,
    get_current_request,
    NotFoundError,
)

_logger = logging.getLogger(__name__)

class AttachmentAPIController(http.Controller):
    """Ticket Attachment Upload and Download API"""

    @http.route('/api/v1/tickets/upload-attachment', type='json', auth='none', methods=['POST'], csrf=False)
    def upload_attachment(self, ticket_id: int, name: str, datas: str, mimetype: str = None):
        """티켓 첨부파일 업로드 (Base64)"""
        user = verify_gateway_request()
        if datas and len(datas) > 7_000_000:
            raise UserError("첨부 파일 크기는 5MB를 초과할 수 없습니다.")
        ticket = get_current_request().env['it.helpdesk.ticket'].with_user(user).browse(int(ticket_id))
        if not ticket.exists():
            raise NotFoundError("문의를 찾을 수 없습니다.")

        is_officer = user.has_group('it_helpdesk.group_helpdesk_officer') or user._is_admin()
        if not is_officer and ticket.author_id.id != user.id:
            raise AccessError("작성자 또는 IT 담당자만 첨부 파일을 업로드할 수 있습니다.")

        clean_name = os.path.basename(str(name).strip())
        if not clean_name:
            clean_name = "attachment"

        attachment = get_current_request().env['ir.attachment'].sudo().create({
            'name': clean_name,
            'datas': datas,
            'res_model': 'it.helpdesk.ticket',
            'res_id': ticket.id,
            'mimetype': mimetype or 'application/octet-stream',
        })

        ticket.message_post(body=f"<b>[첨부파일 등록]</b><br/>파일명: {html.escape(clean_name)}")

        return {
            "status": "success",
            "data": {
                "id": attachment.id,
                "name": attachment.name,
                "mimetype": attachment.mimetype,
                "file_size": attachment.file_size,
                "create_date": _format_datetime_utc(attachment.create_date)
            }
        }

    @http.route('/api/v1/tickets/get-attachment', type='json', auth='none', methods=['POST'], csrf=False)
    def get_attachment(self, ticket_id: int, attachment_id: int):
        """티켓 첨부파일 다운로드/조회 (Base64 반환)"""
        user = verify_gateway_request()
        ticket = get_current_request().env['it.helpdesk.ticket'].with_user(user).browse(int(ticket_id))
        if not ticket.exists():
            raise NotFoundError("문의를 찾을 수 없습니다.")

        is_officer = user.has_group('it_helpdesk.group_helpdesk_officer') or user._is_admin()
        if not is_officer and ticket.author_id.id != user.id and not ticket.is_faq:
            raise AccessError("해당 첨부 파일에 접근할 권한이 없습니다.")

        attachment = get_current_request().env['ir.attachment'].sudo().browse(int(attachment_id))
        if not attachment.exists() or attachment.res_model != 'it.helpdesk.ticket' or attachment.res_id != ticket.id:
            raise NotFoundError("첨부 파일을 찾을 수 없습니다.")

        raw_datas = attachment.datas
        data_str = raw_datas.decode('utf-8') if isinstance(raw_datas, bytes) else (raw_datas or "")

        return {
            "status": "success",
            "data": {
                "id": attachment.id,
                "name": attachment.name,
                "mimetype": attachment.mimetype,
                "file_size": attachment.file_size,
                "datas": data_str,
            }
        }
