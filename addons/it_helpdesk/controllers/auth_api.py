# -*- coding: utf-8 -*-
import logging
from odoo import http
from odoo.http import request
from ..utils import get_current_request

_logger = logging.getLogger(__name__)

class AuthAPIController(http.Controller):
    """Authentication and Session Management API"""

    @http.route('/api/v1/auth/login', type='json', auth='none', methods=['POST'], csrf=False)
    def api_login(self, db, login, password):
        """Odoo 사용자 인증 및 세션 정보 반환"""
        req = get_current_request()
        try:
            credential = {'login': login, 'password': password, 'type': 'password'}
            auth_info = req.session.authenticate(db, credential)
            uid = auth_info.get('uid') if isinstance(auth_info, dict) else auth_info
            if not uid:
                return {'status': 'error', 'message': 'Invalid credentials'}
            
            user = req.env['res.users'].sudo().browse(uid)
            is_admin = user._is_admin()
            is_officer = user.has_group('it_helpdesk.group_helpdesk_officer') or is_admin
            
            return {
                'status': 'success',
                'data': {
                    'uid': uid,
                    'name': user.name,
                    'login': user.login,
                    'is_officer': is_officer,
                    'is_admin': is_admin,
                    'session_id': req.session.sid,
                }
            }
        except Exception as e:
            _logger.exception("Login error in api_login")
            return {'status': 'error', 'message': str(e)}
