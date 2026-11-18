# -*- coding: utf-8 -*-
from odoo.exceptions import AccessError
from .security import ConcurrencyError
from .text_utils import parse_iso_utc, _format_datetime_utc

def check_optimistic_lock(ticket, if_match_write_date: str = None):
    """Verify write_date match for optimistic concurrency control."""
    if not if_match_write_date:
        return
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
            f"다른 사용자가 먼저 수정했습니다. 새로고침 후 다시 시도해 주세요. (문의 {ticket.ticket_number})",
            current_write_date=current_iso
        )

def ensure_officer(user):
    """Ensure user has helpdesk officer permission or is an administrator."""
    if not (user.has_group('it_helpdesk.group_helpdesk_officer') or user._is_admin()):
        raise AccessError("IT 담당자만 수행할 수 있는 작업입니다.")

def ensure_assignee_or_admin(ticket, user):
    """Ensure user is assigned officer, ticket is unassigned, or user is manager/administrator."""
    is_admin = user._is_admin() or user.has_group('it_helpdesk.group_helpdesk_manager')
    is_assignee = bool(ticket.assignee_id and ticket.assignee_id.id == user.id)
    is_unassigned = not bool(ticket.assignee_id)
    if not (is_admin or is_assignee or is_unassigned):
        raise AccessError("담당 IT 담당자 또는 관리자만 수행할 수 있는 작업입니다.")

def ensure_author(ticket, user):
    """Ensure user is ticket author or system administrator."""
    is_admin = user._is_admin()
    is_author = bool(ticket.author_id and ticket.author_id.id == user.id)
    if not (is_admin or is_author):
        raise AccessError("문의 작성자 또는 관리자만 수행할 수 있는 작업입니다.")

def ensure_author_or_officer(ticket, user):
    """Ensure user is ticket author, assigned officer, officer, or administrator."""
    is_admin = user._is_admin()
    is_officer = user.has_group('it_helpdesk.group_helpdesk_officer')
    is_author = bool(ticket.author_id and ticket.author_id.id == user.id)
    if not (is_admin or is_officer or is_author):
        raise AccessError("접근 권한이 없습니다.")
