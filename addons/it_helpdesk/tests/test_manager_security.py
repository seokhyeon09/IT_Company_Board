# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase
from odoo.exceptions import AccessError, UserError
from ..utils.validators import ensure_assignee_or_admin


class TestHelpdeskManagerSecurity(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Ticket = cls.env['it.helpdesk.ticket']

        # 사원 유저
        cls.user_employee = cls.env['res.users'].create({
            'name': '매니저 테스트 사원',
            'login': 'test_emp_mgr',
            'email': 'emp_mgr@audit.com',
            'groups_id': [(6, 0, [
                cls.env.ref('base.group_user').id,
                cls.env.ref('it_helpdesk.group_helpdesk_user').id,
            ])]
        })

        # 담당자 유저
        cls.user_officer = cls.env['res.users'].create({
            'name': '매니저 테스트 담당자',
            'login': 'test_off_mgr',
            'email': 'off_mgr@audit.com',
            'groups_id': [(6, 0, [
                cls.env.ref('base.group_user').id,
                cls.env.ref('it_helpdesk.group_helpdesk_officer').id,
            ])]
        })

        # 관리자 유저
        cls.user_manager = cls.env['res.users'].create({
            'name': '매니저 테스트 관리자',
            'login': 'test_mgr_user',
            'email': 'mgr_user@audit.com',
            'groups_id': [(6, 0, [
                cls.env.ref('base.group_user').id,
                cls.env.ref('it_helpdesk.group_helpdesk_manager').id,
            ])]
        })

    def test_01_manager_group_inheritance(self):
        """[Manager 권한 상속 검증] Manager 그룹은 Officer와 User 그룹을 전이적으로 자동 상속해야 함"""
        # 1. Manager 유저가 Officer 및 User 그룹 권한을 보유하는지 확인
        self.assertTrue(self.user_manager.has_group('it_helpdesk.group_helpdesk_manager'))
        self.assertTrue(self.user_manager.has_group('it_helpdesk.group_helpdesk_officer'))
        self.assertTrue(self.user_manager.has_group('it_helpdesk.group_helpdesk_user'))

        # 2. Ticket 모델의 is_officer 계산 필드가 Manager에게 True로 평가되는지 확인
        ticket = self.Ticket.with_user(self.user_manager).create({
            'title': '매니저 권한 테스트 티켓',
            'content': '<p>테스트 본문</p>',
        })
        self.assertTrue(ticket.is_officer)

    def test_02_unlink_permission_officer_blocked_manager_allowed(self):
        """[티켓 완전 삭제 권한 격리 검증] Officer는 unlink가 차단되고 Manager는 unlink가 허용되어야 함"""
        ticket1 = self.Ticket.with_user(self.user_employee).create({
            'title': '담당자 삭제 불가 테스트 티켓',
            'content': '<p>담당자는 삭제 불가</p>',
        })

        # 1. IT 담당자가 티켓 삭제 시도 -> AccessError 차단
        with self.assertRaises(AccessError):
            ticket1.with_user(self.user_officer).unlink()

        # 2. 헬프데스크 관리자가 티켓 삭제 시도 -> 정상 허용
        ticket2 = self.Ticket.with_user(self.user_employee).create({
            'title': '관리자 삭제 허용 테스트 티켓',
            'content': '<p>관리자는 삭제 가능</p>',
        })
        ticket2_id = ticket2.id
        ticket2.with_user(self.user_manager).unlink()
        self.assertFalse(self.Ticket.search([('id', '=', ticket2_id)]).exists())

    def test_03_manager_override_in_validators(self):
        """[관리자 직권 제어 검증] ensure_assignee_or_admin이 Manager에게 타인 배정 티켓도 통과시켜야 함"""
        ticket = self.Ticket.with_user(self.user_officer).create({
            'title': '타 담당자 배정 티켓',
            'content': '<p>배정 테스트</p>',
            'assignee_id': self.user_officer.id,
            'status': 'assigned',
        })

        # 다른 일반 담당자는 타인 티켓에 대해 AccessError
        other_officer = self.env['res.users'].create({
            'name': '제3의 담당자',
            'login': 'third_officer',
            'email': 'third@audit.com',
            'groups_id': [(6, 0, [self.env.ref('base.group_user').id, self.env.ref('it_helpdesk.group_helpdesk_officer').id])]
        })

        with self.assertRaises(AccessError):
            ensure_assignee_or_admin(ticket, other_officer)

        # 헬프데스크 관리자는 타인 티켓이어도 직권 제어 허용
        ensure_assignee_or_admin(ticket, self.user_manager)
