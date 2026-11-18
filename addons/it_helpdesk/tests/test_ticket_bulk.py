# -*- coding: utf-8 -*-
import html
import hmac
import hashlib
import time
from unittest.mock import MagicMock, patch

from odoo.exceptions import AccessError, UserError
from odoo.tests.common import TransactionCase

from ..controllers.ticket_bulk_api import TicketBulkAPIController
from ..controllers.ticket_workflow_api import TicketWorkflowAPIController
from ..utils.security import GATEWAY_SHARED_SECRET


class TestTicketBulk(TransactionCase):

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
        cls.bulk_ctrl = TicketBulkAPIController()
        cls.wf_ctrl = TicketWorkflowAPIController()

        g_base = cls.env.ref('base.group_user')
        g_user = cls.env.ref('it_helpdesk.group_helpdesk_user')
        g_officer = cls.env.ref('it_helpdesk.group_helpdesk_officer')
        g_manager = cls.env.ref('it_helpdesk.group_helpdesk_manager')

        cls.employee = cls._make_user('bulk_emp', [g_base, g_user])
        cls.off_a = cls._make_user('bulk_off_a', [g_base, g_user, g_officer])
        cls.off_b = cls._make_user('bulk_off_b', [g_base, g_user, g_officer])
        cls.manager = cls._make_user('bulk_mgr', [g_base, g_user, g_officer, g_manager])

        cls.Rule.with_context(active_test=False).search([]).unlink()
        cls.Rule.create({
            'category': 'hw',
            'officer_ids': [(6, 0, [cls.off_a.id, cls.off_b.id])],
            'active': True,
        })

    def _mock_request(self, user, path='/api/v1/tickets/bulk'):
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

    def _create_ticket(self, title='테스트 문의', category='hw', status=None, assignee=None):
        t = self.Ticket.with_user(self.employee).create({
            'title': title,
            'category': category,
            'content': '<p>문의 상세 내용</p>',
            'priority': '1',
        })
        vals = {}
        if assignee:
            vals['assignee_id'] = assignee.id
        if status:
            vals['status'] = status
        if vals:
            t.sudo().write(vals)
        return t

    @staticmethod
    def _chatter(ticket):
        """채터 본문은 이스케이프되어 저장되므로 풀어서 전체 메시지를 이어 붙인다."""
        return ' '.join(html.unescape(html.unescape(m.body or '')) for m in ticket.message_ids)

    def test_01_bulk_assign_success_and_skip_same_assignee(self):
        """일괄 assign 성공 시 [담당자 변경] 메시지와 인계 사유가 기록되고, 동일 담당자 재지정은 건너뜀 처리된다."""
        t1 = self._create_ticket('일괄 배정 1')
        t2 = self._create_ticket('이미 배정됨', status='assigned', assignee=self.off_b)

        with patch('odoo.addons.it_helpdesk.controllers.main_api.request',
                   self._mock_request(self.off_a)):
            res = self.bulk_ctrl.bulk_action(
                ticket_ids=[t1.id, t2.id],
                action='assign',
                officer_id=self.off_b.id,
                reason='업무 이관',
            )

        self.assertEqual(res['status'], 'success')
        data = res['data']
        self.assertEqual(data['total'], 2)
        self.assertEqual(data['success_count'], 2)
        self.assertEqual(data['fail_count'], 0)
        self.assertEqual(t1.assignee_id, self.off_b)
        self.assertEqual(t1.status, 'assigned')
        self.assertIn('[담당자 변경]', self._chatter(t1))
        self.assertIn('인계 사유: 업무 이관', self._chatter(t1))
        self.assertEqual(data['results'][1]['message'], '이미 해당 담당자에게 배정되어 있습니다.')

    def test_02_bulk_assign_auto_skips_absent_and_fails_when_no_candidate(self):
        """assign_auto는 부재 담당자를 제외하고 배정하며, 후보가 없는 분야는 해당 건만 실패 처리한다."""
        self.off_a.write({'helpdesk_absent': True, 'helpdesk_absent_until': False})
        self.off_b.write({'helpdesk_absent': False, 'helpdesk_absent_until': False})

        t_hw = self._create_ticket('HW 문의', category='hw', status='assigned', assignee=self.off_a)
        t_sw = self._create_ticket('SW 문의(규칙없음)', category='sw')

        with patch('odoo.addons.it_helpdesk.controllers.main_api.request',
                   self._mock_request(self.off_a)):
            res = self.bulk_ctrl.bulk_action(
                ticket_ids=[t_hw.id, t_sw.id],
                action='assign_auto',
                reason='담당자 부재로 인한 인계',
            )

        data = res['data']
        self.assertEqual(data['success_count'], 1)
        self.assertEqual(data['fail_count'], 1)
        self.assertEqual(t_hw.assignee_id, self.off_b)
        self.assertTrue(data['results'][0]['ok'])
        self.assertFalse(data['results'][1]['ok'])
        self.assertEqual(data['results'][1]['message'], '자동으로 배정할 수 있는 담당자가 없습니다.')

    def test_03_bulk_start_progress_and_status_mismatch(self):
        """start_progress는 assigned/pending 건은 성공하고 submitted/resolved 건은 실패한다."""
        t_assigned = self._create_ticket('배정 건', status='assigned', assignee=self.off_a)
        t_submitted = self._create_ticket('접수대기 건')

        with patch('odoo.addons.it_helpdesk.controllers.main_api.request',
                   self._mock_request(self.off_a)):
            res = self.bulk_ctrl.bulk_action(
                ticket_ids=[t_assigned.id, t_submitted.id],
                action='start_progress',
            )

        self.assertEqual(res['data']['success_count'], 1)
        self.assertEqual(res['data']['fail_count'], 1)
        self.assertEqual(t_assigned.status, 'in_progress')
        self.assertEqual(t_submitted.status, 'submitted')

    def test_04_bulk_close_and_savepoint_rollback_isolation(self):
        """일괄 close에서 일부 건이 실패해도 성공 건은 커밋되고 실패 건은 savepoint 롤백으로 부작용이 남지 않는다."""
        t_ok_with_note = self._create_ticket('종결 가능 1', status='in_progress', assignee=self.off_a)
        t_ok_default = self._create_ticket('종결 가능 2', status='in_progress', assignee=self.off_a)
        t_fail = self._create_ticket('종결 불가(submitted)')

        with patch('odoo.addons.it_helpdesk.controllers.main_api.request',
                   self._mock_request(self.off_a)):
            res_note = self.bulk_ctrl.bulk_action(
                ticket_ids=[t_ok_with_note.id, t_fail.id, 99999999],
                action='close',
                note='일괄 종결 사유',
            )
            res_default = self.bulk_ctrl.bulk_action(
                ticket_ids=[t_ok_default.id],
                action='close',
            )

        self.assertEqual(res_note['data']['success_count'], 1)
        self.assertEqual(res_note['data']['fail_count'], 2)
        self.assertEqual(t_ok_with_note.status, 'closed')
        self.assertIn('일괄 종결 사유', t_ok_with_note.resolution_note)
        # 실패 건은 savepoint 롤백되어 resolution_note가 변경되지 않아야 함
        self.assertEqual(t_fail.status, 'submitted')
        self.assertFalse(t_fail.resolution_note)
        # 존재하지 않는 ID 실패 메시지
        self.assertEqual(res_note['data']['results'][2]['message'], '문의를 찾을 수 없습니다.')
        # 메모 미입력 종결 기본 문구
        self.assertEqual(res_default['data']['success_count'], 1)
        self.assertEqual(t_ok_default.status, 'closed')
        self.assertIn('담당자 직권 종결 처리', str(t_ok_default.resolution_note))

    def test_05_validation_and_access_control(self):
        """검증 오류(빈 목록, 51건 초과, 잘못된 action, 없는 officer_id), 중복 제거, 사원 AccessError를 검증한다."""
        t1 = self._create_ticket('중복 테스트', status='assigned', assignee=self.off_a)

        # 사원 접근 차단
        with patch('odoo.addons.it_helpdesk.controllers.main_api.request',
                   self._mock_request(self.employee)):
            with self.assertRaises(AccessError):
                self.bulk_ctrl.bulk_action(ticket_ids=[t1.id], action='start_progress')

        with patch('odoo.addons.it_helpdesk.controllers.main_api.request',
                   self._mock_request(self.off_a)):
            with self.assertRaises(UserError):
                self.bulk_ctrl.bulk_action(ticket_ids=[], action='start_progress')
            with self.assertRaises(UserError):
                self.bulk_ctrl.bulk_action(ticket_ids=list(range(1, 52)), action='start_progress')
            with self.assertRaises(UserError):
                self.bulk_ctrl.bulk_action(ticket_ids=[t1.id], action='invalid_action')
            with self.assertRaises(UserError):
                self.bulk_ctrl.bulk_action(ticket_ids=[t1.id], action='assign', officer_id=99999999)

            # 중복 ID는 제거되어 1건만 처리됨
            res_dedup = self.bulk_ctrl.bulk_action(ticket_ids=[t1.id, t1.id], action='start_progress')
            self.assertEqual(res_dedup['data']['total'], 1)
            self.assertEqual(res_dedup['data']['success_count'], 1)

    def test_06_single_workflow_regression_after_refactor(self):
        """workflow_ops 리팩터링 후 단건 assign/start-progress/close 응답과 채터 문구가 동일하다."""
        t = self._create_ticket('단건 회귀 테스트')

        with patch('odoo.addons.it_helpdesk.controllers.main_api.request',
                   self._mock_request(self.off_a, '/api/v1/tickets/assign')):
            r_assign = self.wf_ctrl.assign_ticket(ticket_id=t.id, assignee_id=self.off_b.id, reason='단건 인계')
        self.assertEqual(r_assign['status'], 'success')
        self.assertEqual(r_assign['data']['assignee_id'], self.off_b.id)
        self.assertEqual(r_assign['data']['status'], 'assigned')
        chatter = self._chatter(t)
        self.assertIn('[담당자 변경]', chatter)
        self.assertIn(self.off_b.name, chatter)
        self.assertIn('인계 사유: 단건 인계', chatter)

        with patch('odoo.addons.it_helpdesk.controllers.main_api.request',
                   self._mock_request(self.off_b, '/api/v1/tickets/start-progress')):
            r_start = self.wf_ctrl.start_progress_ticket(ticket_id=t.id)
        self.assertEqual(r_start['status'], 'success')
        self.assertEqual(r_start['data']['status'], 'in_progress')
        self.assertIn(f'<b>[처리 시작]</b> 담당자({self.off_b.name})가 문의 처리를 시작하였습니다.', self._chatter(t))

        with patch('odoo.addons.it_helpdesk.controllers.main_api.request',
                   self._mock_request(self.off_b, '/api/v1/tickets/close')):
            r_close = self.wf_ctrl.close_ticket(ticket_id=t.id)
        self.assertEqual(r_close['status'], 'success')
        self.assertEqual(r_close['data']['status'], 'closed')
        self.assertIn('담당자 직권 종결 처리', str(t.resolution_note))
        self.assertIn(f'<b>[티켓 종결]</b> IT 담당자({self.off_b.name})에 의해 문의가 종결되었습니다.', self._chatter(t))
