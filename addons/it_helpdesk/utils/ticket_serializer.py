# -*- coding: utf-8 -*-
import html
from .text_utils import (
    _format_datetime_utc,
    _clean_html,
    _extract_thread_content,
)
from .related_tickets import find_related_tickets
from .mock_email import build_mock_emails

def build_sequential_timeline(ticket, initial_inquiry: dict) -> list:
    """Build chronological multi-round Q&A sequential timeline."""
    seq_timeline = [initial_inquiry]
    has_resolution_msg = False

    for msg in ticket.message_ids.sorted(key=lambda m: (m.date, m.id), reverse=False):
        body = msg.body or ""
        author_name = msg.author_id.name if msg.author_id else "시스템"
        clean_b = _clean_html(body)
        body_un = html.unescape(body)

        if 'data-msg-type="resolution"' in body_un or "IT 담당자 조치 내용:" in body_un or "[조치 답변]" in body_un or "[조치 답변]" in clean_b:
            has_resolution_msg = True
            c = _extract_thread_content(body, ['data-msg-type="resolution">', 'IT 담당자 조치 내용:', '[조치 답변]', '[조치 답변 (수정)]'])
            if c:
                seq_timeline.append({
                    "id": msg.id,
                    "type": "resolution",
                    "round": 1,
                    "author_id": msg.author_id.id if msg.author_id else None,
                    "author_name": author_name,
                    "date": _format_datetime_utc(msg.date),
                    "content": c,
                })
        elif 'data-msg-type="pending_request"' in body_un or "[답변 대기 요청]" in body_un or "[답변 대기 요청]" in clean_b:
            c = _extract_thread_content(body, ['data-msg-type="pending_request">', '[답변 대기 요청]'])
            if c:
                seq_timeline.append({
                    "id": msg.id,
                    "type": "pending_request",
                    "round": 0,
                    "author_id": msg.author_id.id if msg.author_id else None,
                    "author_name": author_name,
                    "date": _format_datetime_utc(msg.date),
                    "content": c,
                })
        elif 'data-msg-type="pending_response"' in body_un or "[답변 대기 회신]" in body_un or "[답변 대기 회신]" in clean_b:
            c = _extract_thread_content(body, ['data-msg-type="pending_response">', '[답변 대기 회신]'])
            if c:
                seq_timeline.append({
                    "id": msg.id,
                    "type": "pending_response",
                    "round": 0,
                    "author_id": msg.author_id.id if msg.author_id else None,
                    "author_name": author_name,
                    "date": _format_datetime_utc(msg.date),
                    "content": c,
                })
        elif 'data-msg-type="inquiry"' in body or "직원 추가 재문의 내용:" in body or "[추가 재문의]" in clean_b:
            c = _extract_thread_content(body, ['data-msg-type="inquiry">', '직원 추가 재문의 내용:', '[추가 재문의]'])
            if c:
                seq_timeline.append({
                    "id": msg.id,
                    "type": "inquiry",
                    "round": 1,
                    "author_id": msg.author_id.id if msg.author_id else None,
                    "author_name": author_name,
                    "date": _format_datetime_utc(msg.date),
                    "content": c,
                })
        elif 'data-msg-type="reassign"' in body_un or "[담당자 변경]" in clean_b:
            c = _extract_thread_content(body, ['data-msg-type="reassign">', '[담당자 변경]']) or clean_b
            seq_timeline.append({
                "id": msg.id,
                "type": "reassign",
                "round": 0,
                "author_id": msg.author_id.id if msg.author_id else None,
                "author_name": author_name,
                "date": _format_datetime_utc(msg.date),
                "content": c,
            })

    if not has_resolution_msg and ticket.resolution_note:
        seq_timeline.append({
            "id": 0,
            "type": "resolution",
            "round": 1,
            "author_id": ticket.assignee_id.id if ticket.assignee_id else None,
            "author_name": ticket.assignee_name or "IT 담당자",
            "date": _format_datetime_utc(ticket.write_date),
            "content": _clean_html(ticket.resolution_note),
        })

    has_pending_msg = any(item["type"] == "pending_request" for item in seq_timeline)
    if not has_pending_msg and ticket.pending_reason and ticket.status == 'pending':
        seq_timeline.append({
            "id": 0,
            "type": "pending_request",
            "round": 0,
            "author_id": ticket.assignee_id.id if ticket.assignee_id else None,
            "author_name": ticket.assignee_name or "IT 담당자",
            "date": _format_datetime_utc(ticket.write_date),
            "content": _clean_html(ticket.pending_reason),
        })

    seq_timeline.sort(key=lambda x: (x.get("date") or "", x.get("id", 0)))

    inquiry_idx = 1
    resolution_idx = 1
    for item in seq_timeline:
        if item["type"] == "inquiry":
            item["round"] = inquiry_idx
            inquiry_idx += 1
        elif item["type"] == "resolution":
            item["round"] = resolution_idx
            resolution_idx += 1

    return seq_timeline

def serialize_ticket_summary(ticket) -> dict:
    """Serialize basic ticket fields for list and quick cards."""
    return {
        "id": ticket.id,
        "ticket_number": ticket.ticket_number,
        "title": ticket.title,
        "category": ticket.category,
        "status": ticket.status,
        "priority": ticket.priority,
        "deadline": _format_datetime_utc(ticket.deadline),
        "is_overdue": ticket.is_overdue,
        "author_id": ticket.author_id.id if ticket.author_id else None,
        "assignee_id": ticket.assignee_id.id if ticket.assignee_id else None,
        "assignee_name": ticket.assignee_name or "배정 대기",
        "create_date": _format_datetime_utc(ticket.create_date),
        "write_date": _format_datetime_utc(ticket.write_date),
        "is_faq": bool(ticket.is_faq),
        "rating": ticket.rating or None,
    }

def serialize_ticket_detail(ticket, user, req_env) -> dict:
    """Serialize full ticket details including chatter timeline, attachments, logs, and emails."""
    is_officer = user.has_group('it_helpdesk.group_helpdesk_officer') or user._is_admin()

    att_records = req_env['ir.attachment'].sudo().search([
        ('res_model', '=', 'it.helpdesk.ticket'),
        ('res_id', '=', ticket.id)
    ])
    ticket_attachments = [
        {
            "id": att.id,
            "name": att.name,
            "mimetype": att.mimetype,
            "file_size": att.file_size,
            "create_date": _format_datetime_utc(att.create_date),
        }
        for att in att_records
    ]

    initial_inquiry = {
        "id": 0,
        "type": "inquiry",
        "round": 1,
        "author_id": ticket.author_id.id if ticket.author_id else None,
        "author_name": ticket.author_id.name if ticket.author_id else "사원",
        "date": _format_datetime_utc(ticket.create_date),
        "content": _clean_html(ticket.content) or "작성된 상세 내용이 없습니다.",
    }

    seq_timeline = build_sequential_timeline(ticket, initial_inquiry)

    read_records = req_env['it.helpdesk.notification.read'].sudo().search([
        ('user_id', '=', user.id),
        ('ticket_id', '=', ticket.id)
    ])
    read_notification_ids = set(read_records.mapped('notification_id'))

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
        "pending_reason": ticket.pending_reason or None,
        "create_date": _format_datetime_utc(ticket.create_date),
        "write_date": _format_datetime_utc(ticket.write_date),
        "timeline": seq_timeline,
        "attachments": ticket_attachments,
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
        ] if is_officer else [],
        "related_tickets": find_related_tickets(ticket, req_env),
        "email_notifications": build_mock_emails(ticket, user, read_notification_ids),
    }

    return data
