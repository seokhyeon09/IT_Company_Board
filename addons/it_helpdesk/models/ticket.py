from datetime import timedelta
from odoo import models, fields, api
from odoo.exceptions import UserError

class HelpDeskTicket(models.Model):
    _name = "it.helpdesk.ticket"
    _description = "IT 문의 티켓"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    title = fields.Char(string="문의 제목", required=True)
    content = fields.Html(string="상세 내용", required=True)

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
    )

    priority = fields.Selection(
        [
            ("0","낮음"),
            ("1","보통"),
            ("2","높음"),
            ("3","긴급"),
        ],
        string="긴급도",
        default="0",
        tracking=True,
    )

    deadline = fields.Datetime(
        string="처리 기한(SLA)",
        tracking=True,
        help="약속된 조치 완료 기한입니다.",
    )

    is_overdue = fields.Boolean(
        string="기한 초과",
        compute="_compute_is_overdue",
        search="_search_is_overdue",
    )

    author_id = fields.Many2one(
        "res.users",
        string="요청 직원",
        default=lambda self: self.env.user,
        readonly=True,
    )
    assignee_id = fields.Many2one("res.users", string="IT 담당자", tracking=True)

    assignee_name = fields.Char(string="IT 담당자", compute="_compute_assignee_name")

    def _compute_assignee_name(self):
        for record in self:
            if record.assignee_id:
                record.assignee_name = record.assignee_id.name
            else:
                record.assignee_name = "배정 대기"

    resolution_note = fields.Html(
        string="조치 내용",
    )
    
    is_officer = fields.Boolean(compute="_compute_is_officer")
    def _compute_is_officer(self):
            has_group = self.env.user.has_group('it_helpdesk.group_helpdesk_officer')
            for record in self:
                record.is_officer = has_group

    @api.onchange('priority')
    def _onchange_priority_set_deadline(self):
        """긴급도 선택에 따른 SLA 처리 기한 자동 산정"""
        now = fields.Datetime.now()
        hours_map = {
            '3': 4,    # 긴급: 4시간
            '2': 24,   # 높음: 1일 (24시간)
            '1': 48,   # 보통: 2일 (48시간)
            '0': 72,   # 낮음: 3일 (72시간)
        }
        hours = hours_map.get(self.priority, 48)
        self.deadline = now + timedelta(hours=hours)

    @api.depends('deadline', 'status')
    def _compute_is_overdue(self):
        """기한 초과 여부 자동 계산"""
        now = fields.Datetime.now()
        for record in self:
            if record.deadline and record.status not in ('resolved', 'closed', 'canceled'):
                record.is_overdue = record.deadline < now
            else:
                record.is_overdue = False

    def _search_is_overdue(self, operator, value):
        """기한 초과 건 검색 도메인 지원"""
        now = fields.Datetime.now()
        if (operator == '=' and value is True) or (operator == '!=' and value is False):
            return [('deadline', '<', now), ('status', 'not in', ('resolved', 'closed', 'canceled'))]
        else:
            return ['|', ('deadline', '>=', now), ('status', 'in', ('resolved', 'closed', 'canceled'))]


    def action_assign_to_me(self):
        for record in self:
            record.assignee_id = self.env.user
            record.status = 'assigned'

    def action_start_progress(self):
        for record in self :
            record.status = "in_progress"

    def action_pending(self):
        for record in self :
            record.status = "pending"

    def action_restart_ticket(self):
        for record in self :
            record.status = "in_progress"

    def action_resolve(self):
        for record in self :
            if not record.resolution_note : 
                raise UserError("해결 완료 처리를 하려면 조치 내용을 먼저 작성해야 합니다.")
            else :
                record.status = "resolved"

    def action_close(self):
        for record in self : 
            record.status = "closed"

    def action_cancel(self) : 
        for record in self :
            record.status = "canceled"

    def action_reopen(self):
        for record in self:
            if self.env.user.has_group('it_helpdesk.group_helpdesk_officer') :
                record.status="in_progress"
                record.message_post(body="티켓이 IT 담당자에 의해 재오픈되었습니다.")
            else :
                raise UserError("티켓 재오픈은 IT 담당자만 수행할 수 있습니다.")
