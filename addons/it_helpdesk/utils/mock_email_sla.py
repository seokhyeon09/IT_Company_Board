# -*- coding: utf-8 -*-
"""SLA 임박 경고 및 관리자 에스컬레이션 모의 이메일 이벤트 생성기 (Layer 2 유틸)."""
import re

from .text_utils import _clean_html, _format_datetime_utc


def build_sla_warning_events(ticket, sfx, sent_at, mail_fn):
    """SLA 임박 경고: 배정된 담당자(없으면 담당자 전체)에게 발송."""
    assignee = ticket.assignee_id
    s_name = assignee.name if assignee else "IT 담당자"
    num, title = ticket.ticket_number, ticket.title
    dl_str = _format_datetime_utc(ticket.deadline) or "기한 임박"

    if assignee:
        return [
            mail_fn(
                ticket, f"{sfx}-sla-warn", "sla_warning", "assignee", assignee,
                f"[IT 헬프데스크] SLA 마감 임박 경고 ({num})",
                f"{s_name} 담당자님,\n담당 중인 '{title}' ({num}) 티켓의 처리 기한({dl_str})이 임박했습니다.\n"
                f"기한 초과 전에 조치를 완료하거나 진행 상황을 점검해 주세요.",
                sent_at,
            )
        ]
    return [
        mail_fn(
            ticket, f"{sfx}-sla-warn", "sla_warning", "officer", None,
            f"[IT 헬프데스크] 미배정 티켓 SLA 마감 임박 경고 ({num})",
            f"미배정 상태인 '{title}' ({num}) 티켓의 처리 기한({dl_str})이 임박했습니다.\n"
            f"즉시 담당자 배정 및 조치가 필요합니다.",
            sent_at,
        )
    ]


def build_sla_escalation_events(ticket, sfx, sent_at, mail_fn):
    """SLA 초과 에스컬레이션: IT 관리자(manager) 전원 및 담당자(assignee)에게 발송."""
    assignee = ticket.assignee_id
    s_name = assignee.name if assignee else "미배정"
    num, title = ticket.ticket_number, ticket.title
    dl_str = _format_datetime_utc(ticket.deadline) or "기한 초과"

    events = [
        mail_fn(
            ticket, f"{sfx}-sla-esc-m", "sla_escalation", "manager", None,
            f"[IT 헬프데스크] SLA 기한 초과 에스컬레이션 보고 ({num})",
            f"IT 관리자님,\n'{title}' ({num}) 티켓의 처리 기한({dl_str})이 초과되었습니다.\n"
            f"- 현재 담당자: {s_name}\n담당자 재배정 또는 우선 조치를 검토해 주세요.",
            sent_at,
        )
    ]
    if assignee:
        events.append(
            mail_fn(
                ticket, f"{sfx}-sla-esc-a", "sla_escalation", "assignee", assignee,
                f"[IT 헬프데스크] 담당 티켓 SLA 기한 초과 알림 ({num})",
                f"{s_name} 담당자님,\n담당 중인 '{title}' ({num}) 티켓의 처리 기한({dl_str})이 초과되어 "
                f"관리자에게 에스컬레이션되었습니다. 조속히 처리해 주세요.",
                sent_at,
            )
        )
    return events


def build_escalation_rule_events(ticket, sfx, sent_at, mail_fn, body_un):
    """에스컬레이션 규칙 알림: 규칙의 수신 대상(없으면 관리자 전체)에게 발송."""
    num, title = ticket.ticket_number, ticket.title
    preview = _clean_html(body_un)
    match = re.search(r'data-recipient-ids="([\d,]+)"', body_un or "")
    if match:
        uids = [int(x) for x in match.group(1).split(",") if x.isdigit()]
        users = ticket.env["res.users"].sudo().browse(uids).exists().filtered(lambda u: u.active)
        if users:
            return [
                mail_fn(
                    ticket, f"{sfx}-esc-rule-{u.id}", "escalation_rule", "officer", u,
                    f"[IT 헬프데스크] 에스컬레이션 규칙 알림 ({num})",
                    f"{u.name}님,\n'{title}' ({num}) 티켓이 에스컬레이션 규칙 대상에 해당합니다.\n\n{preview}",
                    sent_at,
                )
                for u in users
            ]
    return [
        mail_fn(
            ticket, f"{sfx}-esc-rule-m", "escalation_rule", "manager", None,
            f"[IT 헬프데스크] 에스컬레이션 규칙 알림 ({num})",
            f"IT 관리자님,\n'{title}' ({num}) 티켓이 에스컬레이션 규칙 대상에 해당합니다.\n\n{preview}",
            sent_at,
        )
    ]
