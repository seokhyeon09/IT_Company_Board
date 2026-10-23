from odoo import models, fields
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

    author_id = fields.Many2one(
        "res.users",
        string="요청 직원",
        default=lambda self: self.env.user,
        readonly=True,
    )
    assignee_id = fields.Many2one("res.users", string="IT 담당자", tracking=True)

    assignee_name = fields.Char(string="IT 담당자", compute="_compute_assignee_name")

    rating = fields.Selection(
        [
            ("0","미평가"),
            ("1","매우 불만족"),
            ("2","불만족"),
            ("3","보통"),
            ("4","만족"),
            ("5","매우 만족"),
        ],
        string="만족도",
        default="0",
        tracking=True,
    )

    rating_feedback = fields.Text(
        string = "만족도 의견"
    )

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

    is_author = fields.Boolean(compute="_compute_is_author")
    def _compute_is_author(self):
        for record in self:
            if record.author_id == self.env.user :
                record.is_author =True
            else :
                record.is_author =False

    def action_assign_to_me(self):
        for record in self:
            if self.env.user.has_group("it_helpdesk.group_helpdesk_officer"):
                record.assignee_id = self.env.user
                record.status = 'assigned'
            else :
                raise UserError("담당 접수는 IT 담당자만 수행할 수 있습니다.")

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
            if self.env.user.has_group("it_helpdesk.group_helpdesk_officer"):
                if not record.resolution_note :
                    raise UserError("해결 완료 처리를 하려면 조치 내용을 먼저 작성해야 합니다.")
                else :
                    record.status = "resolved"
            else :
                raise UserError("해결 완료를 IT 담당자만 할 수 있습니다.")
                
    def action_close(self):
        for record in self : 
            record.status = "closed"

    def action_cancel(self) : 
        for record in self :
            if record.author_id == self.env.user or self.env.user.has_group("it_helpdesk.group_helpdesk_officer") :
                record.status = "canceled"
            else :
                raise UserError("문의 취소는 작성자 본인 또는 IT 담당자만 수행할 수 있습니다.")

    def action_reopen(self):
        for record in self:
            if self.env.user.has_group('it_helpdesk.group_helpdesk_officer') :
                record.status="in_progress"
                record.message_post(body="티켓이 IT 담당자에 의해 재오픈되었습니다.")
            else :
                raise UserError("티켓 재오픈은 IT 담당자만 수행할 수 있습니다.")

    def action_submit_rating(self):
        for record in self:

            if self.env.user != record.author_id : 
                raise UserError("만족도 평가는 문의를 등록한 직원 본인만 제출할 수 있습니다.")
            elif record.status != "resolved":
                raise UserError("만족도 평가는 해결 완료된 문의에 한 해서 작성할 수 있습니다.")
            elif record.rating == "0" : 
                raise UserError("만족도 평가는 1점부터 5점사이로 선택해야 합니다.")
            else :
                record.status = "closed"
                record.message_post(body="작성자에 의해 만족도 조사가 작성되었습니다.")
