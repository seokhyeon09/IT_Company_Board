# -*- coding: utf-8 -*-
import os
import html
import logging
from odoo import http
from odoo.exceptions import AccessError, UserError

from ..utils import (
    _format_datetime_utc,
    verify_gateway_request,
    get_current_request,
    serialize_ticket_detail, create_ticket_with_auto_assign,
    ALLOWED_SORTS,
    build_ticket_domain,
    NotFoundError,
)

_logger = logging.getLogger(__name__)

LIST_FIELDS = [
    'id', 'ticket_number', 'title', 'category', 'status',
    'priority', 'deadline', 'is_overdue', 'author_id',
    'assignee_id', 'assignee_name', 'create_date', 'write_date', 'rating', 'is_faq'
]

class TicketQueryAPIController(http.Controller):
    """Ticket Search, Query, Detail, Creation and Updating API"""

    @http.route('/api/v1/tickets/list', type='json', auth='none', methods=['POST'], csrf=False)
    def list_tickets(self, category=None, priority=None, status=None, search=None, is_faq=None, is_overdue=None, assigned_to_me=None, sort_by=None, offset=0, limit=50, **kwargs):
        """티켓 목록 조회 (일반 사원은 본인 글 + FAQ 지식창고 열람 가능, 담당자는 전체 열람)"""
        req_env = get_current_request().env
        user = verify_gateway_request()
        ticket_env = req_env['it.helpdesk.ticket'].with_user(user)

        domain = build_ticket_domain(
            user, category, priority, status, search, is_faq, is_overdue, assigned_to_me
        )
        order_clause = ALLOWED_SORTS.get(sort_by, 'id desc') if sort_by else 'id desc'

        tickets = ticket_env.search_read(
            domain,
            LIST_FIELDS,
            offset=max(0, int(offset)),
            limit=min(max(1, int(limit)), 100),
            order=order_clause
        )

        ticket_ids = [t['id'] for t in tickets]
        merged_map = {}
        if ticket_ids:
            for rec in req_env['it.helpdesk.ticket'].sudo().browse(ticket_ids):
                if rec.merged_into_id:
                    merged_map[rec.id] = (rec.merged_into_id.id, rec.merged_into_id.ticket_number)

        for t in tickets:
            t['deadline'] = _format_datetime_utc(t.get('deadline'))
            t['create_date'] = _format_datetime_utc(t.get('create_date'))
            t['write_date'] = _format_datetime_utc(t.get('write_date'))
            m_id, m_num = merged_map.get(t['id'], (None, None))
            t['merged_into_id'] = m_id
            t['merged_into_number'] = m_num

        total_count = ticket_env.search_count(domain)
        return {"status": "success", "data": tickets, "total": total_count}

    @http.route('/api/v1/tickets/stats', type='json', auth='none', methods=['POST'], csrf=False)
    def get_ticket_stats(self):
        """티켓 현황 통계 조회"""
        req_env = get_current_request().env
        user = verify_gateway_request()
        ticket_env = req_env['it.helpdesk.ticket'].with_user(user)
        is_officer = user.has_group('it_helpdesk.group_helpdesk_officer') or user._is_admin()
        base_domain = []
        if not is_officer:
            base_domain.append(('author_id', '=', user.id))

        total = ticket_env.search_count(base_domain)
        waiting = ticket_env.search_count(base_domain + [('status', 'in', ['submitted', 'assigned'])])
        in_progress = ticket_env.search_count(base_domain + [('status', '=', 'in_progress')])
        pending = ticket_env.search_count(base_domain + [('status', '=', 'pending')])
        resolved = ticket_env.search_count(base_domain + [('status', '=', 'resolved')])
        overdue = ticket_env.search_count(base_domain + [('is_overdue', '=', True), ('status', 'not in', ['resolved', 'closed'])])

        return {
            "status": "success",
            "data": {
                "total": total,
                "waiting": waiting,
                "in_progress": in_progress,
                "pending": pending,
                "resolved": resolved,
                "overdue": overdue,
            }
        }

    @http.route('/api/v1/tickets/detail', type='json', auth='none', methods=['POST'], csrf=False)
    def get_ticket_detail(self, ticket_id: int):
        """티켓 상세 조회 (write_date 낙관적 락킹 버전 및 정밀 직렬화 포함)"""
        req_env = get_current_request().env
        user = verify_gateway_request()
        ticket = req_env['it.helpdesk.ticket'].with_user(user).browse(int(ticket_id))
        if not ticket.exists():
            raise NotFoundError("문의를 찾을 수 없습니다.")

        is_officer = user.has_group('it_helpdesk.group_helpdesk_officer') or user._is_admin()
        if not is_officer and ticket.author_id.id != user.id and not ticket.is_faq:
            raise AccessError("이 문의를 조회할 권한이 없습니다.")

        data = serialize_ticket_detail(ticket, user, req_env)
        return {"status": "success", "data": data}

    @http.route('/api/v1/tickets/create', type='json', auth='none', methods=['POST'], csrf=False)
    def create_ticket(self, **kwargs):
        """새 티켓 접수 (진정 작성자 주입 및 안전한 필드 할당)"""
        req_env = get_current_request().env
        user = verify_gateway_request()
        ticket_env = req_env['it.helpdesk.ticket'].with_user(user)

        allowed = {'title', 'content', 'category', 'priority'}
        vals = {k: v for k, v in kwargs.items() if k in allowed}
        vals['author_id'] = user.id

        if 'priority' in vals:
            raw_p = vals['priority']
            str_p = str(raw_p).strip() if raw_p is not None else '1'
            if str_p not in {'0', '1', '2', '3'}:
                raise UserError(f"긴급도 값이 올바르지 않습니다. ('{raw_p}')")
            vals['priority'] = str_p

        ticket = create_ticket_with_auto_assign(ticket_env, vals)

        initial_attachments = kwargs.get('attachments')
        if initial_attachments and isinstance(initial_attachments, list):
            for att in initial_attachments:
                if isinstance(att, dict) and att.get('name') and att.get('datas') and len(att['datas']) <= 7_000_000:
                    req_env['ir.attachment'].sudo().create({
                        'name': os.path.basename(str(att['name'])),
                        'datas': att['datas'],
                        'res_model': 'it.helpdesk.ticket',
                        'res_id': ticket.id,
                        'mimetype': att.get('mimetype') or 'application/octet-stream',
                    })

        return {
            "status": "success",
            "data": {
                "id": ticket.id,
                "ticket_number": ticket.ticket_number,
                "title": ticket.title,
                "category": ticket.category,
                "status": ticket.status,
                "priority": ticket.priority,
                "deadline": _format_datetime_utc(ticket.deadline),
                "is_overdue": ticket.is_overdue,
                "author_id": ticket.author_id.id,
                "assignee_id": ticket.assignee_id.id if ticket.assignee_id else None,
                "assignee_name": ticket.assignee_id.name if ticket.assignee_id else "배정 대기",
                "create_date": _format_datetime_utc(ticket.create_date),
                "write_date": _format_datetime_utc(ticket.write_date),
            }
        }

    @http.route('/api/v1/tickets/update', type='json', auth='none', methods=['POST'], csrf=False)
    def update_ticket(self, ticket_id: int, **kwargs):
        """접수대기(submitted) 상태에서의 작성자 본인 티켓 내용 수정"""
        req_env = get_current_request().env
        user = verify_gateway_request()
        ticket = req_env['it.helpdesk.ticket'].with_user(user).browse(int(ticket_id))
        if not ticket.exists():
            raise NotFoundError("문의를 찾을 수 없습니다.")

        is_officer = user.has_group('it_helpdesk.group_helpdesk_officer') or user._is_admin()
        if not is_officer and ticket.author_id.id != user.id:
            raise AccessError("작성자만 문의를 수정할 수 있습니다.")

        if ticket.status != 'submitted':
            raise UserError("접수대기 상태의 문의만 수정할 수 있습니다.")

        allowed = {'title', 'content', 'category', 'priority'}
        vals = {k: v for k, v in kwargs.items() if k in allowed and v is not None}

        if 'title' in vals:
            clean_title = str(vals['title']).strip()
            if not clean_title:
                raise UserError("제목을 입력해 주세요.")
            vals['title'] = clean_title

        if 'content' in vals:
            clean_content = str(vals['content']).strip()
            if not clean_content:
                raise UserError("내용을 입력해 주세요.")
            vals['content'] = clean_content

        if 'priority' in vals:
            str_p = str(vals['priority']).strip()
            if str_p not in {'0', '1', '2', '3'}:
                raise UserError("긴급도 값이 올바르지 않습니다.")
            vals['priority'] = str_p

        ticket.write(vals)
        ticket.message_post(body=f"<b>[문의 내용 수정]</b><br/>작성자({html.escape(user.name)})가 접수 대기 중 문의 내용을 수정하였습니다.")

        return {
            "status": "success",
            "data": {
                "id": ticket.id,
                "ticket_number": ticket.ticket_number,
                "title": ticket.title,
                "category": ticket.category,
                "status": ticket.status,
                "priority": ticket.priority,
                "deadline": _format_datetime_utc(ticket.deadline),
                "is_overdue": ticket.is_overdue,
                "author_id": ticket.author_id.id,
                "assignee_id": ticket.assignee_id.id if ticket.assignee_id else None,
                "assignee_name": ticket.assignee_id.name if ticket.assignee_id else "배정 대기",
                "create_date": _format_datetime_utc(ticket.create_date),
                "write_date": _format_datetime_utc(ticket.write_date),
                "is_faq": ticket.is_faq,
                "rating": ticket.rating or None,
            }
        }
