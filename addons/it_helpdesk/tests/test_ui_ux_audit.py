# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase
from odoo.exceptions import UserError, AccessError


class TestHelpdeskUIUXAudit(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Ticket = cls.env['it.helpdesk.ticket']

        # 일반 사원
        cls.user_employee = cls.env['res.users'].create({
            'name': 'UI 테스트 사원',
            'login': 'test_employee_ui',
            'email': 'employee_ui@audit.com',
            'groups_id': [(6, 0, [
                cls.env.ref('base.group_user').id,
                cls.env.ref('it_helpdesk.group_helpdesk_user').id,
            ])]
        })

        # 타 사원
        cls.user_other_employee = cls.env['res.users'].create({
            'name': '타 사원',
            'login': 'test_other_employee_ui',
            'email': 'other_ui@audit.com',
            'groups_id': [(6, 0, [
                cls.env.ref('base.group_user').id,
                cls.env.ref('it_helpdesk.group_helpdesk_user').id,
            ])]
        })

        # IT 담당자
        cls.user_officer = cls.env['res.users'].create({
            'name': 'UI 테스트 담당자',
            'login': 'test_officer_ui',
            'email': 'officer_ui@audit.com',
            'groups_id': [(6, 0, [
                cls.env.ref('base.group_user').id,
                cls.env.ref('it_helpdesk.group_helpdesk_officer').id,
            ])]
        })

    def test_01_reopen_canceled_ticket_allowed(self):
        """[사용자 요청 검증] 취소(canceled)된 티켓도 IT 담당자에 의해 재오픈되어야 함"""
        ticket = self.Ticket.with_user(self.user_employee).create({
            'title': '취소 후 재오픈 테스트',
            'content': '<p>취소할 티켓</p>',
            'status': 'submitted',
        })
        # 취소 처리
        ticket.action_cancel()
        self.assertEqual(ticket.status, 'canceled')

        # IT 담당자가 재오픈 수행 -> 성공 확인
        ticket.with_user(self.user_officer).action_reopen()
        self.assertEqual(ticket.status, 'in_progress')

    def test_02_reopen_resolved_ticket_allowed(self):
        """[UI-03 검증] 해결완료(resolved)된 티켓도 IT 담당자에 의해 재오픈되어야 함"""
        ticket = self.Ticket.with_user(self.user_officer).create({
            'title': '해결 후 재오픈 테스트',
            'content': '<p>해결할 티켓</p>',
            'status': 'in_progress',
            'resolution_note': '<p>1차 조치 완료</p>',
        })
        ticket.action_resolve()
        self.assertEqual(ticket.status, 'resolved')

        # IT 담당자가 재오픈 수행 -> 성공 확인
        ticket.action_reopen()
        self.assertEqual(ticket.status, 'in_progress')

    def test_03_close_officer_only(self):
        """[UI-02 검증] 일반 사원은 종결(action_close)을 수행할 수 없음"""
        ticket = self.Ticket.with_user(self.user_officer).create({
            'title': '종결 권한 테스트',
            'content': '<p>해결된 티켓</p>',
            'status': 'resolved',
            'resolution_note': '<p>조치 완료</p>',
        })
        with self.assertRaises(UserError):
            ticket.with_user(self.user_employee).action_close()

    def test_04_cancel_author_only(self):
        """[UI-08 검증] 타 사원은 다른 직원의 티켓을 취소할 수 없음"""
        ticket = self.Ticket.with_user(self.user_employee).create({
            'title': '내 티켓',
            'content': '<p>내용</p>',
            'author_id': self.user_employee.id,
        })
        # 타 사원이 취소 시도 -> AccessError로 차단
        with self.assertRaises(AccessError):
            ticket.with_user(self.user_other_employee).write({'status': 'canceled'})

    def test_05_kanban_view_permission(self):
        """[사용자 요청 검증] 칸반 뷰는 IT 담당자(group_helpdesk_officer)에게만 그룹이 지정되어 있어야 함"""
        kanban_view = self.env.ref('it_helpdesk.view_helpdesk_ticket_kanban')
        officer_group = self.env.ref('it_helpdesk.group_helpdesk_officer')
        self.assertIn(officer_group, kanban_view.groups_id)
