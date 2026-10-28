# -*- coding: utf-8 -*-
"""유사 문의 연결 (동일 분류 연관 티켓/FAQ, 사원은 FAQ + 본인 티켓만 노출)"""
from .text_utils import _clean_html, _format_datetime_utc

CATEGORY_LABELS = {
    'hw': '하드웨어',
    'sw': '소프트웨어',
    'network': '네트워크',
    'account': '계정/권한',
    'etc': '기타',
}


def find_related_tickets(user, ticket, is_officer, limit=4):
    ticket_env = ticket.env['it.helpdesk.ticket'].with_user(user)
    domain = [
        ('id', '!=', ticket.id),
        ('status', '!=', 'canceled'),
        ('category', '=', ticket.category),
    ]
    if not is_officer:
        domain.extend(['|', ('is_faq', '=', True), ('author_id', '=', user.id)])

    results = []
    for rt in ticket_env.search(domain, order='is_faq desc, id desc', limit=limit):
        summary = _clean_html(rt.resolution_note) if rt.resolution_note else ""
        if len(summary) > 120:
            summary = summary[:120] + "..."
        results.append({
            "id": rt.id,
            "ticket_number": rt.ticket_number,
            "title": rt.title,
            "category": rt.category,
            "status": rt.status,
            "is_faq": bool(rt.is_faq),
            "resolution_summary": summary or None,
            "create_date": _format_datetime_utc(rt.create_date),
        })
    return results
