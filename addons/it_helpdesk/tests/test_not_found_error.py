# -*- coding: utf-8 -*-
"""NotFoundError 예외 클래스 및 단건/일괄 API 동작 검증 테스트."""
import hmac
import hashlib
import time
from unittest.mock import MagicMock, patch

from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase

from ..controllers.ticket_bulk_api import TicketBulkAPIController
from ..controllers.ticket_workflow_api import TicketWorkflowAPIController
from ..utils import NotFoundError
from ..utils.security import GATEWAY_SHARED_SECRET


class TestNotFoundError(TransactionCase):

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
        g_base = cls.env.ref('base.group_user')
        g_user = cls.env.ref('it_helpdesk.group_helpdesk_user')
        g_officer = cls.env.ref('it_helpdesk.group_helpdesk_officer')

        cls.officer = cls._make_user('nf_officer', [g_base, g_user, g_officer])
        cls.wf_ctrl = TicketWorkflowAPIController()
        cls.bulk_ctrl = TicketBulkAPIController()

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

    def test_01_not_found_error_inherits_user_error(self):
        """NotFoundError는 UserError의 하위 클래스여야 한다."""
        self.assertTrue(issubclass(NotFoundError, UserError))
        err = NotFoundError("문의를 찾을 수 없습니다.")
        self.assertIsInstance(err, UserError)
        self.assertEqual(str(err), "문의를 찾을 수 없습니다.")

    def test_02_single_workflow_endpoints_raise_not_found_error(self):
        """존재하지 않는 티켓 ID로 단건 assign/close/start-progress 호출 시 NotFoundError가 발생한다."""
        missing_id = 99999999

        with patch('odoo.addons.it_helpdesk.controllers.main_api.request',
                   self._mock_request(self.officer, '/api/v1/tickets/assign')):
            with self.assertRaises(NotFoundError) as ctx_assign:
                self.wf_ctrl.assign_ticket(ticket_id=missing_id, assignee_id=self.officer.id)
        self.assertEqual(str(ctx_assign.exception), "문의를 찾을 수 없습니다.")

        with patch('odoo.addons.it_helpdesk.controllers.main_api.request',
                   self._mock_request(self.officer, '/api/v1/tickets/close')):
            with self.assertRaises(NotFoundError) as ctx_close:
                self.wf_ctrl.close_ticket(ticket_id=missing_id)
        self.assertEqual(str(ctx_close.exception), "문의를 찾을 수 없습니다.")

        with patch('odoo.addons.it_helpdesk.controllers.main_api.request',
                   self._mock_request(self.officer, '/api/v1/tickets/start-progress')):
            with self.assertRaises(NotFoundError) as ctx_start:
                self.wf_ctrl.start_progress_ticket(ticket_id=missing_id)
        self.assertEqual(str(ctx_start.exception), "문의를 찾을 수 없습니다.")

    def test_03_bulk_action_records_missing_ticket_without_raising(self):
        """일괄 처리(bulk)는 존재하지 않는 티켓 ID에서 예외를 던지지 않고 실패 건으로 기록한다."""
        missing_id = 99999999

        with patch('odoo.addons.it_helpdesk.controllers.main_api.request',
                   self._mock_request(self.officer, '/api/v1/tickets/bulk')):
            res = self.bulk_ctrl.bulk_action(ticket_ids=[missing_id], action='close')

        self.assertEqual(res['status'], 'success')
        data = res['data']
        self.assertEqual(data['total'], 1)
        self.assertEqual(data['success_count'], 0)
        self.assertEqual(data['fail_count'], 1)
        self.assertEqual(len(data['results']), 1)
        item = data['results'][0]
        self.assertEqual(item['id'], missing_id)
        self.assertFalse(item['ok'])
        self.assertEqual(item['message'], "문의를 찾을 수 없습니다.")
