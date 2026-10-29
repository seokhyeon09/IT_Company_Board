# -*- coding: utf-8 -*-
"""SLA 4단계 상태(none/ok/imminent/overdue) 계산 및 임박 경고/관리자 에스컬레이션 크론 믹스인."""
from datetime import timedelta
import html
import logging

from odoo import models, fields, api
from ..utils.webhook_notifier import notify_sla_escalated

_logger = logging.getLogger(__name__)

SLA_WARN_HOURS = {
    '3': 1,   # 긴급(총 4h): 마감 1시간 전부터 임박
    '2': 4,   # 높음(총 24h): 마감 4시간 전부터 임박
    '1': 8,   # 보통(총 48h): 마감 8시간 전부터 임박
    '0': 12,  # 낮음(총 72h): 마감 12시간 전부터 임박
}

CLOSED_STATUSES = ('resolved', 'closed', 'canceled')


class HelpDeskTicketSlaMixin(models.AbstractModel):
    _name = "it.helpdesk.ticket.sla.mixin"
    _description = "IT 문의 티켓 SLA 임박 경고 및 에스컬레이션 믹스인"

    sla_warned_at = fields.Datetime(string="SLA 임박 경고 일시", readonly=True, copy=False)
    sla_escalated_at = fields.Datetime(string="SLA 에스컬레이션 일시", readonly=True, copy=False)
    first_resolved_date = fields.Datetime(string="최초 해결 일시", readonly=True, copy=False)
    resolution_hours = fields.Float(
        string="해결 소요시간(시간)",
        compute="_compute_resolution_hours",
        store=True,
        copy=False,
    )

    @api.depends("first_resolved_date", "create_date")
    def _compute_resolution_hours(self):
        for record in self:
            if record.first_resolved_date and record.create_date:
                diff_sec = (record.first_resolved_date - record.create_date).total_seconds()
                record.resolution_hours = round(max(0.0, diff_sec / 3600.0), 1)
            else:
                record.resolution_hours = 0.0
    sla_state = fields.Selection(
        [
            ("none", "해당 없음"),
            ("ok", "정상"),
            ("imminent", "임박"),
            ("overdue", "초과"),
        ],
        string="SLA 상태",
        compute="_compute_sla_state",
        search="_search_sla_state",
    )

    @api.depends("deadline", "status", "priority")
    def _compute_sla_state(self):
        now = fields.Datetime.now()
        for record in self:
            if not record.deadline or record.status in CLOSED_STATUSES:
                record.sla_state = "none"
                continue
            if record.deadline < now:
                record.sla_state = "overdue"
                continue
            warn_hours = SLA_WARN_HOURS.get(record.priority or "0", 8)
            if record.deadline <= now + timedelta(hours=warn_hours):
                record.sla_state = "imminent"
            else:
                record.sla_state = "ok"

    def _search_sla_state(self, operator, value):
        now = fields.Datetime.now()
        if operator not in ("=", "!="):
            return [("id", "=", 0)]
        if value == "overdue":
            dom = [("deadline", "<", now), ("status", "not in", CLOSED_STATUSES)]
            return dom if operator == "=" else ["!"] + dom
        if value == "none":
            dom = ["|", ("deadline", "=", False), ("status", "in", CLOSED_STATUSES)]
            return dom if operator == "=" else ["!"] + dom
        if value == "imminent":
            branches = []
            for prio, hrs in SLA_WARN_HOURS.items():
                branches.append([
                    "&", "&", "&",
                    ("priority", "=", prio),
                    ("status", "not in", CLOSED_STATUSES),
                    ("deadline", ">=", now),
                    ("deadline", "<=", now + timedelta(hours=hrs)),
                ])
            dom = ["|", "|", "|"] + [ item for sub in branches for item in sub ]
            return dom if operator == "=" else ["!"] + dom
        if value == "ok":
            max_warn = now + timedelta(hours=max(SLA_WARN_HOURS.values()))
            dom = [("deadline", ">", max_warn), ("status", "not in", CLOSED_STATUSES)]
            return dom if operator == "=" else ["!"] + dom
        return [("id", "=", 0)]

    @api.model
    def _cron_sla_monitor(self, limit=200):
        """15분 주기 SLA 임박 경고 및 기한 초과 관리자 에스컬레이션 크론."""
        now = fields.Datetime.now()
        max_warn_horizon = now + timedelta(hours=max(SLA_WARN_HOURS.values()))
        candidates = self.search([
            ("status", "not in", CLOSED_STATUSES),
            ("deadline", "!=", False),
            ("deadline", "<=", max_warn_horizon),
        ], order="deadline asc, id asc", limit=limit)

        warned_count = 0
        escalated_count = 0
        root_partner_id = self.env.ref("base.partner_root").id

        for ticket in candidates:
            try:
                with self.env.cr.savepoint():
                    state = ticket.sla_state
                    s_name = html.escape(ticket.assignee_id.name if ticket.assignee_id else "미배정")
                    dl_str = fields.Datetime.to_string(ticket.deadline)
                    if state == "overdue" and not ticket.sla_escalated_at:
                        ticket.sudo().write({"sla_escalated_at": now})
                        ticket.sudo().message_post(
                            body=(
                                f'<div data-msg-type="sla_escalation">'
                                f'<b>[SLA 기한 초과 에스컬레이션]</b> 처리 기한({dl_str} UTC)이 초과되어 '
                                f'IT 관리자에게 에스컬레이션되었습니다. (현재 담당자: {s_name})</div>'
                            ),
                            subtype_xmlid="mail.mt_note",
                            author_id=root_partner_id,
                        )
                        notify_sla_escalated(ticket, use_postcommit=True)
                        escalated_count += 1
                    elif state == "imminent" and not ticket.sla_warned_at and not ticket.sla_escalated_at:
                        ticket.sudo().write({"sla_warned_at": now})
                        ticket.sudo().message_post(
                            body=(
                                f'<div data-msg-type="sla_warning">'
                                f'<b>[SLA 마감 임박 경고]</b> 처리 기한({dl_str} UTC)이 임박했습니다. '
                                f'신속한 조치가 필요합니다. (현재 담당자: {s_name})</div>'
                            ),
                            subtype_xmlid="mail.mt_note",
                            author_id=root_partner_id,
                        )
                        warned_count += 1
            except Exception:
                _logger.warning("SLA 모니터 처리 실패: ticket_id=%s", ticket.id, exc_info=True)

        _logger.info("SLA 모니터 실행 완료: 임박 경고 %s건, 에스컬레이션 %s건", warned_count, escalated_count)
        return {"warned": warned_count, "escalated": escalated_count}
