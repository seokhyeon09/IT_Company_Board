# -*- coding: utf-8 -*-
"""티켓 목록 및 CSV 내보내기 공용 검색 도메인/정렬 유틸."""

ALLOWED_SORTS = {
    'id desc': 'id desc',
    'id asc': 'id asc',
    'deadline asc': 'deadline asc',
    'deadline desc': 'deadline desc',
    'priority desc': 'priority desc, id desc',
    'priority asc': 'priority asc, id desc',
    'write_date desc': 'write_date desc',
}


def build_ticket_domain(
    user,
    category=None,
    priority=None,
    status=None,
    search=None,
    is_faq=None,
    is_overdue=None,
    assigned_to_me=None,
):
    """목록 조회 및 CSV 내보내기에서 공통으로 사용하는 티켓 검색 도메인을 생성한다."""
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

    return domain
