# -*- coding: utf-8 -*-
import logging
from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)

class AuthAPIController:
    """Authentication and Session Management API"""

    @http.route('/api/v1/auth/login', type='json', auth='none', methods=['POST'], csrf=False)
    def api_login(self, db, login, password):
        """Odoo 사용자 인증 및 세션 정보 반환"""
        try:
            credential = {'login': login, 'password': password, 'type': 'password'}
            auth_info = request.session.authenticate(db, credential)
            uid = auth_info.get('uid') if isinstance(auth_info, dict) else auth_info
            if not uid:
                return {'status': 'error', 'message': 'Invalid credentials'}
            
            user = request.env['res.users'].sudo().browse(uid)
            is_officer = user.has_group('it_helpdesk.group_helpdesk_officer') or user._is_admin()
            
            return {
                'status': 'success',
                'data': {
                    'uid': uid,
                    'name': user.name,
                    'login': user.login,
                    'is_officer': is_officer,
                    'session_id': request.session.sid,
                }
            }
        except Exception as e:
            _logger.exception("Login error in api_login")
            return {'status': 'error', 'message': str(e)}
