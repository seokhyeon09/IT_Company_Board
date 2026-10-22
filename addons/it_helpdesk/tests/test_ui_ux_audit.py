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
        """[사용자 요청 검증] 사원 게시판 액션에서 kanban/graph/pivot 제거 (list,form 전용), 칸반 메뉴는 담당자 전용 분리"""
        officer_group = self.env.ref('it_helpdesk.group_helpdesk_officer')

        # 1. 일반 사원용 게시판 액션 3종 검증: view_mode가 오직 'list,form'만 허용되어야 함
        action_all = self.env.ref('it_helpdesk.action_helpdesk_ticket')
        action_my = self.env.ref('it_helpdesk.action_helpdesk_ticket_my')
        action_faq = self.env.ref('it_helpdesk.action_helpdesk_ticket_faq')

        for action in (action_all, action_my, action_faq):
            modes = [m.strip() for m in action.view_mode.split(',')]
            self.assertEqual(modes, ['list', 'form'], f"{action.name} 액션에 불필요한 뷰 모드가 포함되어 있습니다: {action.view_mode}")
            self.assertNotIn('kanban', modes)
            self.assertNotIn('graph', modes)
            self.assertNotIn('pivot', modes)

        # 2. 담당자 전용 업무 액션 및 메뉴 검증
        action_kanban = self.env.ref('it_helpdesk.action_helpdesk_ticket_kanban_officer')
        self.assertIn('kanban', action_kanban.view_mode.split(','))
        menu_kanban = self.env.ref('it_helpdesk.menu_helpdesk_ticket_kanban_officer')
        self.assertIn(officer_group, menu_kanban.groups_id)

        menu_unassigned = self.env.ref('it_helpdesk.menu_helpdesk_ticket_unassigned')
        self.assertIn(officer_group, menu_unassigned.groups_id)

        menu_analysis = self.env.ref('it_helpdesk.menu_helpdesk_ticket_analysis')
        self.assertIn(officer_group, menu_analysis.groups_id)

    def test_06_reopen_accumulates_rating_history(self):
        """[사용자 요청 검증] 재문의 및 재해결 시 N:1 만족도 평가 이력이 차수별(1차, 2차...)로 누적되어야 함"""
        ticket = self.Ticket.with_user(self.user_employee).create({
            'title': '프린터 출력 오류',
            'content': '<p>인쇄가 안 됩니다.</p>',
            'author_id': self.user_employee.id,
        })
        # 1. 담당자 배정 및 1차 해결
        ticket.with_user(self.user_officer).action_assign_to_me()
        ticket.with_user(self.user_officer).write({
            'status': 'in_progress',
            'resolution_note': '<p>드라이버 재설치</p>',
        })
        ticket.with_user(self.user_officer).action_resolve()
        self.assertEqual(ticket.status, 'resolved')

        # 2. 직원의 1차 만족도 제출 (3점)
        ticket.with_user(self.user_employee).write({
            'rating': '3',
            'rating_comment': '인쇄는 되는데 컬러가 안 나옵니다.',
        })
        ticket.with_user(self.user_employee).action_submit_rating()
        self.assertEqual(ticket.status, 'closed')
        # 1차 평가 레코드 생성 확인
        self.assertEqual(len(ticket.rating_ids), 1)
        self.assertEqual(ticket.rating_ids[0].round, 1)
        self.assertEqual(ticket.rating_ids[0].rating, '3')

        # 3. 직원의 추가 문의 (재문의)
        ticket.with_user(self.user_employee).action_restart_ticket()
        self.assertEqual(ticket.status, 'in_progress')
        # 기존 평가 이력(1차)은 그대로 보존되어 있어야 함
        self.assertEqual(len(ticket.rating_ids), 1)

        # 4. 담당자의 2차 조치 및 해결
        ticket.with_user(self.user_officer).write({'resolution_note': '<p>컬러 토너 카트리지 교체 완료</p>'})
        ticket.with_user(self.user_officer).action_resolve()
        self.assertEqual(ticket.status, 'resolved')

        # 5. 직원의 2차 만족도 제출 (5점)
        ticket.with_user(self.user_employee).write({
            'rating': '5',
            'rating_comment': '컬러도 아주 선명하게 잘 나옵니다! 완벽합니다.',
        })
        ticket.with_user(self.user_employee).action_submit_rating()
        self.assertEqual(ticket.status, 'closed')

        # 6. N:1 평가 이력이 2건으로 늘어났는지 검증
        self.assertEqual(len(ticket.rating_ids), 2)
        ratings = ticket.rating_ids.sorted('round')
        self.assertEqual(ratings[0].round, 1)
        self.assertEqual(ratings[0].rating, '3')
        self.assertEqual(ratings[1].round, 2)
        self.assertEqual(ratings[1].rating, '5')

    def test_07_rating_author_only_and_list_readonly(self):
        """[사용자 요청 검증] 만족도는 작성자만 수정 가능하고, 게시판 목록에서는 readonly="1" 잠금"""
        # 1. 게시판(List) 뷰에서 priority 및 rating 필드가 readonly="1"로 잠겨 있는지 확인
        list_view = self.env.ref('it_helpdesk.view_helpdesk_ticket_list')
        arch = list_view.arch
        self.assertIn('name="priority" widget="priority" readonly="1"', arch)
        self.assertIn('name="rating" widget="priority" string="만족도" optional="show" readonly="1"', arch)

        # 2. 티켓 생성 (user_employee)
        ticket = self.Ticket.with_user(self.user_employee).create({
            'title': '모니터 화면 깜빡임',
            'content': '<p>화면이 깜빡거립니다.</p>',
            'author_id': self.user_employee.id,
        })
        ticket.with_user(self.user_officer).action_assign_to_me()
        ticket.with_user(self.user_officer).write({
            'status': 'in_progress',
            'resolution_note': '<p>HDMI 케이블 재연결</p>',
        })
        ticket.with_user(self.user_officer).action_resolve()

        # 3. 타인(다른 사원)이 만족도 별점을 수정하려고 하면 AccessError 차단
        with self.assertRaises(AccessError):
            ticket.with_user(self.user_other_employee).write({'rating': '5'})

        # 4. IT 담당자라 하더라도 게시글 작성자가 아니면 만족도 별점을 대리 조작할 수 없어야 함 (AccessError)
        with self.assertRaises(AccessError):
            ticket.with_user(self.user_officer).write({'rating': '5'})

        # 5. 작성자 본인은 정상적으로 별점 및 한줄평 작성 가능
        ticket.with_user(self.user_employee).write({
            'rating': '5',
            'rating_comment': '선명하게 잘 나옵니다.',
        })
        self.assertEqual(ticket.rating, '5')

        # 6. rating 기본값 '0'(미평가) 확인 및 0점 제출 시 UserError 차단 검증
        ticket2 = self.Ticket.with_user(self.user_employee).create({
            'title': '마우스 고장',
            'content': '<p>클릭이 안 됩니다.</p>',
            'author_id': self.user_employee.id,
        })
        self.assertEqual(ticket2.rating, '0')

        ticket2.with_user(self.user_officer).action_assign_to_me()
        ticket2.with_user(self.user_officer).write({
            'status': 'in_progress',
            'resolution_note': '<p>새 마우스 지급</p>',
        })
        ticket2.with_user(self.user_officer).action_resolve()

        # 미평가('0') 상태에서 제출 시도 시 차단 확인
        with self.assertRaises(UserError):
            ticket2.with_user(self.user_employee).action_submit_rating()

        # 1점 선택 후 정상 제출 확인
        ticket2.with_user(self.user_employee).write({'rating': '1'})
        ticket2.with_user(self.user_employee).action_submit_rating()
        self.assertEqual(ticket2.status, 'closed')
