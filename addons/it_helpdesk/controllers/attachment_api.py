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
)

_logger = logging.getLogger(__name__)

class AttachmentAPIController:
    """Ticket Attachment Upload and Download API"""

    @http.route('/api/v1/tickets/upload-attachment', type='json', auth='none', methods=['POST'], csrf=False)
    def upload_attachment(self, ticket_id: int, name: str, datas: str, mimetype: str = None):
        """티켓 첨부파일 업로드 (Base64)"""
        user = verify_gateway_request()
        ticket = request.env['it.helpdesk.ticket'].with_user(user).browse(int(ticket_id))
        if not ticket.exists():
            raise UserError("Ticket not found.")

        is_officer = user.has_group('it_helpdesk.group_helpdesk_officer') or user._is_admin()
        if not is_officer and ticket.author_id.id != user.id:
            raise AccessError("Only the author or helpdesk officers can upload attachments.")

        clean_name = os.path.basename(str(name).strip())
        if not clean_name:
            clean_name = "attachment"

        attachment = request.env['ir.attachment'].sudo().create({
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
        ticket = request.env['it.helpdesk.ticket'].with_user(user).browse(int(ticket_id))
        if not ticket.exists():
            raise UserError("Ticket not found.")

        is_officer = user.has_group('it_helpdesk.group_helpdesk_officer') or user._is_admin()
        if not is_officer and ticket.author_id.id != user.id and not ticket.is_faq:
            raise AccessError("Access denied to ticket attachment.")

        attachment = request.env['ir.attachment'].sudo().browse(int(attachment_id))
        if not attachment.exists() or attachment.res_model != 'it.helpdesk.ticket' or attachment.res_id != ticket.id:
            raise UserError("Attachment not found.")

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
