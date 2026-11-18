# -*- coding: utf-8 -*-
import hmac
import hashlib
import time
from unittest.mock import MagicMock, patch

from odoo.exceptions import AccessError, ValidationError
from odoo.tests.common import TransactionCase

from ..controllers.reply_template_api import ReplyTemplateAPIController
from ..utils.security import GATEWAY_SHARED_SECRET


class TestReplyTemplate(TransactionCase):

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
        cls.Template = cls.env['it.helpdesk.reply.template']
        cls.controller = ReplyTemplateAPIController()
        g_base = cls.env.ref('base.group_user')
        g_user = cls.env.ref('it_helpdesk.group_helpdesk_user')
        g_officer = cls.env.ref('it_helpdesk.group_helpdesk_officer')
        g_manager = cls.env.ref('it_helpdesk.group_helpdesk_manager')

        cls.employee = cls._make_user('rt_emp', [g_base, g_user])
        cls.officer_a = cls._make_user('rt_off_a', [g_base, g_user, g_officer])
        cls.officer_b = cls._make_user('rt_off_b', [g_base, g_user, g_officer])
        cls.manager = cls._make_user('rt_mgr', [g_base, g_user, g_officer, g_manager])

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

    def test_01_seed_data_exists(self):
        """기본 시드 상용구 6종(공통+5개 분야)과 자리표시자가 로드되어 있어야 한다."""
        seeds = self.Template.search([])
        self.assertGreaterEqual(len(seeds), 6)
        common = self.env.ref('it_helpdesk.reply_template_common_greeting')
        self.assertFalse(common.category)
        self.assertIn('{{requester_name}}', common.body)
        self.assertIn('{{ticket_number}}', common.body)
        self.assertIn('{{officer_name}}', common.body)

    def test_02_length_and_whitespace_constraints(self):
        """제목(1~60자) 및 본문(1~3000자) 제약과 공백 트리밍을 검증한다."""
        env_a = self.Template.with_user(self.officer_a)

        for bad_name in ('', '   ', '가' * 61):
            with self.assertRaises(ValidationError):
                env_a.create({'name': bad_name, 'category': 'hw', 'body': '유효한 본문'})

        for bad_body in ('', '   ', '나' * 3001):
            with self.assertRaises(ValidationError):
                env_a.create({'name': '유효한 제목', 'category': 'hw', 'body': bad_body})

        rec = env_a.create({'name': '  ' + ('a' * 60) + '  ', 'category': '', 'body': '  ' + ('b' * 3000) + '  '})
        self.assertEqual(len(rec.name), 60)
        self.assertEqual(len(rec.body), 3000)
        self.assertFalse(rec.category)

    def test_03_access_rights_and_record_rules(self):
        """사원 차단, 담당자 본인 것만 수정/삭제, 관리자 전체 제어 권한을 검증한다."""
        rec_a = self.Template.with_user(self.officer_a).create({
            'name': 'A담당자 상용구',
            'category': 'sw',
            'body': '소프트웨어 안내 문구',
        })

        with self.assertRaises(AccessError):
            self.Template.with_user(self.employee).search([])
        with self.assertRaises(AccessError):
            self.Template.with_user(self.employee).create({'name': '사원', 'body': '불가'})
        with self.assertRaises(AccessError):
            rec_a.with_user(self.employee).write({'name': '변조'})
        with self.assertRaises(AccessError):
            rec_a.with_user(self.employee).unlink()

        # 다른 담당자는 조회는 가능하나 수정/삭제는 AccessError
        found = self.Template.with_user(self.officer_b).search([('id', '=', rec_a.id)])
        self.assertEqual(len(found), 1)
        with self.assertRaises(AccessError):
            rec_a.with_user(self.officer_b).write({'name': '타인 수정 시도'})
        with self.assertRaises(AccessError):
            rec_a.with_user(self.officer_b).unlink()

        # 본인 수정 성공
        rec_a.with_user(self.officer_a).write({'name': 'A담당자 수정됨'})
        self.assertEqual(rec_a.name, 'A담당자 수정됨')

        # 관리자는 타인 상용구도 수정 및 삭제 가능
        rec_a.with_user(self.manager).write({'name': '관리자 수정'})
        self.assertEqual(rec_a.name, '관리자 수정')
        rec_a_id = rec_a.id
        rec_a.with_user(self.manager).unlink()
        self.assertFalse(self.Template.search([('id', '=', rec_a_id)]).exists())

    def test_04_controller_list_filter_and_crud(self):
        """컨트롤러 list(category 필터/정렬/is_mine) 및 CRUD 권한을 검증한다."""
        with patch('odoo.addons.it_helpdesk.controllers.main_api.request',
                   self._mock_request(self.officer_a, '/api/v1/reply-templates/create')):
            res_hw = self.controller.create_reply_template(name='가_하드웨어', category='hw', body='  하드웨어 조치  ')
            self.assertEqual(res_hw['status'], 'success')
            self.assertTrue(res_hw['data']['is_mine'])
            self.assertEqual(res_hw['data']['body'], '하드웨어 조치')
            hw_id = res_hw['data']['id']

            res_sw = self.controller.create_reply_template(name='나_소프트웨어', category='sw', body='SW 조치')
            sw_id = res_sw['data']['id']

        with patch('odoo.addons.it_helpdesk.controllers.main_api.request',
                   self._mock_request(self.officer_b, '/api/v1/reply-templates/list')):
            list_hw = self.controller.list_reply_templates(category='hw')
            items = list_hw['data']
            categories = {it['category'] for it in items}
            self.assertTrue(categories.issubset({'hw', ''}))
            names = [it['name'] for it in items]
            self.assertIn('접수 확인 및 처리 안내', names)
            self.assertIn('프린터 드라이버 재설치 안내', names)
            # 한글 정렬 순서는 DB 콜레이션에 따라 달라지므로 모델 정렬(name) 결과와 동일한지만 확인한다.
            expected_ids = self.Template.search([('category', 'in', ['hw', False, ''])], order='name').ids
            self.assertEqual([it['id'] for it in items], expected_ids)
            hw_item = next(it for it in items if it['id'] == hw_id)
            self.assertFalse(hw_item['is_mine'])
            self.assertNotIn(sw_id, [it['id'] for it in items])

            list_all = self.controller.list_reply_templates()
            self.assertIn(sw_id, [it['id'] for it in list_all['data']])

        # 타 담당자 컨트롤러 수정/삭제 차단
        with patch('odoo.addons.it_helpdesk.controllers.main_api.request',
                   self._mock_request(self.officer_b, '/api/v1/reply-templates/update')):
            with self.assertRaises(AccessError):
                self.controller.update_reply_template(template_id=hw_id, name='변경', category='hw', body='본문')

        with patch('odoo.addons.it_helpdesk.controllers.main_api.request',
                   self._mock_request(self.officer_b, '/api/v1/reply-templates/delete')):
            with self.assertRaises(AccessError):
                self.controller.delete_reply_template(template_id=hw_id)

        # 사원 컨트롤러 접근 차단
        with patch('odoo.addons.it_helpdesk.controllers.main_api.request',
                   self._mock_request(self.employee, '/api/v1/reply-templates/list')):
            with self.assertRaises(AccessError):
                self.controller.list_reply_templates()

        # 본인 삭제 성공
        with patch('odoo.addons.it_helpdesk.controllers.main_api.request',
                   self._mock_request(self.officer_a, '/api/v1/reply-templates/delete')):
            del_res = self.controller.delete_reply_template(template_id=hw_id)
            self.assertEqual(del_res['status'], 'success')
