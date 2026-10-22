import re
from datetime import timedelta
from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError, AccessError

SLA_HOURS = {
    '3': 4,    # 긴급: 4시간
    '2': 24,   # 높음: 1일 (24시간)
    '1': 48,   # 보통: 2일 (48시간)
    '0': 72,   # 낮음: 3일 (72시간)
}


def _is_html_empty(html_content):
    """HTML 내용이 실질적으로 비어있는지 검사 (<p><br></p>, &nbsp; 등 방어)"""
    if not html_content:
        return True
    text = re.sub(r'<[^>]*>', '', html_content)
    text = text.replace('&nbsp;', ' ').strip()
    return not text


class HelpDeskTicket(models.Model):
    _name = "it.helpdesk.ticket"
    _description = "IT 문의 티켓"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = "ticket_number"
    _order = "id desc"

    ticket_number = fields.Char(
        string="접수 번호",
        readonly=True,
        copy=False,
        default="New",
        index=True,
    )
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

    deadline = fields.Datetime(
        string="처리 기한(SLA)",
        tracking=True,
        copy=False,
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
    assignee_id = fields.Many2one("res.users", string="IT 담당자 배정", tracking=True, copy=False)

    assignee_name = fields.Char(string="IT 담당자", compute="_compute_assignee_name")

    def _compute_assignee_name(self):
        for record in self:
            if record.assignee_id:
                record.assignee_name = record.assignee_id.name
            else:
                record.assignee_name = "배정 대기"

    resolution_note = fields.Html(
        string="조치 내용",
        copy=False,
    )

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

    # N:1 만족도 평가 이력 누적 (재문의 시 차수별 누적 관리)
    rating_ids = fields.One2many(
        "it.helpdesk.ticket.rating",
        "ticket_id",
        string="만족도 평가 이력",
        copy=False,
    )
    current_round = fields.Integer(
        string="현재 평가 차수",
        compute="_compute_current_round",
    )

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
        """RC-09: 문의 제목 공백 문자열 입력 방지"""
        for record in self:
            if not record.title or not record.title.strip():
                raise ValidationError("문의 제목은 공백만으로 작성할 수 없습니다.")

    @api.constrains('content')
    def _check_content_not_empty(self):
        """보완 5: 문의 상세 내용 빈 줄/공백 HTML 등록 방어"""
        for record in self:
            if _is_html_empty(record.content):
                raise ValidationError("문의 상세 내용을 입력해주세요.")

    def _calculate_deadline(self, priority, base_time=None):
        """RC-07: 변경 시각(now) 기준으로 SLA 마감 기한 산정 (초과 시 is_overdue=True 경고)"""
        base = base_time or fields.Datetime.now()
        hours = SLA_HOURS.get(priority, 48)
        return base + timedelta(hours=hours)

    @api.onchange('priority')
    def _onchange_priority_set_deadline(self):
        """긴급도 선택에 따른 SLA 처리 기한 자동 산정 (변경 시각 기준)"""
        self.deadline = self._calculate_deadline(self.priority)

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

    def copy(self, default=None):
        """보완 4: 티켓 복제 시 제목에 (복사본) 명시 및 초기화 상태 보장"""
        default = dict(default or {})
        default.setdefault('title', f"{self.title} (복사본)")
        return super().copy(default)

    @api.model_create_multi
    def create(self, vals_list):
        """티켓 생성 시 초기화, 고유 접수번호 채번 및 검증"""
        is_officer = self.env.is_admin() or self.env.user.has_group('it_helpdesk.group_helpdesk_officer')
        now = fields.Datetime.now()
        for vals in vals_list:
            # 확장 1: 티켓 고유 접수번호 자동 채번 (TKT-YYYY-0001)
            if vals.get('ticket_number', 'New') == 'New':
                vals['ticket_number'] = self.env['ir.sequence'].next_by_code('it.helpdesk.ticket') or 'New'
            # 일반 사원이 생성 시 상태를 submitted 외의 값으로 임의 주입하는 행위 방어
            if not is_officer and not self.env.su:
                if vals.get('status') and vals['status'] != 'submitted':
                    vals['status'] = 'submitted'
            # SLA 마감 기한이 없으면 priority 기준 자동 산정
            if not vals.get('deadline'):
                p = vals.get('priority', '0')
                vals['deadline'] = self._calculate_deadline(p, base_time=now)
        return super().create(vals_list)

    def write(self, vals):
        """상태 변경, 조치내용, 권한, 종결 불변성, Activity 이관 전수 검증"""
        is_officer = self.env.is_admin() or self.env.user.has_group('it_helpdesk.group_helpdesk_officer')
        is_system = self.env.su

        # RC-07: priority 변경 시 deadline 자동 재산정 (사용자 정책: 변경 시각 기준)
        if 'priority' in vals and 'deadline' not in vals:
            vals['deadline'] = self._calculate_deadline(vals['priority'])

        # 사전 검증 루프
        for record in self:
            # RC-03: 종결/취소 상태인 티켓 내용 수정 차단 (RPC 우회 방어)
            if record.status in ('closed', 'canceled') and not is_system:
                allowed_fields = {'status', 'rating', 'rating_comment', 'is_faq', 'message_follower_ids', 'activity_ids', 'rating_ids'}
                if not set(vals.keys()).issubset(allowed_fields):
                    raise UserError("종결되거나 취소된 문의 티켓의 내용은 수정할 수 없습니다.")

            # RC-02: 일반 사원의 임의 상태 전이 차단
            if 'status' in vals and not is_officer and not is_system:
                new_status = vals['status']
                is_author = record.author_id == self.env.user
                allowed = (
                    is_author and (
                        # 1) 본인 티켓 취소
                        (record.status in ('submitted', 'assigned', 'in_progress', 'pending') and new_status == 'canceled') or
                        # 2) 본인 티켓 재문의
                        (record.status in ('pending', 'resolved', 'closed') and new_status == 'in_progress') or
                        # 3) 본인 티켓 만족도 평가 완료 후 종결
                        (record.status == 'resolved' and new_status == 'closed')
                    )
                )
                if not allowed:
                    raise AccessError("문의 티켓의 상태 전이 권한이 없습니다. (IT 담당자만 처리 가능)")

            # 만족도 평가(rating, rating_comment) 작성 및 변경은 게시글 작성자 본인만 가능 (초기화 및 시스템 제외)
            if not is_system and record.author_id and self.env.user != record.author_id:
                if ('rating' in vals and vals['rating']) or ('rating_comment' in vals and vals['rating_comment']):
                    raise AccessError("고객 만족도 평가는 문의를 등록한 직원 본인만 작성하거나 수정할 수 있습니다.")

            # RC-01: 해결완료(resolved) 또는 종결(closed) 시 조치 내용 필수 검증 (칸반 드래그 앤 드롭 방어)
            if vals.get('status') in ('resolved', 'closed'):
                note = vals.get('resolution_note', record.resolution_note)
                if _is_html_empty(note):
                    raise UserError("해결 완료 또는 종결 처리를 하려면 조치 내용(해결 방안)을 먼저 작성해야 합니다.")

        # RC-06 사전 처리: 담당자 변경 감지
        assignee_changed = 'assignee_id' in vals
        old_assignees = {rec.id: rec.assignee_id for rec in self} if assignee_changed else {}

        res = super().write(vals)

        # RC-06 사후 처리: 담당자 변경 시 Activity 정리 및 새 담당자 할당
        if assignee_changed:
            todo_type = self.env.ref('mail.mail_activity_data_todo', raise_if_not_found=False)
            for record in self:
                if record.status not in ('resolved', 'closed', 'canceled'):
                    old_assignee = old_assignees.get(record.id)
                    new_assignee = record.assignee_id
                    if old_assignee != new_assignee:
                        # 1. 기존 Activity 정리
                        if todo_type and record.activity_ids:
                            record.activity_ids.filtered(lambda a: a.activity_type_id == todo_type).unlink()
                        # 2. 새 담당자에게 Activity 스케줄링
                        if new_assignee:
                            record.activity_schedule(
                                'mail.mail_activity_data_todo',
                                summary=f"IT 문의 조치 배정: {record.title}",
                                user_id=new_assignee.id,
                                date_deadline=record.deadline.date() if record.deadline else fields.Date.today()
                            )

        return res

    def action_assign_to_me(self):
        """IT 담당자 본인 배정"""
        for record in self:
            # RC-04: 상태 검증
            if record.status in ('resolved', 'closed', 'canceled'):
                raise UserError("이미 완료되거나 종결된 티켓은 담당자를 배정할 수 없습니다.")
            record.assignee_id = self.env.user
            record.status = 'assigned'
            
            # 기존 미완료 todo Activity 정리 후 본인에게 스케줄링
            todo_type = self.env.ref('mail.mail_activity_data_todo', raise_if_not_found=False)
            if todo_type and record.activity_ids:
                record.activity_ids.filtered(lambda a: a.activity_type_id == todo_type).unlink()

            record.activity_schedule(
                'mail.mail_activity_data_todo',
                summary=f"IT 문의 조치 배정: {record.title}",
                user_id=record.assignee_id.id,
                date_deadline=record.deadline.date() if record.deadline else fields.Date.today()
            )

    def action_start_progress(self):
        """처리 중으로 변경"""
        for record in self:
            # RC-04: 상태 검증
            if record.status not in ('assigned', 'pending'):
                raise UserError("담당자가 배정되었거나 답변 대기 상태인 티켓만 처리 중으로 변경할 수 있습니다.")
            record.status = "in_progress"

    def action_pending(self):
        """답변 대기로 변경"""
        for record in self:
            # RC-04: 상태 검증
            if record.status != 'in_progress':
                raise UserError("처리 중인 티켓만 답변 대기 상태로 변경할 수 있습니다.")
            record.status = "pending"

    def action_restart_ticket(self):
        """직원의 추가 문의(재문의: 답변대기, 해결완료, 종결 건 재개)"""
        for record in self:
            is_officer = self.env.is_admin() or self.env.user.has_group('it_helpdesk.group_helpdesk_officer')
            if record.author_id != self.env.user and not is_officer:
                raise UserError("추가 문의는 문의를 등록한 본인만 요청할 수 있습니다.")
            if record.status not in ('pending', 'resolved', 'closed'):
                raise UserError("답변 대기, 해결 완료 또는 종결된 티켓에 대해서만 추가 문의를 진행할 수 있습니다.")

            # 다음 차수 평가를 위해 현재 별점 입력값 초기화 (기존 rating_ids는 테이블에 안전하게 보존됨)
            record.sudo().write({'rating': '0', 'rating_comment': False})

            record.status = "in_progress"
            record.message_post(body="요청 직원이 추가 문의(재문의)를 등록하여 처리가 다시 진행됩니다.")

            # RC-05: 담당자에게 새 Activity 자동 스케줄링
            if record.assignee_id:
                record.activity_schedule(
                    'mail.mail_activity_data_todo',
                    summary=f"직원 재문의 확인 필요: {record.title}",
                    user_id=record.assignee_id.id,
                    date_deadline=fields.Date.today()
                )

    def action_resolve(self):
        """해결 완료"""
        for record in self:
            # RC-04: 상태 검증
            if record.status not in ('in_progress', 'pending'):
                raise UserError("처리 중이거나 답변 대기 상태인 티켓만 해결 완료 처리할 수 있습니다.")
            if _is_html_empty(record.resolution_note):
                raise UserError("해결 완료 처리를 하려면 조치 내용을 먼저 작성해야 합니다.")
            record.status = "resolved"
            if record.activity_ids:
                record.activity_ids.action_done()

    def action_close(self):
        """종결 처리"""
        for record in self:
            if not (self.env.is_admin() or self.env.user.has_group('it_helpdesk.group_helpdesk_officer')):
                raise UserError("문의 종결 처리는 IT 담당자만 수행할 수 있습니다.")
            if record.status not in ('resolved', 'in_progress'):
                raise UserError("해결 완료되었거나 처리 중인 티켓만 종결할 수 있습니다.")
            if _is_html_empty(record.resolution_note):
                raise UserError("종결 처리를 하려면 조치 내용을 먼저 작성해야 합니다.")
            record.status = "closed"
            if record.activity_ids:
                record.activity_ids.action_done()

    def action_cancel(self):
        """취소"""
        for record in self:
            if record.status in ('closed', 'canceled'):
                raise UserError("이미 종결되거나 취소된 티켓은 취소할 수 없습니다.")
            record.status = "canceled"
            if record.activity_ids:
                record.activity_ids.action_done()

    def action_reopen(self):
        """IT 담당자의 티켓 재오픈 (해결완료, 종결, 취소 건 재개)"""
        for record in self:
            if not (self.env.is_admin() or self.env.user.has_group('it_helpdesk.group_helpdesk_officer')):
                raise UserError("티켓 재오픈은 IT 담당자만 수행할 수 있습니다.")
            if record.status not in ('closed', 'resolved', 'canceled'):
                raise UserError("해결 완료, 종결 또는 취소된 티켓만 재오픈할 수 있습니다.")

            # 다음 차수 평가를 위해 현재 별점 입력값 초기화 (기존 rating_ids는 보존)
            record.sudo().write({'rating': '0', 'rating_comment': False})

            record.status = "in_progress"
            record.message_post(body="티켓이 IT 담당자에 의해 재오픈되었습니다.")

            # RC-05: 담당자에게 새 Activity 자동 스케줄링
            if record.assignee_id:
                record.activity_schedule(
                    'mail.mail_activity_data_todo',
                    summary=f"재오픈된 문의 조치: {record.title}",
                    user_id=record.assignee_id.id,
                    date_deadline=fields.Date.today()
                )

    def action_submit_rating(self):
        """요청 직원의 만족도 평가 등록 (N:1 평가 이력 누적 후 자동 종결)"""
        for record in self:
            if self.env.user != record.author_id:
                raise UserError("만족도 평가는 문의를 등록한 본인만 작성할 수 있습니다.")
            if not record.rating or record.rating == "0":
                raise UserError("만족도 별점을 1점 이상 선택해 주세요. (미평가 상태로는 제출할 수 없습니다.)")

            next_round = len(record.rating_ids) + 1
            # N:1 만족도 평가 이력 레코드 생성
            self.env['it.helpdesk.ticket.rating'].create({
                'ticket_id': record.id,
                'round': next_round,
                'rating': record.rating,
                'rating_comment': record.rating_comment,
                'author_id': self.env.user.id,
            })

            record.message_post(
                body=f"<b>직원 만족도 평가 ({next_round}차) 완료</b>: {record.rating}점<br/>"
                     f"한줄평: {record.rating_comment or '없음'}"
            )
            # 만족도 제출 시 종결(closed)로 안전하게 마무리
            record.status = "closed"

    def action_toggle_faq(self):
        """IT 담당자가 해결된 유용한 티켓을 FAQ 지식베이스로 등록/해제"""
        for record in self:
            if not (self.env.is_admin() or self.env.user.has_group('it_helpdesk.group_helpdesk_officer')):
                raise UserError("FAQ 등록 및 관리는 IT 담당자만 수행할 수 있습니다.")
            if _is_html_empty(record.resolution_note):
                raise UserError("FAQ로 등록하려면 먼저 공식 조치 내역을 작성해야 합니다.")
            record.is_faq = not record.is_faq
            msg = "<b>사내 FAQ 지식베이스로 등록되었습니다.</b> 전사 사원에게 유용한 조치 사례로 공유됩니다." if record.is_faq else "사내 FAQ 등록이 해제되었습니다."
            record.message_post(body=msg)

    @api.model
    def _cron_auto_close_resolved_tickets(self, days=7):
        """확장 2: 해결완료(resolved) 후 지정된 일수(기본 7일) 동안 추가 문의나 평가가 없는 티켓 자동 종결 스케줄러"""
        cutoff = fields.Datetime.now() - timedelta(days=days)
        tickets = self.search([
            ('status', '=', 'resolved'),
            ('write_date', '<=', cutoff),
        ])
        closed_count = 0
        for ticket in tickets:
            # 시스템 관리자 권한으로 안전하게 종결(closed) 처리 및 Chatter 기록
            ticket.sudo().write({'status': 'closed'})
            ticket.sudo().message_post(
                body=f"해결 완료 상태에서 {days}일 동안 추가 문의 또는 만족도 평가가 등록되지 않아 시스템 스케줄러에 의해 자동으로 문의가 종결되었습니다.",
                subtype_xmlid='mail.mt_note'
            )
            closed_count += 1
        return closed_count


class HelpDeskTicketRating(models.Model):
    _name = "it.helpdesk.ticket.rating"
    _description = "IT 문의 고객 만족도 평가 이력"
    _order = "round asc, id asc"

    ticket_id = fields.Many2one(
        "it.helpdesk.ticket",
        string="대상 티켓",
        required=True,
        ondelete="cascade",
        index=True,
    )
    round = fields.Integer(string="차수", default=1)
    rating = fields.Selection(
        [
            ("0", "미평가"),
            ("1", "1점 (매우 불만)"),
            ("2", "2점 (불만)"),
            ("3", "3점 (보통)"),
            ("4", "4점 (만족)"),
            ("5", "5점 (매우 만족)"),
        ],
        string="만족도",
        required=True,
    )
    rating_comment = fields.Text(string="만족도 한줄평")
    author_id = fields.Many2one(
        "res.users",
        string="평가 직원",
        default=lambda self: self.env.user,
        readonly=True,
    )
    create_date = fields.Datetime(string="평가일시", readonly=True)
