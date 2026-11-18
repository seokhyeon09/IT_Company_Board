# -*- coding: utf-8 -*-
"""실제 알림 메일 발송 이력 모델 및 크론 진입점."""
from odoo import api, fields, models

from ..utils.real_mail import cron_send_real_mail


class HelpDeskMailDispatch(models.Model):
    _name = "it.helpdesk.mail.dispatch"
    _description = "IT 헬프데스크 알림 메일 발송 이력"
    _order = "dispatched_at desc, id desc"

    ticket_id = fields.Many2one(
        "it.helpdesk.ticket",
        string="문의 티켓",
        required=True,
        ondelete="cascade",
        index=True,
    )
    event_key = fields.Char(string="이벤트 키", required=True, index=True)
    recipient_id = fields.Many2one(
        "res.users",
        string="수신자",
        ondelete="set null",
        index=True,
    )
    email_to = fields.Char(string="수신 이메일")
    subject = fields.Char(string="제목")
    state = fields.Selection(
        [
            ("sent", "발송 완료"),
            ("failed", "발송 실패"),
            ("skipped", "건너뜀"),
        ],
        string="발송 상태",
        required=True,
    )
    attempts = fields.Integer(string="시도 횟수", default=1)
    error = fields.Char(string="오류/사유")
    mail_id = fields.Integer(string="메일 ID")
    dispatched_at = fields.Datetime(
        string="발송 일시",
        default=fields.Datetime.now,
    )

    _sql_constraints = [
        (
            "uniq_ticket_event_recipient",
            "UNIQUE(ticket_id, event_key, recipient_id)",
            "동일한 티켓, 이벤트, 수신자 조합에는 중복 발송 이력을 생성할 수 없습니다.",
        ),
    ]

    @api.model
    def _cron_send_real_mail(self, limit_tickets=200):
        """1분 주기 실제 알림 메일 발송 크론 진입점."""
        return cron_send_real_mail(self.env, limit_tickets=limit_tickets)
