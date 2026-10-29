# -*- coding: utf-8 -*-
"""분야별 담당자 자동 배정 (Layer 2 유틸). 실패해도 티켓 접수는 항상 성공해야 한다."""
import html
import logging

_logger = logging.getLogger(__name__)

AUTO_ASSIGN_PARAM = 'it_helpdesk.auto_assign_enabled'
OPEN_STATUSES = ('assigned', 'in_progress', 'pending')


def is_auto_assign_enabled(env):
    return env['ir.config_parameter'].sudo().get_param(AUTO_ASSIGN_PARAM) == 'True'


def pick_officer(env, category):
    """해당 분야 활성 규칙의 후보 중 진행 중 담당 건수가 가장 적은 담당자 (동률이면 id 작은 사람)."""
    env.cr.execute(
        "SELECT id FROM it_helpdesk_assign_rule WHERE category = %s AND active = true LIMIT 1 FOR UPDATE",
        [category]
    )
    row = env.cr.fetchone()
    if not row:
        return None
    rule = env['it.helpdesk.assign.rule'].sudo().browse(row[0])
    candidates = rule.officer_ids.filtered(
        lambda u: u.active and u.has_group('it_helpdesk.group_helpdesk_officer')
    )
    if not candidates:
        return None
    ticket_model = env['it.helpdesk.ticket'].sudo()

    def _load(user):
        return ticket_model.search_count([
            ('assignee_id', '=', user.id),
            ('status', 'in', OPEN_STATUSES),
        ])

    return min(candidates, key=lambda u: (_load(u), u.id))


def try_auto_assign(ticket):
    """스위치가 켜져 있고 미배정 접수대기 티켓이면 자동 배정. 배정했으면 True."""
    env = ticket.env
    if not is_auto_assign_enabled(env):
        return False
    if ticket.assignee_id or ticket.status != 'submitted':
        return False
    try:
        with env.cr.savepoint():
            target = pick_officer(env, ticket.category)
            if not target:
                return False
            sudo_ticket = ticket.sudo()
            sudo_ticket.action_assign_to_user(target)
            sudo_ticket.message_post(
                body=(
                    '<div data-msg-type="auto_assign"><b>[자동 배정]</b> '
                    '카테고리 규칙에 따라 %s 담당자가 자동 배정되었습니다.</div>'
                    % html.escape(target.name)
                ),
                subtype_xmlid='mail.mt_note',
                author_id=env.ref('base.partner_root').id,
            )
            return True
    except Exception:
        _logger.warning("자동 배정 실패 (접수는 정상 처리): ticket_id=%s", ticket.id, exc_info=True)
        ticket.invalidate_recordset()
        return False


def create_ticket_with_auto_assign(ticket_env, vals):
    """티켓 생성 후 자동 배정 및 긴급 웹훅 알림을 시도한다. 컨트롤러에서 호출."""
    from .webhook_notifier import notify_urgent_ticket_created

    ticket = ticket_env.create(vals)
    if try_auto_assign(ticket):
        ticket.invalidate_recordset()
    notify_urgent_ticket_created(ticket, use_postcommit=True)
    return ticket
