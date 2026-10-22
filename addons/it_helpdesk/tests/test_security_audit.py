# -*- coding: utf-8 -*-
from datetime import timedelta
from odoo import fields
from odoo.tests.common import TransactionCase
from odoo.exceptions import UserError, ValidationError, AccessError


class TestHelpdeskSecurityAudit(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Ticket = cls.env['it.helpdesk.ticket']

        # 1. 일반 사원 유저 (group_helpdesk_user)
        cls.user_employee = cls.env['res.users'].create({
            'name': '테스트 사원',
            'login': 'test_employee_audit',
            'email': 'employee@audit.com',
            'groups_id': [(6, 0, [
                cls.env.ref('base.group_user').id,
                cls.env.ref('it_helpdesk.group_helpdesk_user').id,
            ])]
        })

        # 2. IT 담당자 유저 1 (group_helpdesk_officer)
        cls.user_officer1 = cls.env['res.users'].create({
            'name': 'IT 담당자 1',
            'login': 'test_officer1_audit',
            'email': 'officer1@audit.com',
            'groups_id': [(6, 0, [
                cls.env.ref('base.group_user').id,
                cls.env.ref('it_helpdesk.group_helpdesk_officer').id,
            ])]
        })

        # 3. IT 담당자 유저 2 (group_helpdesk_officer)
        cls.user_officer2 = cls.env['res.users'].create({
            'name': 'IT 담당자 2',
            'login': 'test_officer2_audit',
            'email': 'officer2@audit.com',
            'groups_id': [(6, 0, [
                cls.env.ref('base.group_user').id,
                cls.env.ref('it_helpdesk.group_helpdesk_officer').id,
            ])]
        })

    def test_01_kanban_write_without_resolution_note_blocked(self):
        """[RC-01 검증] 조치내용 없이 write로 resolved 시도 시 차단 및 빈 HTML 태그 방어"""
        ticket = self.Ticket.with_user(self.user_officer1).create({
            'title': '네트워크 접속 불가',
            'content': '<p>인터넷이 안 됩니다.</p>',
            'status': 'in_progress',
            'resolution_note': False,
        })

        # 1. 조치내용 False 상태에서 resolved 전이 시도 -> UserError
        with self.assertRaises(UserError):
            ticket.write({'status': 'resolved'})

        # 2. 공백 또는 빈 태그 (<p><br></p>) 상태에서 resolved 전이 시도 -> UserError
        ticket.write({'resolution_note': '<p><br></p>'})
        with self.assertRaises(UserError):
            ticket.write({'status': 'resolved'})

        # 3. 정상 조치내용 작성 후 resolved 전이 -> 성공
        ticket.write({'resolution_note': '<p>공유기 재부팅 완료</p>'})
        ticket.write({'status': 'resolved'})
        self.assertEqual(ticket.status, 'resolved')

    def test_02_normal_user_cannot_arbitrarily_change_status(self):
        """[RC-02 검증] 일반 사원이 본인 티켓을 임의로 종결/배정 처리할 수 없어야 함"""
        ticket = self.Ticket.with_user(self.user_employee).create({
            'title': '모니터 화면 깜빡임',
            'content': '<p>화면이 깜빡거립니다.</p>',
            'author_id': self.user_employee.id,
        })

        # 1. 사원이 본인 티켓을 마음대로 'closed'로 write 시도 -> AccessError
        with self.assertRaises(AccessError):
            ticket.with_user(self.user_employee).write({'status': 'closed'})

        # 2. 사원이 본인 티켓을 마음대로 'assigned'로 write 시도 -> AccessError
        with self.assertRaises(AccessError):
            ticket.with_user(self.user_employee).write({'status': 'assigned'})

        # 3. 사원이 본인 티켓을 'canceled'로 변경 -> 정상 허용
        ticket.with_user(self.user_employee).write({'status': 'canceled'})
        self.assertEqual(ticket.status, 'canceled')

    def test_03_closed_ticket_immutable_via_rpc(self):
        """[RC-03 검증] 종결(closed/canceled)된 티켓은 write()로 제목/내용 변조 불가"""
        ticket = self.Ticket.with_user(self.user_officer1).create({
            'title': '키보드 불량 문의',
            'content': '<p>스페이스바가 눌리지 않습니다.</p>',
            'status': 'closed',
            'author_id': self.user_employee.id,
            'resolution_note': '<p>키보드 교체 완료</p>',
        })

        # 1. 사원이 종결된 티켓의 제목 변조 시도 -> UserError
        with self.assertRaises(UserError):
            ticket.with_user(self.user_employee).write({'title': '키보드 및 마우스 위조 요청'})

        # 2. 담당자가 종결된 티켓의 상세 내용 변조 시도 -> UserError
        with self.assertRaises(UserError):
            ticket.with_user(self.user_officer1).write({'content': '<p>내용 변조 시도</p>'})

        # 3. 단, 사후 고객 만족도 평가는 정상 허용
        ticket.with_user(self.user_employee).write({
            'rating': '5',
            'rating_comment': '빠른 교체 감사합니다!',
        })
        self.assertEqual(ticket.rating, '5')

    def test_04_action_methods_validate_current_status(self):
        """[RC-04 검증] Public 액션 메서드 호출 시 현재 상태 검증"""
        ticket = self.Ticket.with_user(self.user_officer1).create({
            'title': '프린터 토너 교체',
            'content': '<p>토너 부족 메시지가 뜹니다.</p>',
            'status': 'submitted',
        })

        # 1. submitted 상태에서 바로 action_resolve() 시도 -> UserError
        ticket.resolution_note = '<p>조치 완료</p>'
        with self.assertRaises(UserError):
            ticket.action_resolve()

        # 2. submitted 상태에서 바로 action_pending() 시도 -> UserError
        with self.assertRaises(UserError):
            ticket.action_pending()

        # 3. 담당 접수 후 정상 플로우 진행
        ticket.action_assign_to_me()
        self.assertEqual(ticket.status, 'assigned')
        ticket.action_start_progress()
        self.assertEqual(ticket.status, 'in_progress')
        ticket.action_resolve()
        self.assertEqual(ticket.status, 'resolved')

    def test_05_reopen_and_restart_activity_and_rating_preservation(self):
        """[RC-05, RC-08 검증] 재오픈/재문의 시 Activity 재생성 및 이전 만족도 보존"""
        ticket = self.Ticket.with_user(self.user_employee).create({
            'title': 'VPN 접속 에러',
            'content': '<p>사외에서 사내망 접속 불가</p>',
            'author_id': self.user_employee.id,
        })

        # 1. 담당자 배정 및 해결 완료
        ticket.with_user(self.user_officer1).action_assign_to_me()
        self.assertEqual(len(ticket.activity_ids), 1)

        ticket.with_user(self.user_officer1).write({'resolution_note': '<p>VPN 계정 활성화</p>'})
        ticket.with_user(self.user_officer1).action_start_progress()
        ticket.with_user(self.user_officer1).action_resolve()

        # 해결 완료 시 활동 마감 확인
        self.assertEqual(len(ticket.activity_ids), 0)

        # 2. 1차 만족도 등록 (4점)
        ticket.with_user(self.user_employee).write({'rating': '4', 'rating_comment': '1차 처리 만족'})
        self.assertEqual(ticket.rating, '4')

        # 3. 담당자에 의한 티켓 재오픈
        ticket.with_user(self.user_officer1).action_reopen()
        self.assertEqual(ticket.status, 'in_progress')
        # 새 Activity 생성 확인 (RC-05)
        self.assertEqual(len(ticket.activity_ids), 1)
        self.assertEqual(ticket.activity_ids.user_id, self.user_officer1)
        # 이전 만족도 초기화 확인 (Chatter 보존 및 2차 평가 활성화) (RC-08)
        self.assertFalse(ticket.rating)
        self.assertFalse(ticket.rating_comment)

        # 4. 재해결 후 직원의 재문의(action_restart_ticket) 테스트
        ticket.with_user(self.user_officer1).action_resolve()
        self.assertEqual(ticket.status, 'resolved')
        self.assertEqual(len(ticket.activity_ids), 0)

        ticket.with_user(self.user_employee).write({'rating': '2', 'rating_comment': '다시 끊김'})
        ticket.with_user(self.user_employee).action_restart_ticket()
        self.assertEqual(ticket.status, 'in_progress')
        # 새 Activity 생성 확인
        self.assertEqual(len(ticket.activity_ids), 1)
        self.assertFalse(ticket.rating)

    def test_06_assignee_change_transfers_activity(self):
        """[RC-06 검증] 담당자 변경 시 이전 담당자 Activity 제거 및 새 담당자 스케줄링"""
        ticket = self.Ticket.with_user(self.user_officer1).create({
            'title': '서버 백업 에러',
            'content': '<p>백업 디스크 풀</p>',
        })
        ticket.action_assign_to_me()
        self.assertEqual(ticket.activity_ids.user_id, self.user_officer1)

        # 담당자를 officer2로 변경
        ticket.write({'assignee_id': self.user_officer2.id})
        # officer1의 Activity는 사라지고 officer2에게 새 Activity가 생성되어야 함
        self.assertEqual(len(ticket.activity_ids), 1)
        self.assertEqual(ticket.activity_ids.user_id, self.user_officer2)

    def test_07_sla_deadline_recalculation(self):
        """[RC-07 검증] 긴급도 변경 시 SLA 마감 기한 재산정 (변경 시각 기준)"""
        now = fields.Datetime.now()
        ticket = self.Ticket.with_user(self.user_officer1).create({
            'title': 'ERP 조회 지연',
            'content': '<p>속도가 느립니다.</p>',
            'priority': '0',  # 낮음 (72시간)
        })
        # 자동 산정 확인
        self.assertTrue(ticket.deadline > now + timedelta(hours=70))

        # '긴급'(4시간)으로 변경
        ticket.write({'priority': '3'})
        # 변경 시각 기준 4시간 뒤로 마감 기한 재설정 확인
        self.assertTrue(ticket.deadline <= fields.Datetime.now() + timedelta(hours=4, minutes=1))
        self.assertTrue(ticket.deadline >= fields.Datetime.now() + timedelta(hours=3, minutes=58))

    def test_08_empty_title_validation(self):
        """[RC-09 검증] 공백만 있는 제목 입력 차단"""
        with self.assertRaises(ValidationError):
            self.Ticket.with_user(self.user_employee).create({
                'title': '     ',
                'content': '<p>내용</p>',
            })
