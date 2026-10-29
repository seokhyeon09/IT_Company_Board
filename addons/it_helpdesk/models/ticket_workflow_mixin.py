# -*- coding: utf-8 -*-
from datetime import timedelta
from odoo import models, fields, api
from odoo.exceptions import UserError, AccessError
from ..utils.text_utils import is_html_empty

class HelpDeskTicketWorkflowMixin(models.AbstractModel):
    _name = "it.helpdesk.ticket.workflow.mixin"
    _description = "IT Helpdesk Ticket Workflow Transition Mixin"

    def action_assign_to_user(self, target_user):
        """IT 담당자 지정 배정"""
        for record in self:
            if record.status in ('resolved', 'closed', 'canceled'):
                raise UserError("이미 완료되거나 종결된 티켓은 담당자를 배정할 수 없습니다.")
            record.assignee_id = target_user
            if record.status == 'submitted':
                record.status = 'assigned'
            todo_type = self.env.ref('mail.mail_activity_data_todo', raise_if_not_found=False)
            if todo_type and record.activity_ids:
                record.activity_ids.filtered(lambda a: a.activity_type_id == todo_type).unlink()
            record.activity_schedule(
                'mail.mail_activity_data_todo',
                summary=f"IT 문의 조치 배정: {record.title}",
                user_id=record.assignee_id.id,
                date_deadline=record.deadline.date() if record.deadline else fields.Date.today()
            )

    def action_assign_to_me(self):
        """IT 담당자 본인 배정"""
        return self.action_assign_to_user(self.env.user)

    def action_start_progress(self):
        """처리 중으로 변경"""
        for record in self:
            if record.status not in ('assigned', 'pending'):
                raise UserError("담당자가 배정되었거나 답변 대기 상태인 티켓만 처리 중으로 변경할 수 있습니다.")
            record.status = "in_progress"

    def action_pending(self):
        """답변 대기로 변경"""
        for record in self:
            if record.status != 'in_progress':
                raise UserError("처리 중인 티켓만 답변 대기 상태로 변경할 수 있습니다.")
            record.status = "pending"

    def action_restart_ticket(self):
        """직원의 추가 문의 (답변대기 회신 또는 해결완료 건 재문의)"""
        for record in self:
            is_officer = self.env.is_admin() or self.env.user.has_group('it_helpdesk.group_helpdesk_officer')
            if record.author_id != self.env.user and not is_officer:
                raise UserError("추가 문의는 문의를 등록한 본인만 요청할 수 있습니다.")
            if record.status not in ('pending', 'resolved'):
                raise UserError("답변 대기 또는 해결 완료된 티켓에 대해서만 추가 문의를 진행할 수 있습니다. (종결된 티켓은 재문의 불가)")

            was_pending = record.status == 'pending'

            # 다음 차수 평가를 위해 현재 별점 입력값 초기화
            record.sudo().write({'rating': '0', 'rating_comment': False})

            record.status = "in_progress"
            if was_pending:
                record.message_post(body="요청 직원이 답변 대기 요청에 대해 회신을 등록하여 처리가 다시 진행됩니다.")
            else:
                record.message_post(body="요청 직원이 추가 문의(재문의)를 등록하여 처리가 다시 진행됩니다.")

            if record.assignee_id:
                record.activity_schedule(
                    'mail.mail_activity_data_todo',
                    summary=f"직원 답변 대기 회신 확인 필요: {record.title}" if was_pending else f"직원 재문의 확인 필요: {record.title}",
                    user_id=record.assignee_id.id,
                    date_deadline=fields.Date.today()
                )

    def action_resolve(self):
        """해결 완료"""
        now = fields.Datetime.now()
        for record in self:
            if record.status not in ('in_progress', 'pending'):
                raise UserError("처리 중이거나 답변 대기 상태인 티켓만 해결 완료 처리할 수 있습니다.")
            if is_html_empty(record.resolution_note):
                raise UserError("해결 완료 처리를 하려면 조치 내용을 먼저 작성해야 합니다.")
            if not record.first_resolved_date:
                record.first_resolved_date = now
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
            if is_html_empty(record.resolution_note):
                raise UserError("종결 처리를 하려면 조치 내용을 먼저 작성해야 합니다.")
            record.status = "closed"
            if record.activity_ids:
                record.activity_ids.action_done()

    def action_cancel(self):
        """취소 (본인 티켓이거나 IT 담당자/관리자만 가능)"""
        is_officer = self.env.is_admin() or self.env.user.has_group('it_helpdesk.group_helpdesk_officer')
        for record in self:
            if not is_officer and not self.env.su and record.author_id != self.env.user:
                raise AccessError("본인이 작성한 문의 티켓만 취소할 수 있습니다.")
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

            record.sudo().write({'rating': '0', 'rating_comment': False})
            record.status = "in_progress"
            record.message_post(body="티켓이 IT 담당자에 의해 재오픈되었습니다.")

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
            if record.status != 'resolved':
                raise UserError("해결 완료(resolved) 상태의 티켓만 만족도를 평가하고 종결할 수 있습니다.")
            if not record.rating or record.rating == "0":
                raise UserError("만족도 별점을 1점 이상 선택해 주세요. (미평가 상태로는 제출할 수 없습니다.)")

            next_round = len(record.rating_ids) + 1
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
            record.status = "closed"

    def action_toggle_faq(self):
        """IT 담당자가 해결된 유용한 티켓을 FAQ 지식베이스로 등록/해제"""
        for record in self:
            if not (self.env.is_admin() or self.env.user.has_group('it_helpdesk.group_helpdesk_officer')):
                raise UserError("FAQ 등록 및 관리는 IT 담당자만 수행할 수 있습니다.")
            if is_html_empty(record.resolution_note):
                raise UserError("FAQ로 등록하려면 먼저 공식 조치 내역을 작성해야 합니다.")
            record.is_faq = not record.is_faq
            msg = "<b>사내 FAQ 지식베이스로 등록되었습니다.</b> 전사 사원에게 유용한 조치 사례로 공유됩니다." if record.is_faq else "사내 FAQ 등록이 해제되었습니다."
            record.message_post(body=msg)

    @api.model
    def _cron_auto_close_resolved_tickets(self, days=7):
        """해결완료(resolved) 후 지정된 일수 동안 추가 문의나 평가가 없는 티켓 자동 종결 스케줄러"""
        cutoff = fields.Datetime.now() - timedelta(days=days)
        tickets = self.search([
            ('status', '=', 'resolved'),
            ('write_date', '<=', cutoff),
        ])
        closed_count = 0
        for ticket in tickets:
            try:
                with self.env.cr.savepoint():
                    ticket.sudo().write({'status': 'closed'})
                    ticket.sudo().message_post(
                        body=f"해결 완료 상태에서 {days}일 동안 추가 문의 또는 만족도 평가가 등록되지 않아 시스템 스케줄러에 의해 자동으로 문의가 종결되었습니다.",
                        subtype_xmlid='mail.mt_note'
                    )
                    closed_count += 1
            except Exception as e:
                import logging
                logging.getLogger(__name__).warning("Failed to auto-close ticket ID %s: %s", ticket.id, e)
        return closed_count
