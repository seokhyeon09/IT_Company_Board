# -*- coding: utf-8 -*-
from odoo import models, fields

class HelpdeskNotificationRead(models.Model):
    _name = "it.helpdesk.notification.read"
    _description = "사용자별 알림 메일 읽음 기록"
    _order = "read_at desc, id desc"

    user_id = fields.Many2one(
        "res.users",
        string="사용자",
        required=True,
        ondelete="cascade",
        index=True,
    )
    notification_id = fields.Char(
        string="알림 ID",
        required=True,
        index=True,
    )
    read_at = fields.Datetime(
        string="읽은 일시",
        default=fields.Datetime.now,
        required=True,
    )

    _sql_constraints = [
        (
            "user_notification_unique",
            "unique(user_id, notification_id)",
            "이미 읽음 처리된 알림입니다.",
        ),
    ]
