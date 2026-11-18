# -*- coding: utf-8 -*-
import hashlib
import hmac
import secrets
import time
from unittest.mock import MagicMock, patch

from odoo.exceptions import AccessError
from odoo.tests.common import TransactionCase

from ..utils.security import _gateway_secret_is_safe, verify_gateway_request


class TestGatewaySecret(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        g_base = cls.env.ref('base.group_user')
        g_user = cls.env.ref('it_helpdesk.group_helpdesk_user')
        cls.user = cls.env['res.users'].with_context(no_reset_password=True).create({
            'name': 'gw_secret_tester',
            'login': 'gw_secret_tester',
            'email': 'gw_secret_tester@test.com',
            'groups_id': [(6, 0, [g_base.id, g_user.id])],
        })

    def _mock_request(self, user, path, secret):
        ts = str(int(time.time()))
        uid_str = str(user.id)
        body_hash = hashlib.sha256(b'').hexdigest()
        payload = f"POST:{path}:{uid_str}:{ts}:{body_hash}".encode('utf-8')
        sig = hmac.new(secret.encode('utf-8'), payload, hashlib.sha256).hexdigest()

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

    def test_01_gateway_secret_is_safe(self):
        """빈 값, 31자, 알려진 예시값은 거부하고 64자 무작위 hex는 허용한다."""
        self.assertFalse(_gateway_secret_is_safe(''))
        self.assertFalse(_gateway_secret_is_safe('   '))
        self.assertFalse(_gateway_secret_is_safe(secrets.token_hex(16)[:31]))
        for known in (
            'secure_inter_tier_hmac_secret_key_32_chars',
            'it_company_board_super_secret_jwt_key_2026_xyz',
            'production_change_in_env_super_secret_key',
            'gateway_odoo_tunnel_shared_secret_key',
        ):
            self.assertFalse(_gateway_secret_is_safe(known))
        self.assertTrue(_gateway_secret_is_safe(secrets.token_hex(32)))

    def test_02_verify_gateway_request_fails_closed_when_secret_empty(self):
        """GATEWAY_SHARED_SECRET가 빈 문자열이면 올바른 HMAC 형식 헤더도 AccessError로 차단한다."""
        req = self._mock_request(self.user, '/api/v1/tickets/list', '')
        with (
            patch('odoo.addons.it_helpdesk.controllers.main_api.request', req),
            patch('odoo.addons.it_helpdesk.utils.security.GATEWAY_SHARED_SECRET', ''),
        ):
            with self.assertRaises(AccessError):
                verify_gateway_request()

    def test_03_verify_gateway_request_succeeds_with_valid_secret(self):
        """안전한 64자 hex 비밀키로 서명된 요청은 해당 사용자를 반환한다."""
        valid_secret = secrets.token_hex(32)
        req = self._mock_request(self.user, '/api/v1/tickets/list', valid_secret)
        with (
            patch('odoo.addons.it_helpdesk.controllers.main_api.request', req),
            patch('odoo.addons.it_helpdesk.utils.security.GATEWAY_SHARED_SECRET', valid_secret),
        ):
            authed_user = verify_gateway_request()
        self.assertEqual(authed_user.id, self.user.id)
