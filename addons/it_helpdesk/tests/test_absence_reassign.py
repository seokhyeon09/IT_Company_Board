# -*- coding: utf-8 -*-
import hmac
import hashlib
import time
from unittest.mock import MagicMock, patch

from odoo.tests.common import TransactionCase

from ..controllers.officer_absence_api import OfficerAbsenceAPIController
from ..utils.security import GATEWAY_SHARED_SECRET


class TestAbsenceReassign(TransactionCase):

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
        cls.absence_ctrl = OfficerAbsenceAPIController()

        g_base = cls.env.ref('base.group_user')
        g_user = cls.env.ref('it_helpdesk.group_helpdesk_user')
        g_officer = cls.env.ref('it_helpdesk.group_helpdesk_officer')

        cls.employee = cls._make_user('abs_r_emp', [g_base, g_user])
        cls.off_a = cls._make_user('abs_r_off_a', [g_base, g_user, g_officer])
        cls.off_b = cls._make_user('abs_r_off_b', [g_base, g_user, g_officer])

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

    def _create_ticket(self, title, status, assignee=None):
        t = self.Ticket.with_user(self.employee).create({
            'title': title,
            'category': 'hw',
            'content': '<p>내용</p>',
            'priority': '1',
        })
        vals = {'status': status}
        if assignee:
            vals['assignee_id'] = assignee.id
        if status in ('resolved', 'closed'):
            vals['resolution_note'] = '<p>조치 완료</p>'
        t.sudo().write(vals)
        return t

    def test_01_open_tickets_filtered_by_assignee_and_status(self):
        """부재 설정 응답의 open_tickets는 본인 배정 + assigned/in_progress/pending만 포함한다."""
        t_assigned = self._create_ticket('대상1', 'assigned', self.off_a)
        t_progress = self._create_ticket('대상2', 'in_progress', self.off_a)
        t_pending = self._create_ticket('대상3', 'pending', self.off_a)
        self._create_ticket('제외-해결', 'resolved', self.off_a)
        self._create_ticket('제외-종결', 'closed', self.off_a)
        self._create_ticket('제외-취소', 'canceled', self.off_a)
        self._create_ticket('제외-미배정', 'submitted', None)
        self._create_ticket('제외-타인', 'in_progress', self.off_b)

        with patch('odoo.addons.it_helpdesk.controllers.main_api.request',
                   self._mock_request(self.off_a, '/api/v1/officers/me/absence/set')):
            res_on = self.absence_ctrl.set_my_absence(is_absent=True)

        returned_ids = {t['id'] for t in res_on['open_tickets']}
        self.assertEqual(returned_ids, {t_assigned.id, t_progress.id, t_pending.id})
        self.assertEqual(res_on['open_ticket_total'], 3)
        for item in res_on['open_tickets']:
            self.assertEqual(set(item.keys()), {'id', 'ticket_number', 'title', 'status', 'priority', 'category'})

        with patch('odoo.addons.it_helpdesk.controllers.main_api.request',
                   self._mock_request(self.off_a, '/api/v1/officers/me/absence/get')):
            res_get = self.absence_ctrl.get_my_absence()
        self.assertEqual(res_get['open_tickets'], [])
        self.assertEqual(res_get['open_ticket_total'], 0)

        with patch('odoo.addons.it_helpdesk.controllers.main_api.request',
                   self._mock_request(self.off_a, '/api/v1/officers/me/absence/set')):
            res_off = self.absence_ctrl.set_my_absence(is_absent=False)
        self.assertEqual(res_off['open_tickets'], [])
        self.assertEqual(res_off['open_ticket_total'], 0)

    def test_02_open_tickets_limit_100_and_total(self):
        """미처리 티켓이 100건을 초과하면 100건만 반환하고 open_ticket_total에 전체 건수를 반환한다."""
        vals_list = [
            {
                'title': f'대량 테스트 {i}',
                'category': 'hw',
                'content': '<p>내용</p>',
                'priority': '1',
                'author_id': self.employee.id,
                'assignee_id': self.off_b.id,
                'status': 'assigned',
            }
            for i in range(105)
        ]
        self.Ticket.sudo().create(vals_list)

        with patch('odoo.addons.it_helpdesk.controllers.main_api.request',
                   self._mock_request(self.off_b, '/api/v1/officers/me/absence/set')):
            res = self.absence_ctrl.set_my_absence(is_absent=True)

        self.assertEqual(len(res['open_tickets']), 100)
        self.assertEqual(res['open_ticket_total'], 105)
