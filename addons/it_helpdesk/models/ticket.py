# -*- coding: utf-8 -*-
from datetime import timedelta
from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError, AccessError
from ..utils.text_utils import is_html_empty

SLA_HOURS = {
    '3': 4,    # 긴급: 4시간
    '2': 24,   # 높음: 1일 (24시간)
    '1': 48,   # 보통: 2일 (48시간)
    '0': 72,   # 낮음: 3일 (72시간)
}

class HelpDeskTicket(models.Model):
    _name = "it.helpdesk.ticket"
    _description = "IT 문의 티켓"
    _inherit = ['mail.thread', 'mail.activity.mixin', 'it.helpdesk.ticket.workflow.mixin']
    _rec_name = "ticket_number"
    _order = "id desc"

    ticket_number = fields.Char(string="접수 번호", readonly=True, copy=False, default="New", index=True)
    title = fields.Char(string="문의 제목", required=True)
    content = fields.Html(string="상세 내용", required=True)

    @api.depends('ticket_number', 'title')
    def _compute_display_name(self):
        for record in self:
            if record.ticket_number and record.ticket_number != 'New':
                record.display_name = record.ticket_number
            else:
                record.display_name = record.title or "New"

    category = fields.Selection(
        [
            ("hw", "하드웨어"),
            ("sw", "소프트웨어"),
            ("network", "네트워크"),
            ("account", "계정/권한"),
            ("etc", "기타"),
        ],
        string="카테고리",
        default="etc",
    )

    status = fields.Selection(
        [
            ("submitted", "접수대기"),
            ("assigned", "담당자배정"),
            ("in_progress", "처리중"),
            ("pending", "답변 대기"),
            ("resolved", "해결완료"),
            ("closed", "종결"),
            ("canceled", "취소"),
        ],
        string="상태",
        default="submitted",
        tracking=True,
        copy=False,
    )

    priority = fields.Selection(
        [
            ("0", "낮음"),
            ("1", "보통"),
            ("2", "높음"),
            ("3", "긴급"),
        ],
        string="긴급도",
        default="0",
        tracking=True,
    )

    deadline = fields.Datetime(string="처리 기한(SLA)", tracking=True, copy=False)
    is_overdue = fields.Boolean(string="기한 초과", compute="_compute_is_overdue", search="_search_is_overdue")

    author_id = fields.Many2one("res.users", string="요청 직원", default=lambda self: self.env.user, readonly=True)
    assignee_id = fields.Many2one("res.users", string="IT 담당자 배정", tracking=True, copy=False)
    assignee_name = fields.Char(string="IT 담당자", compute="_compute_assignee_name")

    def _compute_assignee_name(self):
        for record in self:
            record.assignee_name = record.assignee_id.name if record.assignee_id else "배정 대기"

    resolution_note = fields.Html(string="조치 내용", copy=False)
    pending_reason = fields.Text(string="답변 대기 요청 사유", copy=False)

    rating = fields.Selection(
        [
            ("0", "미평가"),
            ("1", "1점 (매우 불만)"),
            ("2", "2점 (불만)"),
            ("3", "3점 (보통)"),
            ("4", "4점 (만족)"),
            ("5", "5점 (매우 만족)"),
        ],
        string="최신 만족도",
        default="0",
        tracking=True,
        copy=False,
    )
    rating_comment = fields.Text(string="만족도 한줄평", tracking=True, copy=False)
    is_faq = fields.Boolean(string="FAQ 추천 사례", tracking=True, copy=False)

    rating_ids = fields.One2many("it.helpdesk.ticket.rating", "ticket_id", string="만족도 평가 이력", copy=False)
    current_round = fields.Integer(string="현재 평가 차수", compute="_compute_current_round")

    @api.depends('rating_ids')
    def _compute_current_round(self):
        for record in self:
            record.current_round = len(record.rating_ids) + 1

    is_officer = fields.Boolean(compute="_compute_is_officer")

    def _compute_is_officer(self):
        has_group = self.env.is_admin() or self.env.user.has_group('it_helpdesk.group_helpdesk_officer')
        for record in self:
            record.is_officer = has_group

    @api.constrains('title')
    def _check_title_not_empty(self):
        for record in self:
            if not record.title or not record.title.strip():
                raise ValidationError("문의 제목은 공백만으로 작성할 수 없습니다.")

    @api.constrains('content')
    def _check_content_not_empty(self):
        for record in self:
            if is_html_empty(record.content):
                raise ValidationError("문의 상세 내용을 입력해주세요.")

    def _calculate_deadline(self, priority, base_time=None):
        base = base_time or fields.Datetime.now()
        hours = SLA_HOURS.get(priority, 48)
        return base + timedelta(hours=hours)

    @api.onchange('priority')
    def _onchange_priority_set_deadline(self):
        self.deadline = self._calculate_deadline(self.priority)

    @api.depends('deadline', 'status')
    def _compute_is_overdue(self):
        now = fields.Datetime.now()
        for record in self:
            if record.deadline and record.status not in ('resolved', 'closed', 'canceled'):
                record.is_overdue = record.deadline < now
            else:
                record.is_overdue = False

    def _search_is_overdue(self, operator, value):
        now = fields.Datetime.now()
        if (operator == '=' and value is True) or (operator == '!=' and value is False):
            return [('deadline', '<', now), ('status', 'not in', ('resolved', 'closed', 'canceled'))]
        else:
            return ['|', ('deadline', '>=', now), ('status', 'in', ('resolved', 'closed', 'canceled'))]

    def copy(self, default=None):
        default = dict(default or {})
        default.setdefault('title', f"{self.title} (복사본)")
        return super().copy(default)

    @api.model_create_multi
    def create(self, vals_list):
        is_officer = self.env.is_admin() or self.env.user.has_group('it_helpdesk.group_helpdesk_officer')
        now = fields.Datetime.now()
        for vals in vals_list:
            if vals.get('ticket_number', 'New') == 'New':
                vals['ticket_number'] = self.env['ir.sequence'].next_by_code('it.helpdesk.ticket') or 'New'
            if not is_officer and not self.env.su:
                if vals.get('status') and vals['status'] != 'submitted':
                    vals['status'] = 'submitted'
            if not vals.get('deadline'):
                p = vals.get('priority', '0')
                vals['deadline'] = self._calculate_deadline(p, base_time=now)
        return super().create(vals_list)

    def write(self, vals):
        is_officer = self.env.is_admin() or self.env.user.has_group('it_helpdesk.group_helpdesk_officer')
        is_system = self.env.su

        if 'priority' in vals and 'deadline' not in vals:
            vals['deadline'] = self._calculate_deadline(vals['priority'])

        for record in self:
            if record.status in ('closed', 'canceled') and not is_system:
                allowed_fields = {'status', 'rating', 'rating_comment', 'is_faq', 'message_follower_ids', 'activity_ids', 'rating_ids'}
                if not set(vals.keys()).issubset(allowed_fields):
                    raise UserError("종결되거나 취소된 문의 티켓의 내용은 수정할 수 없습니다.")

            if 'status' in vals and not is_officer and not is_system:
                new_status = vals['status']
                is_author = record.author_id == self.env.user
                allowed = (
                    is_author and (
                        (record.status in ('submitted', 'assigned', 'in_progress', 'pending', 'resolved') and new_status == 'canceled') or
                        (record.status in ('pending', 'resolved') and new_status == 'in_progress') or
                        (record.status == 'resolved' and new_status == 'closed')
                    )
                )
                if not allowed:
                    raise AccessError("문의 티켓의 상태 전이 권한이 없습니다. (IT 담당자만 처리 가능)")

            if not is_system and record.author_id and self.env.user != record.author_id:
                if ('rating' in vals and vals['rating']) or ('rating_comment' in vals and vals['rating_comment']):
                    raise AccessError("고객 만족도 평가는 문의를 등록한 직원 본인만 작성하거나 수정할 수 있습니다.")

            if vals.get('status') in ('resolved', 'closed'):
                note = vals.get('resolution_note', record.resolution_note)
                if is_html_empty(note):
                    raise UserError("해결 완료 또는 종결 처리를 하려면 조치 내용(해결 방안)을 먼저 작성해야 합니다.")

        assignee_changed = 'assignee_id' in vals
        old_assignees = {rec.id: rec.assignee_id for rec in self} if assignee_changed else {}

        res = super().write(vals)

        if assignee_changed:
            todo_type = self.env.ref('mail.mail_activity_data_todo', raise_if_not_found=False)
            for record in self:
                if record.status not in ('resolved', 'closed', 'canceled'):
                    old_assignee = old_assignees.get(record.id)
                    new_assignee = record.assignee_id
                    if old_assignee != new_assignee:
                        if todo_type and record.activity_ids:
                            record.activity_ids.filtered(lambda a: a.activity_type_id == todo_type).unlink()
                        if new_assignee:
                            record.activity_schedule(
                                'mail.mail_activity_data_todo',
                                summary=f"IT 문의 조치 배정: {record.title}",
                                user_id=new_assignee.id,
                                date_deadline=record.deadline.date() if record.deadline else fields.Date.today()
                            )

        return res
