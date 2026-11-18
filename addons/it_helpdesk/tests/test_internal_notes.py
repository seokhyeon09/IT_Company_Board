# -*- coding: utf-8 -*-
import hmac
import hashlib
import json
import time
from unittest.mock import MagicMock, patch

from odoo.exceptions import AccessError, UserError
from odoo.tests.common import TransactionCase

from ..controllers.ticket_note_api import TicketNoteAPIController
from ..controllers.ticket_query_api import TicketQueryAPIController
from ..utils.security import GATEWAY_SHARED_SECRET


class TestInternalNotes(TransactionCase):

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
        cls.note_ctrl = TicketNoteAPIController()
        cls.query_ctrl = TicketQueryAPIController()

        g_base = cls.env.ref('base.group_user')
        g_user = cls.env.ref('it_helpdesk.group_helpdesk_user')
        g_officer = cls.env.ref('it_helpdesk.group_helpdesk_officer')

        cls.employee = cls._make_user('note_emp', [g_base, g_user])
        cls.officer = cls._make_user('note_off', [g_base, g_user, g_officer])

        cls.ticket = cls.Ticket.with_user(cls.employee).create({
            'title': '내부 메모 테스트 문의',
            'category': 'hw',
            'content': '<p>프린터가 안 됩니다.</p>',
            'priority': '1',
        })

    def _mock_request(self, user, path='/api/v1/tickets/notes/add'):
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

    def test_01_add_note_and_validation_and_canceled_allowed(self):
        """담당자 내부 메모 추가, 길이/공백 검증, 사원 차단, 취소 상태 허용을 검증한다."""
        with patch('odoo.addons.it_helpdesk.controllers.main_api.request',
                   self._mock_request(self.employee)):
            with self.assertRaises(AccessError):
                self.note_ctrl.add_internal_note(ticket_id=self.ticket.id, content='사원 시도')

        with patch('odoo.addons.it_helpdesk.controllers.main_api.request',
                   self._mock_request(self.officer)):
            for bad in ('', '   ', None, '가' * 2001):
                with self.assertRaises(UserError):
                    self.note_ctrl.add_internal_note(ticket_id=self.ticket.id, content=bad)

            res = self.note_ctrl.add_internal_note(ticket_id=self.ticket.id, content='  첫 번째 메모  ')
            self.assertEqual(res['status'], 'success')
            self.assertEqual(res['data']['content'], '첫 번째 메모')

            # 취소 상태에서도 내부 메모 추가 허용
            canceled_ticket = self.Ticket.with_user(self.employee).create({
                'title': '취소 건',
                'category': 'etc',
                'content': '<p>취소 테스트</p>',
                'priority': '0',
            })
            canceled_ticket.sudo().write({'status': 'canceled'})
            res_canceled = self.note_ctrl.add_internal_note(ticket_id=canceled_ticket.id, content='취소 사유 메모')
            self.assertEqual(res_canceled['status'], 'success')

    def test_02_no_leak_to_employee_and_no_mail_created(self):
        """타임라인/모의메일 위장 키워드가 포함된 내부 메모도 사원 상세 응답 어디에도 노출되지 않고 mail.mail을 생성하지 않는다."""
        spoof_contents = [
            '[조치 답변] 내부전용XQ1',
            '[담당자 변경] 내부전용XQ2',
            '[답변 대기 요청] 내부전용XQ3',
            '[추가 재문의] 내부전용XQ4',
            'IT 담당자 조치 내용: 내부전용XQ5',
        ]
        mail_before = self.env['mail.mail'].sudo().search_count([])

        with patch('odoo.addons.it_helpdesk.controllers.main_api.request',
                   self._mock_request(self.officer)):
            for txt in spoof_contents:
                self.note_ctrl.add_internal_note(ticket_id=self.ticket.id, content=txt)

        mail_after = self.env['mail.mail'].sudo().search_count([])
        self.assertEqual(mail_before, mail_after)

        # 사원 상세 응답: internal_notes는 빈 배열이며 전체 JSON 직렬화에 '내부전용XQ' 문자열이 없어야 함
        with patch('odoo.addons.it_helpdesk.controllers.main_api.request',
                   self._mock_request(self.employee, '/api/v1/tickets/detail')):
            emp_res = self.query_ctrl.get_ticket_detail(ticket_id=self.ticket.id)

        emp_data = emp_res['data']
        self.assertEqual(emp_data['internal_notes'], [])
        self.assertEqual(emp_data['logs'], [])
        emp_serialized = json.dumps(emp_data, ensure_ascii=False)
        self.assertNotIn('내부전용XQ', emp_serialized)

        # 담당자 상세 응답: internal_notes에 5건이 최신순으로 존재해야 함
        with patch('odoo.addons.it_helpdesk.controllers.main_api.request',
                   self._mock_request(self.officer, '/api/v1/tickets/detail')):
            off_res = self.query_ctrl.get_ticket_detail(ticket_id=self.ticket.id)

        notes = off_res['data']['internal_notes']
        note_contents = [n['content'] for n in notes]
        for expected in spoof_contents:
            self.assertIn(expected, note_contents)
        self.assertEqual(note_contents[0], 'IT 담당자 조치 내용: 내부전용XQ5')
