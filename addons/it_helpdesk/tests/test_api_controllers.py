# -*- coding: utf-8 -*-
import time
import hmac
import hashlib
from datetime import datetime, timezone
from odoo.tests.common import TransactionCase
from odoo.exceptions import AccessError, UserError
from ..controllers.main_api import ITHelpdeskAPIController, GATEWAY_SHARED_SECRET, ConcurrencyError


class TestHelpdeskAPIController(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.controller = ITHelpdeskAPIController()

        cls.group_user = cls.env.ref('it_helpdesk.group_helpdesk_user')
        cls.group_officer = cls.env.ref('it_helpdesk.group_helpdesk_officer')

        cls.user_employee = cls.env['res.users'].create({
            'name': 'API 사원 1',
            'login': 'api_emp1',
            'email': 'api_emp1@test.com',
            'groups_id': [(6, 0, [cls.group_user.id])],
        })

        cls.user_other_employee = cls.env['res.users'].create({
            'name': 'API 사원 2',
            'login': 'api_emp2',
            'email': 'api_emp2@test.com',
            'groups_id': [(6, 0, [cls.group_user.id])],
        })

        cls.user_officer = cls.env['res.users'].create({
            'name': 'API 담당자',
            'login': 'api_officer',
            'email': 'api_officer@test.com',
            'groups_id': [(6, 0, [cls.group_officer.id])],
        })

        cls.ticket_emp1 = cls.env['it.helpdesk.ticket'].with_user(cls.user_employee).create({
            'title': '사원1 문의',
            'category': 'hw',
            'content': '<p>사원 1 문의 내용</p>',
            'priority': '1',
        })

        cls.ticket_emp2 = cls.env['it.helpdesk.ticket'].with_user(cls.user_other_employee).create({
            'title': '사원2 비밀 문의',
            'category': 'sw',
            'content': '<p>사원 2 문의 내용</p>',
            'priority': '2',
        })

        cls.ticket_faq = cls.env['it.helpdesk.ticket'].with_user(cls.user_officer).create({
            'title': '사내 공용 FAQ',
            'category': 'network',
            'content': '<p>FAQ 공지 내용</p>',
            'priority': '0',
            'is_faq': True,
        })

    def _generate_hmac_headers(self, user_id, method='POST', path='/api/v1/tickets/list', body=b''):
        ts = str(int(time.time()))
        uid_str = str(user_id)
        body_hash = hashlib.sha256(body).hexdigest()
        payload = f"{method.upper()}:{path}:{uid_str}:{ts}:{body_hash}".encode('utf-8')
        sig = hmac.new(GATEWAY_SHARED_SECRET.encode('utf-8'), payload, hashlib.sha256).hexdigest()
        return {
            'X-Gateway-User-Id': uid_str,
            'X-Gateway-Timestamp': ts,
            'X-Gateway-Signature': sig,
        }

    def test_01_employee_ticket_isolation_and_faq(self):
        """일반 사원은 자신의 티켓 및 FAQ만 조회되어야 함 (타인 티켓 차단)"""
        headers = self._generate_hmac_headers(self.user_employee.id, path='/api/v1/tickets/list')
        
        from unittest.mock import patch, MagicMock
        mock_req = MagicMock()
        mock_req.httprequest.headers = headers
        mock_req.httprequest.method = 'POST'
        mock_req.httprequest.path = '/api/v1/tickets/list'
        mock_req.httprequest.get_data.return_value = b''
        mock_req.env = self.env
        mock_req.session.uid = None

        with patch('odoo.addons.it_helpdesk.controllers.main_api.request', mock_req):
            res = self.controller.list_tickets()
            self.assertEqual(res['status'], 'success')
            ticket_ids = [t['id'] for t in res['data']]
            
            # 9단계 사원 문의-FAQ 목록 격리: 일반 목록에서는 본인 티켓만 노출 (타인 FAQ 합산 차단)
            self.assertIn(self.ticket_emp1.id, ticket_ids)
            self.assertNotIn(self.ticket_faq.id, ticket_ids)
            # 타인 티켓은 절대 포함되지 않아야 함 (BOLA 방어)
            self.assertNotIn(self.ticket_emp2.id, ticket_ids)

            # FAQ 탭 요청 시에는 FAQ 티켓이 정상 조회됨
            res_faq = self.controller.list_tickets(is_faq=True)
            self.assertEqual(res_faq['status'], 'success')
            faq_ids = [t['id'] for t in res_faq['data']]
            self.assertIn(self.ticket_faq.id, faq_ids)

    def test_02_officer_sees_all_tickets(self):
        """IT 담당자는 모든 티켓을 조회할 수 있어야 함"""
        headers = self._generate_hmac_headers(self.user_officer.id, path='/api/v1/tickets/list')

        from unittest.mock import patch, MagicMock
        mock_req = MagicMock()
        mock_req.httprequest.headers = headers
        mock_req.httprequest.method = 'POST'
        mock_req.httprequest.path = '/api/v1/tickets/list'
        mock_req.httprequest.get_data.return_value = b''
        mock_req.env = self.env
        mock_req.session.uid = None

        with patch('odoo.addons.it_helpdesk.controllers.main_api.request', mock_req):
            res = self.controller.list_tickets()
            self.assertEqual(res['status'], 'success')
            ticket_ids = [t['id'] for t in res['data']]
            
            self.assertIn(self.ticket_emp1.id, ticket_ids)
            self.assertIn(self.ticket_emp2.id, ticket_ids)
            self.assertIn(self.ticket_faq.id, ticket_ids)

    def test_03_create_ticket_with_priority_and_sla(self):
        """티켓 생성 시 우선순위 강제 형변환 및 SLA 정상 산정 검증"""
        headers = self._generate_hmac_headers(self.user_employee.id, path='/api/v1/tickets/create')

        from unittest.mock import patch, MagicMock
        mock_req = MagicMock()
        mock_req.httprequest.headers = headers
        mock_req.httprequest.method = 'POST'
        mock_req.httprequest.path = '/api/v1/tickets/create'
        mock_req.httprequest.get_data.return_value = b''
        mock_req.env = self.env
        mock_req.session.uid = None

        with patch('odoo.addons.it_helpdesk.controllers.main_api.request', mock_req):
            res = self.controller.create_ticket(
                title='신규 API 테스트 티켓',
                category='sw',
                content='<p>상세 내용입니다</p>',
                priority='3', # 긴급: 4시간
            )
            self.assertEqual(res['status'], 'success')
            self.assertEqual(res['data']['status'], 'submitted')
            self.assertEqual(res['data']['priority'], '3')
            self.assertTrue(res['data']['deadline'].endswith('Z'))

    def test_04_optimistic_concurrency_control(self):
        """조치 완료 시 write_date가 일치하지 않으면 ConcurrencyError 발생 검증"""
        headers = self._generate_hmac_headers(self.user_officer.id, path='/api/v1/tickets/resolve')

        from unittest.mock import patch, MagicMock
        mock_req = MagicMock()
        mock_req.httprequest.headers = headers
        mock_req.httprequest.method = 'POST'
        mock_req.httprequest.path = '/api/v1/tickets/resolve'
        mock_req.httprequest.get_data.return_value = b''
        mock_req.env = self.env
        mock_req.session.uid = None

        with patch('odoo.addons.it_helpdesk.controllers.main_api.request', mock_req):
            # 과거의 임의 시간 전달 -> 충돌 에러
            with self.assertRaises(ConcurrencyError):
                self.controller.resolve_ticket(
                    ticket_id=self.ticket_emp1.id,
                    resolution_note='<p>해결 완료</p>',
                    if_match_write_date='2020-01-01T00:00:00Z'
                )

    def test_05_ticket_rating_and_close(self):
        """해결 완료된 티켓에 대해 본인 평가 제출 시 closed 상태로 자동 전이 검증"""
        from unittest.mock import patch, MagicMock

        # 1. 먼저 담당자가 해결 완료
        h_resolve = self._generate_hmac_headers(self.user_officer.id, path='/api/v1/tickets/resolve')
        mock_req_officer = MagicMock()
        mock_req_officer.httprequest.headers = h_resolve
        mock_req_officer.httprequest.method = 'POST'
        mock_req_officer.httprequest.path = '/api/v1/tickets/resolve'
        mock_req_officer.httprequest.get_data.return_value = b''
        mock_req_officer.env = self.env
        mock_req_officer.session.uid = None

        with patch('odoo.addons.it_helpdesk.controllers.main_api.request', mock_req_officer):
            self.controller.resolve_ticket(
                ticket_id=self.ticket_emp1.id,
                resolution_note='<p>점검 및 해결 완료</p>'
            )

        # 2. 사원 본인이 만족도 평가 제출 -> closed 전이 확인
        h_rate = self._generate_hmac_headers(self.user_employee.id, path='/api/v1/tickets/rate')
        mock_req_emp = MagicMock()
        mock_req_emp.httprequest.headers = h_rate
        mock_req_emp.httprequest.method = 'POST'
        mock_req_emp.httprequest.path = '/api/v1/tickets/rate'
        mock_req_emp.httprequest.get_data.return_value = b''
        mock_req_emp.env = self.env
        mock_req_emp.session.uid = None

        with patch('odoo.addons.it_helpdesk.controllers.main_api.request', mock_req_emp):
            res = self.controller.rate_ticket(
                ticket_id=self.ticket_emp1.id,
                rating='5',
                rating_comment='친절한 조치 감사합니다.'
            )
            self.assertEqual(res['status'], 'success')
            self.assertEqual(res['data']['status'], 'closed')
            self.assertEqual(res['data']['rating'], '5')
            self.assertEqual(res['data']['rating_comment'], '친절한 조치 감사합니다.')

    def test_06_toggle_faq(self):
        """IT 담당자가 해결된 티켓을 FAQ로 등록/해제 토글 검증"""
        from unittest.mock import patch, MagicMock

        # FAQ 등록을 위해 조치 내역 설정
        self.ticket_emp1.sudo().write({'resolution_note': '<p>공식 조치 완료 내용</p>'})

        headers = self._generate_hmac_headers(self.user_officer.id, path='/api/v1/tickets/toggle-faq')
        mock_req = MagicMock()
        mock_req.httprequest.headers = headers
        mock_req.httprequest.method = 'POST'
        mock_req.httprequest.path = '/api/v1/tickets/toggle-faq'
        mock_req.httprequest.get_data.return_value = b''
        mock_req.env = self.env
        mock_req.session.uid = None

        with patch('odoo.addons.it_helpdesk.controllers.main_api.request', mock_req):
            initial_faq = self.ticket_emp1.is_faq
            res = self.controller.toggle_faq(ticket_id=self.ticket_emp1.id)
            self.assertEqual(res['status'], 'success')
            self.assertNotEqual(res['data']['is_faq'], initial_faq)

    def test_07_workflow_state_transitions(self):
        """IT 담당자 단계별 상태 제어 (assign -> start-progress -> pending -> close) 검증"""
        from unittest.mock import patch, MagicMock

        # 신규 접수 티켓 생성
        ticket = self.env['it.helpdesk.ticket'].with_user(self.user_employee).create({
            'title': '워크플로우 테스트 티켓',
            'category': 'sw',
            'content': '<p>상태 전이 검증용</p>',
            'priority': '1',
        })
        self.assertEqual(ticket.status, 'submitted')

        # 1. 담당자 내게 배정 (assign)
        h_assign = self._generate_hmac_headers(self.user_officer.id, path='/api/v1/tickets/assign')
        mock_req = MagicMock()
        mock_req.httprequest.headers = h_assign
        mock_req.httprequest.method = 'POST'
        mock_req.httprequest.path = '/api/v1/tickets/assign'
        mock_req.httprequest.get_data.return_value = b''
        mock_req.env = self.env
        mock_req.session.uid = None

        with patch('odoo.addons.it_helpdesk.controllers.main_api.request', mock_req):
            res = self.controller.assign_ticket(ticket_id=ticket.id)
            self.assertEqual(res['status'], 'success')
            self.assertEqual(res['data']['status'], 'assigned')
            self.assertEqual(res['data']['assignee_id'], self.user_officer.id)

        # 2. 처리 시작 (start-progress)
        h_start = self._generate_hmac_headers(self.user_officer.id, path='/api/v1/tickets/start-progress')
        mock_req.httprequest.headers = h_start
        mock_req.httprequest.path = '/api/v1/tickets/start-progress'

        with patch('odoo.addons.it_helpdesk.controllers.main_api.request', mock_req):
            res = self.controller.start_progress_ticket(ticket_id=ticket.id)
            self.assertEqual(res['status'], 'success')
            self.assertEqual(res['data']['status'], 'in_progress')

        # 3. 답변 대기 요청 (pending)
        h_pending = self._generate_hmac_headers(self.user_officer.id, path='/api/v1/tickets/pending')
        mock_req.httprequest.headers = h_pending
        mock_req.httprequest.path = '/api/v1/tickets/pending'

        with patch('odoo.addons.it_helpdesk.controllers.main_api.request', mock_req):
            res = self.controller.pending_ticket(ticket_id=ticket.id)
            self.assertEqual(res['status'], 'success')
            self.assertEqual(res['data']['status'], 'pending')

        # 4. 다시 처리 시작 후 직권 종결 (close)
        with patch('odoo.addons.it_helpdesk.controllers.main_api.request', mock_req):
            self.controller.start_progress_ticket(ticket_id=ticket.id)

        h_close = self._generate_hmac_headers(self.user_officer.id, path='/api/v1/tickets/close')
        mock_req.httprequest.headers = h_close
        mock_req.httprequest.path = '/api/v1/tickets/close'

        with patch('odoo.addons.it_helpdesk.controllers.main_api.request', mock_req):
            res = self.controller.close_ticket(ticket_id=ticket.id, note='직권 종결 처리 사유 작성')
            self.assertEqual(res['status'], 'success')
            self.assertEqual(res['data']['status'], 'closed')

    def test_08_cancel_ticket(self):
        """요청 직원의 본인 티켓 취소(cancel) 및 상태 전이 검증"""
        from unittest.mock import patch, MagicMock

        # 사원 문의 티켓 생성
        ticket = self.env['it.helpdesk.ticket'].with_user(self.user_employee).create({
            'title': '취소 대상 티켓',
            'category': 'hw',
            'content': '<p>취소할 문의 내용</p>',
            'priority': '0',
        })
        self.assertEqual(ticket.status, 'submitted')

        # 사원 본인의 취소 요청
        h_cancel = self._generate_hmac_headers(self.user_employee.id, path='/api/v1/tickets/cancel')
        mock_req = MagicMock()
        mock_req.httprequest.headers = h_cancel
        mock_req.httprequest.method = 'POST'
        mock_req.httprequest.path = '/api/v1/tickets/cancel'
        mock_req.httprequest.get_data.return_value = b''
        mock_req.env = self.env
        mock_req.session.uid = None

        with patch('odoo.addons.it_helpdesk.controllers.main_api.request', mock_req):
            res = self.controller.cancel_ticket(ticket_id=ticket.id, reason='단순 변심으로 인한 취소')
            self.assertEqual(res['status'], 'success')
            self.assertEqual(res['data']['status'], 'canceled')
            self.assertEqual(ticket.status, 'canceled')
