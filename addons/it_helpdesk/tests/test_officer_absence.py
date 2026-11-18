# -*- coding: utf-8 -*-
import hmac
import hashlib
import time
from datetime import timedelta
from unittest.mock import MagicMock, patch

from odoo import fields
from odoo.exceptions import AccessError, UserError
from odoo.tests.common import TransactionCase

from ..controllers.insight_api import InsightAPIController
from ..controllers.officer_absence_api import OfficerAbsenceAPIController
from ..utils.auto_assign import AUTO_ASSIGN_PARAM, create_ticket_with_auto_assign, pick_officer
from ..utils.security import GATEWAY_SHARED_SECRET


class TestOfficerAbsence(TransactionCase):

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
        cls.Rule = cls.env['it.helpdesk.assign.rule']
        cls.absence_ctrl = OfficerAbsenceAPIController()
        cls.insight_ctrl = InsightAPIController()

        g_base = cls.env.ref('base.group_user')
        g_user = cls.env.ref('it_helpdesk.group_helpdesk_user')
        g_officer = cls.env.ref('it_helpdesk.group_helpdesk_officer')

        cls.employee = cls._make_user('abs_emp', [g_base, g_user])
        cls.off_a = cls._make_user('abs_off_a', [g_base, g_user, g_officer])
        cls.off_b = cls._make_user('abs_off_b', [g_base, g_user, g_officer])

        cls.Rule.with_context(active_test=False).search([]).unlink()
        cls.env['ir.config_parameter'].sudo().set_param(AUTO_ASSIGN_PARAM, 'True')
        cls.Rule.create({
            'category': 'hw',
            'officer_ids': [(6, 0, [cls.off_a.id, cls.off_b.id])],
            'active': True,
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

    def test_01_effective_absence_method(self):
        """_helpdesk_is_absent가 종료일 없음/미래/오늘/과거 케이스를 정확히 판정한다."""
        today = fields.Date.today()
        self.off_a.write({'helpdesk_absent': False, 'helpdesk_absent_until': today + timedelta(days=3)})
        self.assertFalse(self.off_a._helpdesk_is_absent(today=today))

        self.off_a.write({'helpdesk_absent': True, 'helpdesk_absent_until': False})
        self.assertTrue(self.off_a._helpdesk_is_absent(today=today))

        self.off_a.write({'helpdesk_absent': True, 'helpdesk_absent_until': today + timedelta(days=2)})
        self.assertTrue(self.off_a._helpdesk_is_absent(today=today))

        self.off_a.write({'helpdesk_absent': True, 'helpdesk_absent_until': today})
        self.assertTrue(self.off_a._helpdesk_is_absent(today=today))

        self.off_a.write({'helpdesk_absent': True, 'helpdesk_absent_until': today - timedelta(days=1)})
        self.assertFalse(self.off_a._helpdesk_is_absent(today=today))

    def test_02_auto_assign_skips_absent_and_handles_all_absent(self):
        """부재 담당자는 자동 배정에서 제외되고, 전원 부재 시 미배정으로 정상 접수된다."""
        today = fields.Date.today()
        self.off_a.write({'helpdesk_absent': True, 'helpdesk_absent_until': False})
        self.off_b.write({'helpdesk_absent': False, 'helpdesk_absent_until': False})

        t1 = create_ticket_with_auto_assign(
            self.Ticket.with_user(self.employee),
            {'title': '부재 테스트 1', 'content': '<p>내용</p>', 'category': 'hw'},
        )
        self.assertEqual(t1.status, 'assigned')
        self.assertEqual(t1.assignee_id, self.off_b)

        # 전원 부재
        self.off_b.write({'helpdesk_absent': True, 'helpdesk_absent_until': today + timedelta(days=1)})
        self.assertIsNone(pick_officer(self.env, 'hw'))
        t2 = create_ticket_with_auto_assign(
            self.Ticket.with_user(self.employee),
            {'title': '전원 부재 테스트', 'content': '<p>내용</p>', 'category': 'hw'},
        )
        self.assertEqual(t2.status, 'submitted')
        self.assertFalse(t2.assignee_id)

        # off_a 종료일 경과 시 별도 크론 없이 다시 배정 대상
        self.off_a.write({'helpdesk_absent': True, 'helpdesk_absent_until': today - timedelta(days=1)})
        t3 = create_ticket_with_auto_assign(
            self.Ticket.with_user(self.employee),
            {'title': '부재 만료 후 배정', 'content': '<p>내용</p>', 'category': 'hw'},
        )
        self.assertEqual(t3.status, 'assigned')
        self.assertEqual(t3.assignee_id, self.off_a)

    def test_03_absence_api_self_only_and_validation(self):
        """부재 API는 사원을 거부하고, 과거 날짜를 거부하며, 요청자 본인만 변경한다."""
        today = fields.Date.today()
        future_str = fields.Date.to_string(today + timedelta(days=3))
        past_str = fields.Date.to_string(today - timedelta(days=1))

        # 사원 접근 차단
        with patch('odoo.addons.it_helpdesk.controllers.main_api.request',
                   self._mock_request(self.employee, '/api/v1/officers/me/absence/get')):
            with self.assertRaises(AccessError):
                self.absence_ctrl.get_my_absence()

        with patch('odoo.addons.it_helpdesk.controllers.main_api.request',
                   self._mock_request(self.employee, '/api/v1/officers/me/absence/set')):
            with self.assertRaises(AccessError):
                self.absence_ctrl.set_my_absence(is_absent=True)

        # 과거 날짜 차단
        with patch('odoo.addons.it_helpdesk.controllers.main_api.request',
                   self._mock_request(self.off_a, '/api/v1/officers/me/absence/set')):
            with self.assertRaises(UserError):
                self.absence_ctrl.set_my_absence(is_absent=True, absent_until=past_str)

            # user_id를 임의로 넘겨도 본인(off_a)만 변경됨
            res = self.absence_ctrl.set_my_absence(
                is_absent=True, absent_until=future_str, user_id=self.off_b.id
            )
            self.assertEqual(res['data'], {'is_absent': True, 'absent_until': future_str})
            self.assertFalse(self.off_b.helpdesk_absent)

            # 해제 시 absent_until은 None으로 저장
            res_off = self.absence_ctrl.set_my_absence(is_absent=False, absent_until=future_str)
            self.assertEqual(res_off['data'], {'is_absent': False, 'absent_until': None})
            self.assertFalse(self.off_a.helpdesk_absent_until)

    def test_04_get_officers_includes_absence_fields(self):
        """get_officers 응답 각 항목에 실효 부재 여부와 종료일이 포함된다."""
        today = fields.Date.today()
        future_str = fields.Date.to_string(today + timedelta(days=2))
        self.off_a.write({'helpdesk_absent': True, 'helpdesk_absent_until': today + timedelta(days=2)})
        self.off_b.write({'helpdesk_absent': True, 'helpdesk_absent_until': today - timedelta(days=1)})

        with patch('odoo.addons.it_helpdesk.controllers.main_api.request',
                   self._mock_request(self.off_a, '/api/v1/tickets/officers')):
            res = self.insight_ctrl.get_officers()

        by_id = {item['id']: item for item in res['data']}
        self.assertTrue(by_id[self.off_a.id]['is_absent'])
        self.assertEqual(by_id[self.off_a.id]['absent_until'], future_str)
        self.assertFalse(by_id[self.off_b.id]['is_absent'])
        self.assertIsNone(by_id[self.off_b.id]['absent_until'])
