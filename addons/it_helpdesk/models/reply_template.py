# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError
from .assign_rule import CATEGORY_SELECTION

VALID_TEMPLATE_CATEGORIES = {code for code, _ in CATEGORY_SELECTION}


class HelpDeskReplyTemplate(models.Model):
    _name = "it.helpdesk.reply.template"
    _description = "IT 헬프데스크 답변 상용구"
    _order = "name"

    name = fields.Char(string="상용구 이름", required=True)
    category = fields.Selection(CATEGORY_SELECTION, string="분야")
    body = fields.Text(string="상용구 본문", required=True)
    active = fields.Boolean(string="활성", default=True)

    @api.constrains("name", "body")
    def _check_name_and_body(self):
        for rec in self:
            name = (rec.name or "").strip()
            if not name or len(name) > 60:
                raise ValidationError("상용구 이름은 1~60자 이내로 입력해야 합니다.")
            body = (rec.body or "").strip()
            if not body or len(body) > 3000:
                raise ValidationError("상용구 본문은 1~3000자 이내로 입력해야 합니다.")

    @staticmethod
    def _normalize_vals(vals):
        item = dict(vals)
        if item.get("category") == "":
            item["category"] = False
        if "name" in item:
            if isinstance(item["name"], str):
                item["name"] = item["name"].strip()
            if not item["name"]:
                raise ValidationError("상용구 이름은 1~60자 이내로 입력해야 합니다.")
        if "body" in item:
            if isinstance(item["body"], str):
                item["body"] = item["body"].strip()
            if not item["body"]:
                raise ValidationError("상용구 본문은 1~3000자 이내로 입력해야 합니다.")
        return item

    @api.model_create_multi
    def create(self, vals_list):
        cleaned = [self._normalize_vals(vals) for vals in vals_list]
        return super().create(cleaned)

    def write(self, vals):
        return super().write(self._normalize_vals(vals))
