# -*- coding: utf-8 -*-
"""SLA 일시정지/준수 여부 기존 데이터 백필 유틸 (멱등)."""


def backfill_sla_fields(env):
    """기존 pending 티켓의 일시정지 시작 시각과 해결 티켓의 SLA 준수 스냅샷을 채운다."""
    Ticket = env["it.helpdesk.ticket"].sudo().with_context(
        tracking_disable=True,
        mail_notrack=True,
    )
    Message = env["mail.message"].sudo()

    pending_tickets = Ticket.search([
        ("status", "=", "pending"),
        ("sla_paused_at", "=", False),
    ])
    for ticket in pending_tickets:
        msg = Message.search([
            ("model", "=", "it.helpdesk.ticket"),
            ("res_id", "=", ticket.id),
            ("body", "ilike", 'data-msg-type="pending_request"'),
        ], order="id desc", limit=1)
        paused_at = msg.date if msg and msg.date else ticket.write_date
        if paused_at:
            ticket.write({"sla_paused_at": paused_at})

    resolved_tickets = Ticket.search([
        ("first_resolved_date", "!=", False),
        ("first_resolved_on_time", "=", False),
    ])
    if resolved_tickets:
        on_time = resolved_tickets.filtered(
            lambda t: bool(t.deadline and t.first_resolved_date <= t.deadline)
        )
        if on_time:
            on_time.write({"first_resolved_on_time": True})
