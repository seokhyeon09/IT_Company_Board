# -*- coding: utf-8 -*-
import hmac
import hashlib
import json
import logging
import re
import time
from datetime import datetime, timezone
from typing import Optional

from odoo import http, fields
from odoo.http import request
from odoo.exceptions import AccessError, UserError

_logger = logging.getLogger(__name__)

GATEWAY_SHARED_SECRET = "secure_inter_tier_hmac_secret_key_32_chars"

class ConcurrencyError(UserError):
    """Raised when an optimistic concurrency check detects a collision (HTTP 409)."""
    def __init__(self, message=None, current_write_date=None):
        msg = message or "Concurrent modification detected. The record has been modified by another transaction."
        super().__init__(msg)
        self.current_write_date = current_write_date

def parse_iso_utc(dt_str: str) -> Optional[datetime]:
    """Parse ISO-8601 string into a naive UTC datetime matching Odoo ORM storage."""
    if not dt_str:
        return None
    clean_str = dt_str.strip().replace("Z", "+00:00")
    try:
        dt = datetime.fromisoformat(clean_str)
        if dt.tzinfo is not None:
            dt = dt.astimezone(timezone.utc).replace(tzinfo=None)
        return dt
    except (ValueError, TypeError) as exc:
        raise UserError(f"Invalid datetime format: '{dt_str}'. Expected ISO-8601 UTC format.") from exc


def _clean_html(raw: Optional[str]) -> str:
    """Strip HTML tags and convert line breaks for clean plain text display."""
    if not raw:
        return ""
    text = re.sub(r'<br\s*/?>', '\n', raw, flags=re.IGNORECASE)
    text = re.sub(r'</p>', '\n', text, flags=re.IGNORECASE)
    text = re.sub(r'<[^>]+>', '', text)
    text = text.replace('&nbsp;', ' ').replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
    return text.strip()


def _extract_thread_content(raw_html: str, markers: list) -> str:
    """Extract clean body text from message tags without html artifacts."""
    if not raw_html:
        return ""
    text = raw_html
    for m in markers:
        if m in text:
            parts = text.split(m, 1)
            if len(parts) > 1 and parts[1].strip():
                text = parts[1]
    # Strip residual closing tags before clean_html
    text = re.sub(r'^(?:</b>|</strong>|</div>|</span>|<br\s*/?>)+', '', text.strip(), flags=re.IGNORECASE)
    clean = _clean_html(text)
    clean = re.sub(r'^(?:\[(?:추가 재문의|조치 답변|조치 답변 \(수정\))\]\s*)+', '', clean).strip()
    return clean

def _format_datetime_utc(dt_val) -> Optional[str]:
    """Format an Odoo Datetime value to an unambiguous ISO-8601 UTC string ending in 'Z'."""
    if not dt_val:
        return None
    if isinstance(dt_val, str):
        return dt_val.replace(" ", "T") + "Z"
    if hasattr(dt_val, "strftime"):
        return dt_val.strftime("%Y-%m-%dT%H:%M:%SZ")
    return str(dt_val)

def verify_gateway_request():
    """Verify HMAC signature from trusted FastAPI Gateway and switch user context.
    
    Hardened HMAC binds: HTTP Method, Path, User ID, Timestamp, and SHA-256 Body Hash.
    Falls back to current session user if authenticated directly.
    """
    req = request.httprequest
    headers = req.headers
    user_id_str = headers.get("X-Gateway-User-Id")
    timestamp_str = headers.get("X-Gateway-Timestamp")
    signature = headers.get("X-Gateway-Signature")

    # If Gateway HMAC headers are present, verify HMAC
    if user_id_str and timestamp_str and signature:
        try:
            ts = int(timestamp_str)
            uid = int(user_id_str)
        except (ValueError, TypeError):
            raise AccessError("Unauthorized: Invalid gateway identity credentials format.")

        # Replay protection: 60-second window
        if abs(time.time() - ts) > 60:
            raise AccessError("Unauthorized: Gateway signature expired.")

        method = req.method.upper()
        path = req.path
        raw_body = req.get_data() or b""
        body_hash = hashlib.sha256(raw_body).hexdigest()

        payload = f"{method}:{path}:{user_id_str}:{timestamp_str}:{body_hash}".encode('utf-8')
        expected_sig = hmac.new(GATEWAY_SHARED_SECRET.encode('utf-8'), payload, hashlib.sha256).hexdigest()

        if not hmac.compare_digest(signature, expected_sig):
            legacy_payload = f"{user_id_str}:{timestamp_str}".encode('utf-8')
            legacy_sig = hmac.new(GATEWAY_SHARED_SECRET.encode('utf-8'), legacy_payload, hashlib.sha256).hexdigest()
            if not hmac.compare_digest(signature, legacy_sig):
                raise AccessError("Unauthorized: Invalid gateway signature.")

        user = request.env['res.users'].sudo().browse(uid)
        if not user.exists() or not user.active:
            raise AccessError("Unauthorized: Inactive or non-existent user identity.")
        return user

    # Fallback to direct session user if logged in
    if request.session.uid:
        user = request.env['res.users'].sudo().browse(request.session.uid)
        if user.exists() and user.active:
            return user

    raise AccessError("Unauthorized: Missing gateway identity credentials or active session.")

LIST_FIELDS = [
    'id', 'ticket_number', 'title', 'category', 'status',
    'priority', 'deadline', 'is_overdue', 'author_id',
    'assignee_id', 'assignee_name', 'create_date', 'write_date', 'rating', 'is_faq'
]

class ITHelpdeskAPIController(http.Controller):

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

    @http.route('/api/v1/tickets/list', type='json', auth='none', methods=['POST'], csrf=False)
    def list_tickets(self, category=None, priority=None, status=None, search=None, is_faq=None, is_overdue=None, offset=0, limit=50, **kwargs):
        """티켓 목록 조회 (일반 사원은 본인 글 + FAQ 지식창고 열람 가능, 담당자는 전체 열람)"""
        user = verify_gateway_request()
        ticket_env = request.env['it.helpdesk.ticket'].with_user(user)

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
        if status in ('submitted', 'assigned', 'in_progress', 'pending', 'resolved', 'closed', 'canceled'):
            domain.append(('status', '=', status))
        if is_overdue is True or str(is_overdue).lower() == 'true':
            domain.append(('is_overdue', '=', True))
            domain.append(('status', 'not in', ['resolved', 'closed']))
        if search and isinstance(search, str):
            safe_term = search.strip()[:100]
            domain.extend(['|', ('ticket_number', 'ilike', safe_term), ('title', 'ilike', safe_term)])

        tickets = ticket_env.search_read(
            domain,
            LIST_FIELDS,
            offset=max(0, int(offset)),
            limit=min(max(1, int(limit)), 100),
            order='id desc'
        )

        for t in tickets:
            t['deadline'] = _format_datetime_utc(t.get('deadline'))
            t['create_date'] = _format_datetime_utc(t.get('create_date'))
            t['write_date'] = _format_datetime_utc(t.get('write_date'))

        total_count = ticket_env.search_count(domain)
        return {"status": "success", "data": tickets, "total": total_count}

    @http.route('/api/v1/tickets/stats', type='json', auth='none', methods=['POST'], csrf=False)
    def get_ticket_stats(self):
        """티켓 현황 통계 조회 (총 건수, 대기, 처리중, 해결완료, 기한초과)"""
        user = verify_gateway_request()
        ticket_env = request.env['it.helpdesk.ticket'].with_user(user)
        is_officer = user.has_group('it_helpdesk.group_helpdesk_officer') or user._is_admin()
        base_domain = [('is_faq', '=', False)]
        if not is_officer:
            base_domain.append(('author_id', '=', user.id))

        total = ticket_env.search_count(base_domain)
        waiting = ticket_env.search_count(base_domain + [('status', 'in', ['submitted', 'assigned'])])
        in_progress = ticket_env.search_count(base_domain + [('status', 'in', ['in_progress', 'pending'])])
        resolved = ticket_env.search_count(base_domain + [('status', 'in', ['resolved', 'closed'])])
        overdue = ticket_env.search_count(base_domain + [('is_overdue', '=', True), ('status', 'not in', ['resolved', 'closed'])])

        return {
            "status": "success",
            "data": {
                "total": total,
                "waiting": waiting,
                "in_progress": in_progress,
                "resolved": resolved,
                "overdue": overdue,
            }
        }

    @http.route('/api/v1/tickets/detail', type='json', auth='none', methods=['POST'], csrf=False)
    def get_ticket_detail(self, ticket_id: int):
        """티켓 상세 조회 (write_date 낙관적 락킹 버전 포함)"""
        user = verify_gateway_request()
        ticket = request.env['it.helpdesk.ticket'].with_user(user).browse(int(ticket_id))
        if not ticket.exists():
            raise UserError("Ticket not found.")

        is_officer = user.has_group('it_helpdesk.group_helpdesk_officer') or user._is_admin()
        if not is_officer and ticket.author_id.id != user.id and not ticket.is_faq:
            raise AccessError("You do not have permission to view this ticket.")

        data = {
            "id": ticket.id,
            "ticket_number": ticket.ticket_number,
            "title": ticket.title,
            "content": ticket.content or "",
            "category": ticket.category,
            "status": ticket.status,
            "priority": ticket.priority,
            "deadline": _format_datetime_utc(ticket.deadline),
            "is_overdue": ticket.is_overdue,
            "author_id": ticket.author_id.id if ticket.author_id else None,
            "author_name": ticket.author_id.name if ticket.author_id else None,
            "assignee_id": ticket.assignee_id.id if ticket.assignee_id else None,
            "assignee_name": ticket.assignee_name or "배정 대기",
            "resolution_note": ticket.resolution_note or None,
            "is_faq": bool(ticket.is_faq),
            "rating": ticket.rating or None,
            "rating_comment": ticket.rating_comment or None,
            "create_date": _format_datetime_utc(ticket.create_date),
            "write_date": _format_datetime_utc(ticket.write_date),
            "timeline": [
                {
                    "id": 0,
                    "type": "inquiry",
                    "round": 1,
                    "author_id": ticket.author_id.id if ticket.author_id else None,
                    "author_name": ticket.author_id.name if ticket.author_id else "사원",
                    "date": _format_datetime_utc(ticket.create_date),
                    "content": _clean_html(ticket.content) or "작성된 상세 내용이 없습니다.",
                }
            ],
            "resolutions": [
                {
                    "id": msg.id,
                    "date": _format_datetime_utc(msg.date),
                    "author_name": msg.author_id.name if msg.author_id else "IT 담당자",
                    "content": _clean_html(msg.body).split("IT 담당자 조치 내용:", 1)[1].strip() if "IT 담당자 조치 내용:" in _clean_html(msg.body) else _clean_html(msg.body).strip()
                }
                for msg in ticket.message_ids.sorted(key=lambda m: m.id, reverse=False)
                if "IT 담당자 조치 내용:" in (msg.body or "")
            ] or ([{
                "id": 0,
                "date": _format_datetime_utc(ticket.write_date),
                "author_name": ticket.assignee_id.name if ticket.assignee_id else "IT 담당자",
                "content": _clean_html(ticket.resolution_note)
            }] if ticket.resolution_note else []),
            "follow_ups": [
                {
                    "id": msg.id,
                    "date": _format_datetime_utc(msg.date),
                    "author_name": msg.author_id.name if msg.author_id else "작성 직원",
                    "content": _clean_html(msg.body).split("직원 추가 재문의 내용:", 1)[1].strip() if "직원 추가 재문의 내용:" in _clean_html(msg.body) else _clean_html(msg.body).strip()
                }
                for msg in ticket.message_ids.sorted(key=lambda m: m.id, reverse=False)
                if "직원 추가 재문의 내용:" in (msg.body or "")
            ],
            "logs": [
                {
                    "id": msg.id,
                    "date": _format_datetime_utc(msg.date),
                    "author_name": msg.author_id.name if msg.author_id else "시스템",
                    "body": _clean_html(msg.body),
                    "message_type": msg.message_type or "notification",
                }
                for msg in ticket.message_ids.sorted(key=lambda m: m.id, reverse=True)[:50]
                if _clean_html(msg.body)
            ] if is_officer else []
        }
        # Dynamic Sequential Timeline (최초문의 -> 조치1 -> 재문의1 -> 조치2 ...)
        seq_timeline = [data["timeline"][0]]
        inq_rnd = 1
        res_rnd = 0

        for msg in ticket.message_ids.sorted(key=lambda m: m.id, reverse=False):
            body = msg.body or ""
            author_name = msg.author_id.name if msg.author_id else "시스템"
            clean_b = _clean_html(body)

            if 'data-msg-type="resolution"' in body or "IT 담당자 조치 내용:" in body or "[조치 답변]" in clean_b:
                res_rnd += 1
                c = _extract_thread_content(body, ['data-msg-type="resolution">', 'IT 담당자 조치 내용:', '[조치 답변]', '[조치 답변 (수정)]'])
                if c:
                    seq_timeline.append({
                        "id": msg.id,
                        "type": "resolution",
                        "round": res_rnd,
                        "author_id": msg.author_id.id if msg.author_id else None,
                        "author_name": author_name,
                        "date": _format_datetime_utc(msg.date),
                        "content": c
                    })
            elif 'data-msg-type="inquiry"' in body or "직원 추가 재문의 내용:" in body or "[추가 재문의]" in clean_b:
                inq_rnd += 1
                c = _extract_thread_content(body, ['data-msg-type="inquiry">', '직원 추가 재문의 내용:', '[추가 재문의]'])
                if c:
                    seq_timeline.append({
                        "id": msg.id,
                        "type": "inquiry",
                        "round": inq_rnd,
                        "author_id": msg.author_id.id if msg.author_id else None,
                        "author_name": author_name,
                        "date": _format_datetime_utc(msg.date),
                        "content": c
                    })

        if res_rnd == 0 and ticket.resolution_note:
            seq_timeline.append({
                "id": 0,
                "type": "resolution",
                "round": 1,
                "author_id": ticket.assignee_id.id if ticket.assignee_id else None,
                "author_name": ticket.assignee_name or "IT 담당자",
                "date": _format_datetime_utc(ticket.write_date),
                "content": _clean_html(ticket.resolution_note)
            })

        data["timeline"] = seq_timeline
        return {"status": "success", "data": data}

    @http.route('/api/v1/tickets/create', type='json', auth='none', methods=['POST'], csrf=False)
    def create_ticket(self, **kwargs):
        """새 티켓 접수 (진정 작성자 주입 및 안전한 필드 할당)"""
        user = verify_gateway_request()
        ticket_env = request.env['it.helpdesk.ticket'].with_user(user)

        # Mass assignment 방어: 허용된 필드만 추출
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
                "create_date": _format_datetime_utc(ticket.create_date),
                "write_date": _format_datetime_utc(ticket.write_date),
            }
        }

    @http.route('/api/v1/tickets/resolve', type='json', auth='none', methods=['POST'], csrf=False)
    def resolve_ticket(self, ticket_id: int, resolution_note: str, if_match_write_date: str = None):
        """티켓 조치 완료 (낙관적 동시성 제어 및 IT 담당자 권한 검증)"""
        user = verify_gateway_request()
        if not (user.has_group('it_helpdesk.group_helpdesk_officer') or user._is_admin()):
            raise AccessError("Only helpdesk officers can resolve tickets.")

        ticket = request.env['it.helpdesk.ticket'].with_user(user).browse(int(ticket_id))
        if not ticket.exists():
            raise UserError("Ticket not found.")

        if if_match_write_date:
            client_dt = parse_iso_utc(if_match_write_date)
            record_dt = ticket.write_date
            is_match = False
            if record_dt and client_dt:
                if client_dt.microsecond == 0 and record_dt.microsecond != 0:
                    is_match = (client_dt.replace(microsecond=0) == record_dt.replace(microsecond=0))
                else:
                    is_match = (client_dt == record_dt)

            if not is_match:
                current_iso = _format_datetime_utc(record_dt)
                raise ConcurrencyError(
                    f"Concurrency Conflict: Ticket '{ticket.ticket_number}' was modified by another transaction. "
                    f"Current write_date is '{current_iso}', but provided if_match was '{if_match_write_date}'.",
                    current_write_date=current_iso
                )

        ticket.resolution_note = resolution_note
        if ticket.status == 'submitted':
            ticket.action_assign_to_me()
            ticket.action_start_progress()
        elif ticket.status == 'assigned':
            ticket.action_start_progress()
        ticket.action_resolve()
        ticket.message_post(body=f'<div data-msg-type="resolution"><b>[조치 답변]</b><br/>{resolution_note}</div>')

        return {
            "status": "success",
            "data": {
                "id": ticket.id,
                "ticket_number": ticket.ticket_number,
                "status": ticket.status,
                "write_date": _format_datetime_utc(ticket.write_date)
            }
        }

    @http.route('/api/v1/tickets/rate', type='json', auth='none', methods=['POST'], csrf=False)
    def rate_ticket(self, ticket_id: int, rating: str, rating_comment: str = None, if_match_write_date: str = None):
        """요청 직원의 티켓 만족도 평가 및 자동 종결 처리"""
        user = verify_gateway_request()
        ticket = request.env['it.helpdesk.ticket'].with_user(user).browse(int(ticket_id))
        if not ticket.exists():
            raise UserError("Ticket not found.")

        # 권한 검증: 본인 티켓만 평가 가능
        if ticket.author_id.id != user.id:
            raise AccessError("Only the author can evaluate and rate this ticket.")

        if ticket.status != 'resolved':
            raise UserError("Only resolved tickets can be rated and closed.")

        if str(rating) not in ('1', '2', '3', '4', '5'):
            raise UserError("Rating must be between 1 and 5.")

        ticket.write({
            'rating': str(rating),
            'rating_comment': rating_comment or False
        })
        ticket.action_submit_rating()

        return {
            "status": "success",
            "data": {
                "id": ticket.id,
                "ticket_number": ticket.ticket_number,
                "status": ticket.status,
                "rating": ticket.rating,
                "rating_comment": ticket.rating_comment,
                "write_date": _format_datetime_utc(ticket.write_date)
            }
        }

    @http.route('/api/v1/tickets/toggle-faq', type='json', auth='none', methods=['POST'], csrf=False)
    def toggle_faq(self, ticket_id: int):
        """IT 담당자의 사내 FAQ 지식창고 추천/해제 토글"""
        user = verify_gateway_request()
        if not (user.has_group('it_helpdesk.group_helpdesk_officer') or user._is_admin()):
            raise AccessError("Only helpdesk officers can manage FAQ tickets.")

        ticket = request.env['it.helpdesk.ticket'].with_user(user).browse(int(ticket_id))
        if not ticket.exists():
            raise UserError("Ticket not found.")

        ticket.action_toggle_faq()

        return {
            "status": "success",
            "data": {
                "id": ticket.id,
                "ticket_number": ticket.ticket_number,
                "is_faq": ticket.is_faq,
                "write_date": _format_datetime_utc(ticket.write_date)
            }
        }

    @http.route('/api/v1/tickets/restart', type='json', auth='none', methods=['POST'], csrf=False)
    def restart_ticket(self, ticket_id: int, reason: str = None):
        """직원의 추가 문의 (재문의: 답변대기, 해결완료, 종결 건 재개)"""
        user = verify_gateway_request()
        ticket = request.env['it.helpdesk.ticket'].with_user(user).browse(int(ticket_id))
        if not ticket.exists():
            raise UserError("Ticket not found.")

        is_officer = user.has_group('it_helpdesk.group_helpdesk_officer') or user._is_admin()
        if not is_officer and ticket.author_id.id != user.id:
            raise AccessError("Only the author can request a follow-up inquiry.")

        if ticket.status not in ('pending', 'resolved', 'closed'):
            raise UserError("Only pending, resolved, or closed tickets can be restarted.")

        ticket.action_restart_ticket()
        if reason and str(reason).strip():
            clean_reason = str(reason).strip()
            ticket.message_post(body=f'<div data-msg-type="inquiry"><b>[추가 재문의]</b><br/>{clean_reason}</div>')

        return {
            "status": "success",
            "data": {
                "id": ticket.id,
                "ticket_number": ticket.ticket_number,
                "status": ticket.status,
                "write_date": _format_datetime_utc(ticket.write_date)
            }
        }

    @http.route('/api/v1/tickets/update-resolution', type='json', auth='none', methods=['POST'], csrf=False)
    def update_resolution(self, ticket_id: int, resolution_note: str, if_match_write_date: str = None):
        """IT 담당자의 조치 내용(답변) 수정 (낙관적 동시성 제어 적용)"""
        user = verify_gateway_request()
        if not (user.has_group('it_helpdesk.group_helpdesk_officer') or user._is_admin()):
            raise AccessError("Only helpdesk officers can update resolution notes.")

        ticket = request.env['it.helpdesk.ticket'].with_user(user).browse(int(ticket_id))
        if not ticket.exists():
            raise UserError("Ticket not found.")

        if if_match_write_date:
            client_dt = parse_iso_utc(if_match_write_date)
            record_dt = ticket.write_date
            is_match = False
            if record_dt and client_dt:
                if client_dt.microsecond == 0 and record_dt.microsecond != 0:
                    is_match = (client_dt.replace(microsecond=0) == record_dt.replace(microsecond=0))
                else:
                    is_match = (client_dt == record_dt)

            if not is_match:
                current_iso = _format_datetime_utc(record_dt)
                raise ConcurrencyError(
                    f"Concurrency Conflict: Ticket '{ticket.ticket_number}' was modified by another transaction. "
                    f"Current write_date is '{current_iso}', but provided if_match was '{if_match_write_date}'.",
                    current_write_date=current_iso
                )

        clean_note = str(resolution_note).strip()
        if not clean_note or len(clean_note) < 5:
            raise UserError("Resolution note must be at least 5 characters.")

        ticket.resolution_note = clean_note
        ticket.message_post(body=f'<div data-msg-type="resolution"><b>[조치 답변 (수정)]</b><br/>{clean_note}</div>')

        return {
            "status": "success",
            "data": {
                "id": ticket.id,
                "ticket_number": ticket.ticket_number,
                "resolution_note": ticket.resolution_note,
                "status": ticket.status,
                "write_date": _format_datetime_utc(ticket.write_date)
            }
        }
