# -*- coding: utf-8 -*-
from datetime import timedelta
from odoo import fields
from odoo.tests.common import TransactionCase
from odoo.exceptions import UserError, AccessError, ValidationError


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

    def test_08_form_view_buttons_and_assignee_field(self):
        """[보완 1 & 3 검증] 담당자 전용 버튼 4종의 사원 노출 차단 및 폼 뷰 담당자 이관 필드 검증"""
        # 1. 폼 뷰 XML arch 검사
        form_view = self.env.ref('it_helpdesk.view_helpdesk_ticket_form')
        arch = form_view.arch

        # 버튼 4종에 is_officer 조건이 누락 없이 들어가 있는지 확인
        self.assertIn('name="action_assign_to_me"', arch)
        self.assertIn('invisible="status != \'submitted\' or not is_officer"', arch)

        self.assertIn('name="action_start_progress"', arch)
        self.assertIn('invisible="status != \'assigned\' or not is_officer"', arch)

        self.assertIn('name="action_pending"', arch)
        self.assertIn('invisible="status != \'in_progress\' or not is_officer"', arch)

        self.assertIn('name="action_resolve"', arch)
        self.assertIn('invisible="status not in (\'in_progress\', \'pending\') or not is_officer"', arch)

        # 폼 뷰 내 assignee_name / assignee_id 조건 검사
        self.assertIn('name="assignee_name" invisible="is_officer"', arch)
        self.assertIn('name="assignee_id" invisible="not is_officer"', arch)

        # 2. IT 담당자가 폼에서 assignee_id를 다른 담당자로 수동 이관할 때 RC-06 자동 연동 검증
        # 제2의 IT 담당자 생성
        officer2 = self.env['res.users'].create({
            'name': '2차 IT 담당자',
            'login': 'test_officer2_ui',
            'email': 'officer2_ui@audit.com',
            'groups_id': [(6, 0, [
                self.env.ref('base.group_user').id,
                self.env.ref('it_helpdesk.group_helpdesk_officer').id,
            ])]
        })

        ticket = self.Ticket.with_user(self.user_employee).create({
            'title': '네트워크 접속 불가',
            'content': '<p>인터넷 연결이 끊어졌습니다.</p>',
            'author_id': self.user_employee.id,
        })
        # 1차 담당자 배정
        ticket.with_user(self.user_officer).action_assign_to_me()
        self.assertEqual(ticket.assignee_id, self.user_officer)
        self.assertEqual(len(ticket.activity_ids), 1)
        self.assertEqual(ticket.activity_ids[0].user_id, self.user_officer)

        # 1차 담당자가 2차 담당자에게 수동 이관 (write 호출)
        ticket.with_user(self.user_officer).write({'assignee_id': officer2.id})
        self.assertEqual(ticket.assignee_id, officer2)
        # 이전 활동 정리 및 새 담당자 활동 스케줄링 확인
        self.assertEqual(len(ticket.activity_ids), 1)
        self.assertEqual(ticket.activity_ids[0].user_id, officer2)

    def test_09_rec_name_and_order(self):
        """[보완 2 검증] _rec_name = 'title' 및 _order = 'id desc' 검증"""
        ticket1 = self.Ticket.with_user(self.user_employee).create({
            'title': '첫 번째 문의 티켓',
            'content': '<p>첫 번째 문의 내용입니다.</p>',
        })
        ticket2 = self.Ticket.with_user(self.user_employee).create({
            'title': '두 번째 문의 티켓',
            'content': '<p>두 번째 문의 내용입니다.</p>',
        })

        # _rec_name 및 display_name 검증 (티켓 번호 단독 표기)
        self.assertEqual(ticket1.display_name, ticket1.ticket_number)
        self.assertEqual(ticket2.display_name, ticket2.ticket_number)
        self.assertEqual(self.Ticket._rec_name, 'ticket_number')

        # _order 검증
        self.assertEqual(self.Ticket._order, 'id desc')
        tickets = self.Ticket.search([('id', 'in', [ticket1.id, ticket2.id])])
        self.assertEqual(tickets.ids, [ticket2.id, ticket1.id])

    def test_10_ticket_duplicate_resets_fields(self):
        """[보완 4 검증] 티켓 복제(copy) 시 상태, 담당자, 조치내역, 만족도, FAQ 등 초기화 검증"""
        ticket = self.Ticket.with_user(self.user_employee).create({
            'title': '윈도우 정품 인증 오류',
            'content': '<p>인증 키 만료 경고가 뜹니다.</p>',
            'category': 'sw',
            'priority': '2',
            'author_id': self.user_employee.id,
        })
        ticket.with_user(self.user_officer).action_assign_to_me()
        ticket.with_user(self.user_officer).write({
            'status': 'in_progress',
            'resolution_note': '<p>볼륨 라이선스 키 재등록 완료</p>',
            'is_faq': True,
        })
        ticket.with_user(self.user_officer).action_resolve()
        ticket.with_user(self.user_employee).write({
            'rating': '5',
            'rating_comment': '빠르게 해결되었습니다!',
        })
        ticket.with_user(self.user_employee).action_submit_rating()
        self.assertEqual(ticket.status, 'closed')
        self.assertTrue(ticket.is_faq)
        self.assertEqual(len(ticket.rating_ids), 1)

        # 복제 실행
        duplicated = ticket.copy()

        # 검증: 복사본 타이틀 및 초기화된 필드들
        self.assertEqual(duplicated.title, '윈도우 정품 인증 오류 (복사본)')
        self.assertEqual(duplicated.category, 'sw')  # 분류는 유지
        self.assertEqual(duplicated.priority, '2')  # 긴급도는 유지
        self.assertEqual(duplicated.status, 'submitted')  # 접수대기로 초기화
        self.assertFalse(duplicated.assignee_id)  # 담당자 초기화
        self.assertFalse(duplicated.resolution_note)  # 조치내역 초기화
        self.assertEqual(duplicated.rating, '0')  # 만족도 미평가로 초기화
        self.assertFalse(duplicated.rating_comment)  # 한줄평 초기화
        self.assertFalse(duplicated.is_faq)  # FAQ 초기화
        self.assertFalse(duplicated.rating_ids)  # 차수별 평가 이력 복제 방지
        # 새 deadline이 정상 계산되었는지 확인
        self.assertTrue(duplicated.deadline)

    def test_11_empty_html_content_rejected(self):
        """[보완 5 검증] 문의 상세 내용(content) 빈 줄/공백 HTML 등록 차단 검증"""
        empty_contents = [
            '',
            '   ',
            '<p><br></p>',
            '<p>&nbsp;</p>',
            '<p>&nbsp; &nbsp;</p>',
            '<div><br></div>',
            '<p></p>',
        ]

        for empty_val in empty_contents:
            with self.assertRaises(ValidationError):
                self.Ticket.with_user(self.user_employee).create({
                    'title': '내용 누락 테스트',
                    'content': empty_val,
                })

        # 유효한 본문은 정상 등록 확인
        valid_ticket = self.Ticket.with_user(self.user_employee).create({
            'title': '정상 본문 테스트',
            'content': '<p>모니터 전원이 들어오지 않습니다.</p>',
        })
        self.assertTrue(valid_ticket.id)

        # 수정 시 빈 본문으로 변경 시도 차단 확인
        with self.assertRaises(ValidationError):
            valid_ticket.with_user(self.user_employee).write({'content': '<p><br></p>'})

    def test_12_ticket_sequence_generation(self):
        """[확장 1 검증] 티켓 고유 접수번호 자동 채번 (ir.sequence) 및 display_name 연동 검증"""
        # 1. 첫 번째 티켓 생성 시 번호 채번 확인
        ticket1 = self.Ticket.with_user(self.user_employee).create({
            'title': '네트워크 포트 연결 요청',
            'content': '<p>자리 이동으로 LAN선 포트 활성화가 필요합니다.</p>',
        })
        self.assertTrue(ticket1.ticket_number)
        self.assertNotEqual(ticket1.ticket_number, 'New')
        self.assertTrue(ticket1.ticket_number.startswith('TKT-'))

        # display_name 연동 확인 (티켓 번호 단독 표기)
        self.assertEqual(ticket1.display_name, ticket1.ticket_number)

        # 2. 두 번째 티켓 생성 시 순차 증가 확인
        ticket2 = self.Ticket.with_user(self.user_employee).create({
            'title': '모니터 추가 지급 요청',
            'content': '<p>듀얼 모니터 사용을 희망합니다.</p>',
        })
        self.assertTrue(ticket2.ticket_number.startswith('TKT-'))
        self.assertNotEqual(ticket1.ticket_number, ticket2.ticket_number)

        # 3. 뷰 XML에 접수번호 필드가 배치되어 있는지 검증
        list_view = self.env.ref('it_helpdesk.view_helpdesk_ticket_list')
        self.assertIn('name="ticket_number"', list_view.arch)

        form_view = self.env.ref('it_helpdesk.view_helpdesk_ticket_form')
        self.assertIn('name="ticket_number"', form_view.arch)

        kanban_view = self.env.ref('it_helpdesk.view_helpdesk_ticket_kanban')
        self.assertIn('name="ticket_number"', kanban_view.arch)

        search_view = self.env.ref('it_helpdesk.view_helpdesk_ticket_search')
        self.assertIn('name="ticket_number"', search_view.arch)

    def test_13_cron_auto_close_resolved_tickets(self):
        """[확장 2 검증] 장기 미평가 해결 티켓 자동 종결 스케줄러 (ir.cron) 검증"""
        # 1. 7일 초과 경과된 해결완료 티켓 시뮬레이션
        ticket_old = self.Ticket.with_user(self.user_employee).create({
            'title': '오래된 해결 티켓',
            'content': '<p>오래 전에 해결된 문의입니다.</p>',
            'author_id': self.user_employee.id,
        })
        ticket_old.with_user(self.user_officer).action_assign_to_me()
        ticket_old.with_user(self.user_officer).write({
            'status': 'in_progress',
            'resolution_note': '<p>과거에 조치 완료함</p>',
        })
        ticket_old.with_user(self.user_officer).action_resolve()
        self.assertEqual(ticket_old.status, 'resolved')

        # SQL로 write_date를 8일 전으로 강제 변경하여 스케줄러 조건 생성
        past_date = fields.Datetime.now() - timedelta(days=8)
        self.env.cr.execute(
            "UPDATE it_helpdesk_ticket SET write_date = %s WHERE id = %s",
            (past_date, ticket_old.id)
        )
        ticket_old.invalidate_recordset(['write_date'])

        # 2. 최근 해결된 티켓 (1일 전) 생성
        ticket_recent = self.Ticket.with_user(self.user_employee).create({
            'title': '최근 해결 티켓',
            'content': '<p>어제 막 해결된 문의입니다.</p>',
            'author_id': self.user_employee.id,
        })
        ticket_recent.with_user(self.user_officer).action_assign_to_me()
        ticket_recent.with_user(self.user_officer).write({
            'status': 'in_progress',
            'resolution_note': '<p>방금 조치 완료함</p>',
        })
        ticket_recent.with_user(self.user_officer).action_resolve()
        self.assertEqual(ticket_recent.status, 'resolved')

        # 3. 자동 종결 크론 스케줄러 메서드 실행 (7일 기준)
        closed_count = self.Ticket._cron_auto_close_resolved_tickets(days=7)
        self.assertGreaterEqual(closed_count, 1)

        # 4. 검증: 오래된 건은 closed로 자동 전이, 최근 건은 resolved 유지
        ticket_old.invalidate_recordset(['status'])
        ticket_recent.invalidate_recordset(['status'])
        self.assertEqual(ticket_old.status, 'closed')
        self.assertEqual(ticket_recent.status, 'resolved')

        # 5. 오래된 건에 스케줄러 자동 종결 시스템 메시지가 Chatter에 남았는지 확인
        messages = ticket_old.message_ids.mapped('body')
        self.assertTrue(any('자동으로 문의가 종결되었습니다' in m for m in messages))
