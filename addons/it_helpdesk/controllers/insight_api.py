# -*- coding: utf-8 -*-
"""담당자 통계 및 모의 이메일 알림 API"""
from odoo import http
from odoo.exceptions import AccessError

from ..utils import verify_gateway_request, get_current_request
from ..utils.mock_email import build_mock_emails
from ..utils.stats_calculator import compute_officer_stats_payload


class InsightAPIController(http.Controller):
    """Officer Statistics and Mock Email Notification API"""

    @http.route('/api/v1/tickets/officer-stats', type='json', auth='none', methods=['POST'], csrf=False)
    def get_officer_stats(self):
        """담당자별 처리 현황, SLA 준수율, 평균 만족도, MTTR 및 카테고리 비중 (담당자/관리자 전용)"""
        req_env = get_current_request().env
        user = verify_gateway_request()
        if not (user.has_group('it_helpdesk.group_helpdesk_officer') or user._is_admin()):
            raise AccessError("Only IT officers can view officer statistics.")

        data = compute_officer_stats_payload(req_env, user)
        return {"status": "success", "data": data}

    @http.route('/api/v1/tickets/notifications', type='json', auth='none', methods=['POST'], csrf=False)
    def get_mock_notifications(self, limit=50):
        """로그인 사용자 본인이 수신자인 모의 이메일 알림만 조회 (DB 읽음 기록 연동)"""
        req_env = get_current_request().env
        user = verify_gateway_request()
        is_officer = user.has_group('it_helpdesk.group_helpdesk_officer') or user._is_admin()
        tickets = req_env['it.helpdesk.ticket'].sudo().search([], order='write_date desc, id desc', limit=100)

        # DB에서 해당 사용자의 읽은 알림 ID 조회
        read_records = req_env['it.helpdesk.notification.read'].sudo().search([('user_id', '=', user.id)])
        read_ids = set(read_records.mapped('notification_id'))

        emails = []
        for t in tickets:
            emails.extend(build_mock_emails(t, user, is_officer, read_ids=read_ids))
        emails.sort(key=lambda x: x.get("sent_at") or "", reverse=True)
        max_items = min(max(1, int(limit or 50)), 100)
        return {"status": "success", "total": len(emails), "data": emails[:max_items]}

    @http.route('/api/v1/tickets/notifications/read', type='json', auth='none', methods=['POST'], csrf=False)
    def mark_notifications_read(self, notification_ids=None):
        """알림 메일 읽음 처리 (DB 영구 저장)"""
        req_env = get_current_request().env
        user = verify_gateway_request()
        if not notification_ids:
            return {"status": "success", "message": "No notification IDs provided."}

        target_ids = list(notification_ids) if isinstance(notification_ids, (list, tuple)) else [str(notification_ids)]
        ReadModel = req_env['it.helpdesk.notification.read'].sudo()
        existing = set(ReadModel.search([
            ('user_id', '=', user.id),
            ('notification_id', 'in', target_ids)
        ]).mapped('notification_id'))

        to_create = [
            {'user_id': user.id, 'notification_id': nid}
            for nid in target_ids if nid and nid not in existing
        ]
        if to_create:
            ReadModel.create(to_create)

        return {"status": "success", "data": {"marked_count": len(to_create)}}

    @http.route('/api/v1/tickets/officers', type='json', auth='none', methods=['POST'], csrf=False)
    def get_officers(self):
        """배정 가능한 IT 담당자 목록 조회 (IT 담당자/관리자 전용)"""
        req_env = get_current_request().env
        user = verify_gateway_request()
        if not (user.has_group('it_helpdesk.group_helpdesk_officer') or user._is_admin()):
            raise AccessError("Only IT officers can view officers list.")

        officer_ids = set()
        for xmlid in ('it_helpdesk.group_helpdesk_officer', 'base.group_system'):
            grp = user.env.ref(xmlid, raise_if_not_found=False)
            if grp:
                officer_ids.update(grp.users.filtered(lambda u: u.active).ids)

        officer_list = []
        for u in req_env['res.users'].sudo().browse(sorted(officer_ids)):
            if not u.exists() or u.id == 1:
                continue
            officer_list.append({
                "id": u.id,
                "name": u.name,
                "login": u.login,
            })
        return {"status": "success", "data": officer_list}
