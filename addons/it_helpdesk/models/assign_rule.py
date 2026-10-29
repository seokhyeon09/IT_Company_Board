# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError

# 티켓 카테고리와 동일한 값이어야 함 (tests/test_auto_assign.py에서 키 일치 검증)
CATEGORY_SELECTION = [
    ("hw", "하드웨어"),
    ("sw", "소프트웨어"),
    ("network", "네트워크"),
    ("account", "계정/권한"),
    ("etc", "기타"),
]


class HelpDeskAssignRule(models.Model):
    _name = "it.helpdesk.assign.rule"
    _description = "IT 헬프데스크 분야별 담당자 배정 규칙"
    _order = "category"

    category = fields.Selection(CATEGORY_SELECTION, string="분야", required=True)
    officer_ids = fields.Many2many(
        "res.users",
        "it_helpdesk_assign_rule_user_rel",
        "rule_id",
        "user_id",
        string="담당 후보",
    )
    active = fields.Boolean(string="활성", default=True)

    @api.constrains("category", "active")
    def _check_unique_active_category(self):
        for rule in self.filtered("active"):
            duplicated = self.search_count([
                ("id", "!=", rule.id),
                ("category", "=", rule.category),
                ("active", "=", True),
            ])
            if duplicated:
                raise ValidationError("같은 분야의 활성 규칙은 하나만 둘 수 있습니다.")

    @api.constrains("officer_ids")
    def _check_officers_have_group(self):
        for rule in self:
            invalid = rule.officer_ids.filtered(
                lambda u: not u.has_group("it_helpdesk.group_helpdesk_officer")
            )
            if invalid:
                raise ValidationError(
                    "담당자 권한이 없는 사용자는 후보로 지정할 수 없습니다: %s"
                    % ", ".join(invalid.mapped("name"))
                )
