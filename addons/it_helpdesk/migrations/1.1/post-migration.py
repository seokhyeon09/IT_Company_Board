# -*- coding: utf-8 -*-
"""1.1 마이그레이션: 기존 해결/종결 티켓의 mail.tracking.value 이력에서 first_resolved_date 백필."""
import logging
from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def backfill_first_resolved_date(env):
    Ticket = env["it.helpdesk.ticket"].sudo()
    targets = Ticket.search([
        ("status", "in", ("resolved", "closed")),
        ("first_resolved_date", "=", False),
    ])
    updated = 0
    for ticket in targets:
        earliest_dt = None
        for msg in ticket.message_ids.sorted(key=lambda m: (m.date, m.id)):
            for tv in msg.sudo().tracking_value_ids:
                f_name = tv.field_id.name if tv.field_id else ""
                new_val = (tv.new_value_char or "").strip()
                if f_name == "status" and new_val in ("resolved", "해결완료"):
                    earliest_dt = msg.date
                    break
            if earliest_dt:
                break
        if earliest_dt:
            ticket.write({"first_resolved_date": earliest_dt})
            updated += 1
    _logger.info("MTTR 1.1 post-migration 완료: %s건 first_resolved_date 백필", updated)
    return updated


def migrate(cr, version):
    if not version:
        return
    env = api.Environment(cr, SUPERUSER_ID, {})
    backfill_first_resolved_date(env)
