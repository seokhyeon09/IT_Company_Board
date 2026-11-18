# -*- coding: utf-8 -*-
import hmac
import hashlib
import time
from unittest.mock import MagicMock, patch

from odoo.exceptions import AccessError
from odoo.tests.common import TransactionCase

from ..controllers.main_api import ITHelpdeskAPIController
from ..controllers.ticket_export_api import TicketExportAPIController
from ..utils.security import GATEWAY_SHARED_SECRET
from ..utils.ticket_domain import build_ticket_domain


class TestTicketExport(TransactionCase):

    @classmethod
    def _make_user(cls, login, groups):
        return cls.env['res.users'].with_context(no_reset_password=True).create({
            'name': login,
            'login': login,
            'email': f'{login}@test.com',
            'groups_id': [(6, 0, [g.id for g in groups])],
        })

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Ticket = cls.env['it.helpdesk.ticket']
        cls.query_ctrl = ITHelpdeskAPIController()
        cls.export_ctrl = TicketExportAPIController()

        g_base = cls.env.ref('base.group_user')
        g_user = cls.env.ref('it_helpdesk.group_helpdesk_user')
        g_officer = cls.env.ref('it_helpdesk.group_helpdesk_officer')

        cls.employee = cls._make_user('exp_emp', [g_base, g_user])
        cls.other_emp = cls._make_user('exp_emp2', [g_base, g_user])
        cls.officer = cls._make_user('exp_off', [g_base, g_user, g_officer])

        cls.t1 = cls.Ticket.with_user(cls.employee).create({
            'title': '내보내기 HW 티켓',
            'content': '<p>프린터</p>',
            'category': 'hw',
            'priority': '2',
        })
        cls.t2 = cls.Ticket.with_user(cls.other_emp).create({
            'title': '내보내기 SW 해결 티켓',
            'content': '<p>오피스</p>',
            'category': 'sw',
            'priority': '3',
        })
        cls.t2.with_user(cls.officer).action_assign_to_me()
        cls.t2.with_user(cls.officer).action_start_progress()
        cls.t2.with_user(cls.officer).write({'resolution_note': '<p>조치 완료</p>'})
        cls.t2.with_user(cls.officer).action_resolve()

        cls.t_faq = cls.Ticket.with_user(cls.officer).create({
            'title': '내보내기 공용 FAQ',
            'content': '<p>FAQ</p>',
            'category': 'network',
            'priority': '0',
            'is_faq': True,
        })

    def _mock_request(self, user, path):
        ts = str(int(time.time()))
        uid_str = str(user.id)
        body_hash = hashlib.sha256(b'').hexdigest()
        payload = f"POST:{path}:{uid_str}:{ts}:{body_hash}".encode('utf-8')
        sig = hmac.new(GATEWAY_SHARED_SECRET.encode('utf-8'), payload, hashlib.sha256).hexdigest()

        mock_req = MagicMock()
        mock_req.httprequest.headers = {
            'X-Gateway-User-Id': uid_str,
            'X-Gateway-Timestamp': ts,
            'X-Gateway-Signature': sig,
        }
        mock_req.httprequest.method = 'POST'
        mock_req.httprequest.path = path
        mock_req.httprequest.get_data.return_value = b''
        mock_req.env = self.env
        mock_req.session.uid = None
        return mock_req

    def test_01_employee_forbidden(self):
        """일반 사원은 /api/v1/tickets/export 호출 시 AccessError로 차단된다."""
        with patch('odoo.addons.it_helpdesk.controllers.main_api.request',
                   self._mock_request(self.employee, '/api/v1/tickets/export')):
            with self.assertRaises(AccessError):
                self.export_ctrl.export_tickets()

    def test_02_export_matches_list_filters_and_fields(self):
        """export 결과는 동일 필터의 list_tickets와 건수/대상이 일치하며 first_resolved_date를 포함한다."""
        filter_cases = [
            {},
            {'category': 'hw'},
            {'status': 'resolved'},
            {'status': 'waiting'},
            {'is_faq': True},
            {'assigned_to_me': True},
            {'search': '내보내기'},
            {'sort_by': 'priority desc'},
        ]
        for params in filter_cases:
            with patch('odoo.addons.it_helpdesk.controllers.main_api.request',
                       self._mock_request(self.officer, '/api/v1/tickets/list')):
                list_res = self.query_ctrl.list_tickets(limit=100, **params)

            with patch('odoo.addons.it_helpdesk.controllers.main_api.request',
                       self._mock_request(self.officer, '/api/v1/tickets/export')):
                exp_res = self.export_ctrl.export_tickets(**params)

            self.assertEqual(exp_res['total'], list_res['total'])
            # 목록은 limit=100이므로 라이브 DB의 데이터가 100건을 넘어도 같은 순서의 앞부분이 일치하는지 본다.
            list_ids = [t['id'] for t in list_res['data']]
            self.assertEqual([t['id'] for t in exp_res['data']][:len(list_ids)], list_ids)
            self.assertGreaterEqual(len(exp_res['data']), len(list_ids))

        # resolved 티켓의 first_resolved_date 및 author_id [id, name] 확인
        with patch('odoo.addons.it_helpdesk.controllers.main_api.request',
                   self._mock_request(self.officer, '/api/v1/tickets/export')):
            res = self.export_ctrl.export_tickets(status='resolved')
        row = next(r for r in res['data'] if r['id'] == self.t2.id)
        self.assertTrue(row['first_resolved_date'].endswith('Z'))
        self.assertEqual(row['author_id'][0], self.other_emp.id)
        self.assertEqual(row['author_id'][1], self.other_emp.name)

    def test_03_build_ticket_domain_preserves_employee_and_faq_rules(self):
        """build_ticket_domain이 사원 격리 및 FAQ 필터 동작을 유지한다."""
        dom_emp = build_ticket_domain(self.employee)
        ids_emp = self.Ticket.with_user(self.employee).search(dom_emp).ids
        self.assertIn(self.t1.id, ids_emp)
        self.assertNotIn(self.t2.id, ids_emp)
        self.assertNotIn(self.t_faq.id, ids_emp)

        dom_faq = build_ticket_domain(self.employee, is_faq=True)
        ids_faq = self.Ticket.with_user(self.employee).search(dom_faq).ids
        self.assertIn(self.t_faq.id, ids_faq)
        self.assertNotIn(self.t1.id, ids_faq)

        with patch('odoo.addons.it_helpdesk.controllers.main_api.request',
                   self._mock_request(self.officer, '/api/v1/tickets/export')):
            limited = self.export_ctrl.export_tickets(limit=1)
        self.assertEqual(len(limited['data']), 1)
        self.assertGreaterEqual(limited['total'], 3)
