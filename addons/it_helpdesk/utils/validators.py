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
            f"Concurrency Conflict: Ticket '{ticket.ticket_number}' was modified by another transaction. "
            f"Current write_date is '{current_iso}', but provided if_match was '{if_match_write_date}'.",
            current_write_date=current_iso
        )

def ensure_officer(user):
    """Ensure user has helpdesk officer permission or is an administrator."""
    if not (user.has_group('it_helpdesk.group_helpdesk_officer') or user._is_admin()):
        raise AccessError("Only helpdesk officers can perform this action.")

def ensure_assignee_or_admin(ticket, user):
    """Ensure user is assigned officer, ticket is unassigned, or user is manager/administrator."""
    is_admin = user._is_admin() or user.has_group('it_helpdesk.group_helpdesk_manager')
    is_assignee = bool(ticket.assignee_id and ticket.assignee_id.id == user.id)
    is_unassigned = not bool(ticket.assignee_id)
    if not (is_admin or is_assignee or is_unassigned):
        raise AccessError("Only the assigned officer or a manager/administrator can perform this action.")

def ensure_author(ticket, user):
    """Ensure user is ticket author or system administrator."""
    is_admin = user._is_admin()
    is_author = bool(ticket.author_id and ticket.author_id.id == user.id)
    if not (is_admin or is_author):
        raise AccessError("Only the ticket author or an administrator can perform this action.")

def ensure_author_or_officer(ticket, user):
    """Ensure user is ticket author, assigned officer, officer, or administrator."""
    is_admin = user._is_admin()
    is_officer = user.has_group('it_helpdesk.group_helpdesk_officer')
    is_author = bool(ticket.author_id and ticket.author_id.id == user.id)
    if not (is_admin or is_officer or is_author):
        raise AccessError("Access denied.")
