# -*- coding: utf-8 -*-
from odoo import models, fields


class ResUsers(models.Model):
    _inherit = "res.users"

    helpdesk_absent = fields.Boolean(string="부재 중 여부", default=False)
    helpdesk_absent_until = fields.Date(string="부재 종료일")

    def _helpdesk_is_absent(self, today=None):
        """부재 설정 및 종료일 기준 실효 부재 여부를 반환한다."""
        self.ensure_one()
        if not self.helpdesk_absent:
            return False
        if not self.helpdesk_absent_until:
            return True
        ref_date = today if today is not None else fields.Date.today()
        if isinstance(ref_date, str):
            ref_date = fields.Date.from_string(ref_date)
        return self.helpdesk_absent_until >= ref_date
