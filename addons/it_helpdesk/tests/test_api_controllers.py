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
            
            # 본인 티켓과 FAQ는 포함되어야 함
            self.assertIn(self.ticket_emp1.id, ticket_ids)
            self.assertIn(self.ticket_faq.id, ticket_ids)
            # 타인 티켓은 절대 포함되지 않아야 함 (BOLA 방어)
            self.assertNotIn(self.ticket_emp2.id, ticket_ids)

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
