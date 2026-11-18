# -*- coding: utf-8 -*-
"""담당자 답변 상용구 CRUD API (담당자/관리자 전용)."""
from odoo import http
from odoo.exceptions import UserError

from ..utils import (
    _format_datetime_utc,
    verify_gateway_request,
    get_current_request,
    ensure_officer,
    NotFoundError,
)

VALID_CATEGORIES = ('hw', 'sw', 'network', 'account', 'etc')


def _parse_category(category):
    if category in (None, False, ''):
        return False
    if category in VALID_CATEGORIES:
        return category
    raise UserError("유효하지 않은 분야입니다.")


def _serialize_template(rec, user):
    return {
        "id": rec.id,
        "name": rec.name,
        "category": rec.category or "",
        "body": rec.body,
        "is_mine": rec.create_uid.id == user.id,
        "write_date": _format_datetime_utc(rec.write_date),
    }


class ReplyTemplateAPIController(http.Controller):
    """Officer Reply Template CRUD API"""

    @http.route('/api/v1/reply-templates/list', type='json', auth='none', methods=['POST'], csrf=False)
    def list_reply_templates(self, category=None, **kwargs):
        user = verify_gateway_request()
        ensure_officer(user)
        tmpl_env = get_current_request().env['it.helpdesk.reply.template'].with_user(user)

        domain = []
        if category in VALID_CATEGORIES:
            domain.extend(['|', ('category', '=', category), ('category', '=', False)])

        records = tmpl_env.search(domain, order='name asc, id asc')
        return {
            "status": "success",
            "data": [_serialize_template(rec, user) for rec in records],
        }

    @http.route('/api/v1/reply-templates/create', type='json', auth='none', methods=['POST'], csrf=False)
    def create_reply_template(self, name=None, category='', body=None, **kwargs):
        user = verify_gateway_request()
        ensure_officer(user)
        tmpl_env = get_current_request().env['it.helpdesk.reply.template'].with_user(user)

        clean_name = str(name).strip() if name is not None else ""
        clean_body = str(body).strip() if body is not None else ""
        cat_val = _parse_category(category)

        rec = tmpl_env.create({
            "name": clean_name,
            "category": cat_val,
            "body": clean_body,
        })
        return {"status": "success", "data": _serialize_template(rec, user)}

    @http.route('/api/v1/reply-templates/update', type='json', auth='none', methods=['POST'], csrf=False)
    def update_reply_template(self, template_id=None, name=None, category='', body=None, **kwargs):
        user = verify_gateway_request()
        ensure_officer(user)
        if not template_id:
            raise NotFoundError("답변 상용구를 찾을 수 없습니다.")

        rec = get_current_request().env['it.helpdesk.reply.template'].with_user(user).browse(int(template_id))
        if not rec.exists():
            raise NotFoundError("답변 상용구를 찾을 수 없습니다.")

        clean_name = str(name).strip() if name is not None else ""
        clean_body = str(body).strip() if body is not None else ""
        cat_val = _parse_category(category)

        rec.write({
            "name": clean_name,
            "category": cat_val,
            "body": clean_body,
        })
        return {"status": "success", "data": _serialize_template(rec, user)}

    @http.route('/api/v1/reply-templates/delete', type='json', auth='none', methods=['POST'], csrf=False)
    def delete_reply_template(self, template_id=None, **kwargs):
        user = verify_gateway_request()
        ensure_officer(user)
        if not template_id:
            raise NotFoundError("답변 상용구를 찾을 수 없습니다.")

        rec = get_current_request().env['it.helpdesk.reply.template'].with_user(user).browse(int(template_id))
        if not rec.exists():
            raise NotFoundError("답변 상용구를 찾을 수 없습니다.")

        rec.unlink()
        return {"status": "success"}
