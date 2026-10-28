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
    serialize_ticket_detail,
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

        domain = []
        is_officer = user.has_group('it_helpdesk.group_helpdesk_officer') or user._is_admin()

        if is_faq is True:
            domain.append(('is_faq', '=', True))
        elif is_faq is False:
            domain.append(('is_faq', '=', False))
            if not is_officer:
                domain.append(('author_id', '=', user.id))
        else:
            if not is_officer:
                domain.append(('author_id', '=', user.id))

        if category in ('hw', 'sw', 'network', 'account', 'etc'):
            domain.append(('category', '=', category))
        if priority in ('0', '1', '2', '3'):
            domain.append(('priority', '=', str(priority)))
        if status == 'waiting':
            domain.append(('status', 'in', ['submitted', 'assigned']))
        elif status == 'overdue':
            domain.append(('is_overdue', '=', True))
            domain.append(('status', 'not in', ['resolved', 'closed']))
        elif status in ('submitted', 'assigned', 'in_progress', 'pending', 'resolved', 'closed', 'canceled'):
            domain.append(('status', '=', status))
        if is_overdue is True or str(is_overdue).lower() == 'true':
            domain.append(('is_overdue', '=', True))
            domain.append(('status', 'not in', ['resolved', 'closed']))
        if assigned_to_me is True or str(assigned_to_me).lower() == 'true':
            domain.append(('assignee_id', '=', user.id))

        if search and isinstance(search, str):
            safe_term = search.strip()[:100]
            domain.extend(['|', ('ticket_number', 'ilike', safe_term), ('title', 'ilike', safe_term)])

        ALLOWED_SORTS = {
            'id desc': 'id desc',
            'id asc': 'id asc',
            'deadline asc': 'deadline asc',
            'deadline desc': 'deadline desc',
            'priority desc': 'priority desc, id desc',
            'priority asc': 'priority asc, id desc',
            'write_date desc': 'write_date desc',
        }
        order_clause = ALLOWED_SORTS.get(sort_by, 'id desc') if sort_by else 'id desc'

        tickets = ticket_env.search_read(
            domain,
            LIST_FIELDS,
            offset=max(0, int(offset)),
            limit=min(max(1, int(limit)), 100),
            order=order_clause
        )

        for t in tickets:
            t['deadline'] = _format_datetime_utc(t.get('deadline'))
            t['create_date'] = _format_datetime_utc(t.get('create_date'))
            t['write_date'] = _format_datetime_utc(t.get('write_date'))

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
            raise UserError("Ticket not found.")

        is_officer = user.has_group('it_helpdesk.group_helpdesk_officer') or user._is_admin()
        if not is_officer and ticket.author_id.id != user.id and not ticket.is_faq:
            raise AccessError("You do not have permission to view this ticket.")

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
                raise UserError(f"Invalid priority '{raw_p}'. Must be '0', '1', '2', or '3'.")
            vals['priority'] = str_p

        ticket = ticket_env.create(vals)

        initial_attachments = kwargs.get('attachments')
        if initial_attachments and isinstance(initial_attachments, list):
            for att in initial_attachments:
                if isinstance(att, dict) and att.get('name') and att.get('datas'):
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
            raise UserError("Ticket not found.")

        is_officer = user.has_group('it_helpdesk.group_helpdesk_officer') or user._is_admin()
        if not is_officer and ticket.author_id.id != user.id:
            raise AccessError("Only the author can update this ticket.")

        if ticket.status != 'submitted':
            raise UserError("Only tickets in 'submitted' (waiting) status can be updated.")

        allowed = {'title', 'content', 'category', 'priority'}
        vals = {k: v for k, v in kwargs.items() if k in allowed and v is not None}

        if 'title' in vals:
            clean_title = str(vals['title']).strip()
            if not clean_title:
                raise UserError("Title cannot be empty.")
            vals['title'] = clean_title

        if 'content' in vals:
            clean_content = str(vals['content']).strip()
            if not clean_content:
                raise UserError("Content cannot be empty.")
            vals['content'] = clean_content

        if 'priority' in vals:
            str_p = str(vals['priority']).strip()
            if str_p not in {'0', '1', '2', '3'}:
                raise UserError("Invalid priority value.")
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
