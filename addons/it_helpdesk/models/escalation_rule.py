# -*- coding: utf-8 -*-
"""SLA 에스컬레이션 규칙 및 실행 이력 모델."""
from datetime import timedelta
import html
import logging

from odoo import models, fields, api
from odoo.exceptions import ValidationError

from .assign_rule import CATEGORY_SELECTION
from .ticket_sla_mixin import NON_ACTIVE_STATUSES, SLA_WARN_HOURS
from ..utils.auto_assign import OPEN_STATUSES, pick_officer

_logger = logging.getLogger(__name__)

PRIORITY_SELECTION = [("0", "낮음"), ("1", "보통"), ("2", "높음"), ("3", "긴급")]
TRIGGER_SELECTION = [("imminent", "마감 임박"), ("overdue", "기한 초과")]
ACTION_SELECTION = [("notify", "알림 발송"), ("reassign", "자동 재배정")]


class HelpDeskEscalationRule(models.Model):
    _name = "it.helpdesk.escalation.rule"
    _description = "IT 헬프데스크 자동 에스컬레이션 규칙"
    _order = "sequence, id"

    name = fields.Char(string="규칙명", required=True, help="관리자 화면과 알림에 표시되는 규칙 이름")
    active = fields.Boolean(string="활성", default=True, help="체크 해제 시 크론에서 실행되지 않습니다.")
    sequence = fields.Integer(string="순서", default=10, help="숫자가 작을수록 먼저 평가됩니다.")
    trigger = fields.Selection(
        TRIGGER_SELECTION, string="실행 조건", required=True, default="overdue",
        help="마감 임박 또는 기한 초과 시점을 선택합니다.",
    )
    after_hours = fields.Integer(
        string="초과 경과 시간(시간)", default=0,
        help="기한 초과 후 지정한 시간이 지난 티켓을 대상으로 합니다. (마감 임박 조건에서는 무시)",
    )
    category = fields.Selection(CATEGORY_SELECTION, string="분야", help="비워 두면 전체 분야를 대상으로 합니다.")
    priority_min = fields.Selection(
        PRIORITY_SELECTION, string="최소 긴급도",
        help="선택한 긴급도 이상인 문의만 대상으로 합니다. 비워 두면 전체 긴급도 대상입니다.",
    )
    action = fields.Selection(
        ACTION_SELECTION, string="실행 작업", required=True, default="notify",
        help="조건 충족 시 수행할 작업(알림 발송 또는 자동 재배정)을 선택합니다.",
    )
    notify_user_ids = fields.Many2many(
        "res.users", "it_helpdesk_escalation_rule_user_rel", "rule_id", "user_id",
        string="알림 수신자",
        help="알림 작업 시 수신할 담당자/관리자 목록. 비워 두면 활성 관리자 전체에게 발송됩니다.",
    )
    target_user_id = fields.Many2one(
        "res.users", string="재배정 대상 담당자",
        help="자동 재배정 작업 시 지정할 담당자. 비워 두면 분야별 배정 규칙에 따라 자동 선택됩니다.",
    )
    log_ids = fields.One2many("it.helpdesk.escalation.log", "rule_id", string="실행 이력", readonly=True)

    @api.constrains("after_hours")
    def _check_after_hours_non_negative(self):
        for rule in self:
            if (rule.after_hours or 0) < 0:
                raise ValidationError("경과 시간은 0 이상이어야 합니다.")

    @api.constrains("action", "trigger")
    def _check_reassign_only_overdue(self):
        for rule in self:
            if rule.action == "reassign" and rule.trigger != "overdue":
                raise ValidationError("자동 재배정은 기한 초과 규칙에서만 사용할 수 있습니다.")

    @api.constrains("notify_user_ids")
    def _check_notify_users_have_group(self):
        for rule in self:
            invalid = rule.notify_user_ids.filtered(
                lambda u: not (
                    u.has_group("it_helpdesk.group_helpdesk_officer")
                    or u.has_group("it_helpdesk.group_helpdesk_manager")
                )
            )
            if invalid:
                raise ValidationError(
                    "담당자 또는 관리자 권한이 없는 사용자는 알림 수신자로 지정할 수 없습니다: %s"
                    % ", ".join(invalid.mapped("name"))
                )

    def _build_candidate_domain(self, cur_now, logged_ids):
        self.ensure_one()
        domain = [("status", "not in", NON_ACTIVE_STATUSES), ("deadline", "!=", False)]
        if self.category:
            domain.append(("category", "=", self.category))
        if self.priority_min:
            domain.append(("priority", "in", [str(p) for p in range(int(self.priority_min), 4)]))
        if logged_ids:
            domain.append(("id", "not in", logged_ids))

        if self.trigger == "overdue":
            cutoff = cur_now - timedelta(hours=max(0, self.after_hours or 0))
            domain.append(("deadline", "<=", cutoff))
        else:
            branches = [
                ["&", "&", ("priority", "=", prio), ("deadline", ">=", cur_now), ("deadline", "<=", cur_now + timedelta(hours=hrs))]
                for prio, hrs in SLA_WARN_HOURS.items()
            ]
            domain.extend(["|", "|", "|"] + [item for sub in branches for item in sub])
        return domain

    def _resolve_notify_recipients(self):
        self.ensure_one()
        if self.notify_user_ids:
            return self.notify_user_ids.filtered(lambda u: u.active)
        mgr_group = self.env.ref("it_helpdesk.group_helpdesk_manager", raise_if_not_found=False)
        return mgr_group.users.filtered(lambda u: u.active) if mgr_group else self.env["res.users"]

    def _pick_alternative_officer(self, category, exclude_user_id):
        assign_rule = self.env["it.helpdesk.assign.rule"].sudo().search(
            [("category", "=", category), ("active", "=", True)], limit=1
        )
        if not assign_rule:
            return None
        candidates = assign_rule.officer_ids.filtered(
            lambda u: u.active
            and u.id != exclude_user_id
            and u.has_group("it_helpdesk.group_helpdesk_officer")
            and not u._helpdesk_is_absent()
        )
        if not candidates:
            return None
        ticket_model = self.env["it.helpdesk.ticket"].sudo()
        return min(
            candidates,
            key=lambda u: (ticket_model.search_count([("assignee_id", "=", u.id), ("status", "in", OPEN_STATUSES)]), u.id),
        )

    def _execute_notify(self, ticket, root_partner_id):
        recipients = self._resolve_notify_recipients()
        if not recipients:
            return "skipped", "활성 알림 수신자 없음"
        safe_name = html.escape(self.name)
        for user in recipients:
            ticket.sudo().activity_schedule(
                "mail.mail_activity_data_todo",
                user_id=user.id,
                summary=f"[에스컬레이션] {self.name}",
                note=f"에스컬레이션 규칙 '{safe_name}' 조건에 해당하여 알림이 발송되었습니다.",
            )
        recipient_names = ", ".join(html.escape(u.name) for u in recipients)
        recipient_ids = ",".join(str(u.id) for u in recipients)
        ticket.sudo().message_post(
            body=(
                f'<div data-recipient-ids="{recipient_ids}" data-rule-id="{self.id}" data-msg-type="escalation_rule">'
                f"<b>[에스컬레이션 규칙]</b> '{safe_name}' 조건에 해당하여 알림이 발송되었습니다. "
                f"(수신: {recipient_names})</div>"
            ),
            subtype_xmlid="mail.mt_note",
            author_id=root_partner_id,
        )
        return "done", f"알림 발송 ({len(recipients)}명)"

    def _execute_reassign(self, ticket, root_partner_id):
        if self.target_user_id:
            target = self.target_user_id
            if not target.active or target._helpdesk_is_absent():
                return "skipped", "지정 대상 담당자 부재 또는 비활성"
            if ticket.assignee_id and ticket.assignee_id.id == target.id:
                return "skipped", "이미 지정 대상 담당자에게 배정됨"
        else:
            cat = self.category or ticket.category
            target = pick_officer(self.env, cat)
            if target and ticket.assignee_id and target.id == ticket.assignee_id.id:
                target = self._pick_alternative_officer(cat, exclude_user_id=ticket.assignee_id.id)
            if not target:
                return "skipped", "재배정 가능한 담당자 후보 없음"

        old_assignee = ticket.assignee_id
        old_name = ticket.assignee_name or "배정 대기"
        ticket.sudo().action_assign_to_user(target)
        old_attr = f' data-old-user-id="{old_assignee.id}"' if old_assignee else ""
        safe_name = html.escape(self.name)
        ticket.sudo().message_post(
            body=(
                f'<div{old_attr} data-msg-type="reassign">'
                f"<b>[담당자 변경]</b> {html.escape(old_name)} -> {html.escape(target.name)}"
                f"<br/>인계 사유: 에스컬레이션 규칙 '{safe_name}'</div>"
            ),
            subtype_xmlid="mail.mt_note",
            author_id=root_partner_id,
        )
        return "done", f"담당자 재배정 ({target.name})"

    def _execute_on_ticket(self, ticket, root_partner_id):
        self.ensure_one()
        if self.action == "notify":
            return self._execute_notify(ticket, root_partner_id)
        return self._execute_reassign(ticket, root_partner_id)

    @api.model
    def _run_escalation_rules(self, now=None, limit=200):
        """활성 에스컬레이션 규칙을 sequence 순으로 평가하고 티켓당 1회 실행한다."""
        cur_now = now or fields.Datetime.now()
        rules = self.sudo().search([("active", "=", True)], order="sequence asc, id asc")
        Ticket = self.env["it.helpdesk.ticket"].sudo()
        Log = self.env["it.helpdesk.escalation.log"].sudo()
        root_partner_id = self.env.ref("base.partner_root").id

        executed = 0
        skipped = 0
        for rule in rules:
            logged_rows = Log.search_read([("rule_id", "=", rule.id)], ["ticket_id"], load=False)
            logged_ids = [r["ticket_id"] for r in logged_rows if r.get("ticket_id")]
            tickets = Ticket.search(rule._build_candidate_domain(cur_now, logged_ids), order="deadline asc, id asc", limit=limit)
            for ticket in tickets:
                try:
                    with self.env.cr.savepoint():
                        res, note = rule._execute_on_ticket(ticket, root_partner_id)
                        Log.create({"rule_id": rule.id, "ticket_id": ticket.id, "executed_at": cur_now, "result": res, "note": note})
                        if res == "done":
                            executed += 1
                        else:
                            skipped += 1
                except Exception:
                    _logger.warning("에스컬레이션 규칙 실행 실패: rule_id=%s, ticket_id=%s", rule.id, ticket.id, exc_info=True)
        return {"executed": executed, "skipped": skipped}


class HelpDeskEscalationLog(models.Model):
    _name = "it.helpdesk.escalation.log"
    _description = "IT 헬프데스크 에스컬레이션 실행 이력"
    _order = "executed_at desc, id desc"

    rule_id = fields.Many2one("it.helpdesk.escalation.rule", string="에스컬레이션 규칙", required=True, ondelete="cascade", index=True)
    ticket_id = fields.Many2one("it.helpdesk.ticket", string="문의 티켓", required=True, ondelete="cascade", index=True)
    executed_at = fields.Datetime(string="실행 일시", required=True, default=fields.Datetime.now)
    result = fields.Selection([("done", "실행 완료"), ("skipped", "건너뜀")], string="실행 결과", required=True)
    note = fields.Char(string="비고")

    _sql_constraints = [
        ("uniq_rule_ticket", "UNIQUE(rule_id, ticket_id)", "같은 규칙은 티켓당 한 번만 실행할 수 있습니다."),
    ]
