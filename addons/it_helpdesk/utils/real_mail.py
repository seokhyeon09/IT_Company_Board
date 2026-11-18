# -*- coding: utf-8 -*-
"""실제 이메일 알림 발송기 (모의 이메일 이벤트 재사용, Odoo mail.mail 발송)."""
from datetime import timedelta
import html
import logging
import re

from odoo import fields

from .mock_email import SENDER_EMAIL, collect_outgoing_events
from .text_utils import _format_datetime_utc, parse_iso_utc
from .webhook_notifier import get_frontend_base_url

_logger = logging.getLogger(__name__)

PARAM_SEND_REAL_MAIL = "it_helpdesk.send_real_mail"
PARAM_SINCE = "it_helpdesk.send_real_mail_since"
PARAM_LAST_RUN = "it_helpdesk.send_real_mail_last_run"
PARAM_ALLOWED_DOMAINS = "it_helpdesk.real_mail_allowed_domains"
PARAM_MAIL_FROM = "it_helpdesk.real_mail_from"

STALE_RUN_SECONDS = 600
RETRY_COOLDOWN_SECONDS = 300
MAX_RETRY_ATTEMPTS = 3
LOOKBACK_DAYS = 2
MAX_MAILS_PER_RUN = 200
FOOTER_TEXT = "본 메일은 사내 IT 헬프데스크에서 자동 발송되었습니다. 회신하지 마세요."
AUDIENCE_GROUP_XMLIDS = {
    "officer": "it_helpdesk.group_helpdesk_officer",
    "manager": "it_helpdesk.group_helpdesk_manager",
}


def _parse_optional_utc(raw_str):
    if not raw_str:
        return None
    try:
        return parse_iso_utc(raw_str)
    except Exception:
        return None


def compute_since_window(now_utc, since_str, last_run_str, stale_seconds=STALE_RUN_SECONDS):
    """since/last_run 파라미터를 계산한다 (미설정 시 초기화, 10분 초과 중단 시 재설정)."""
    since_dt = _parse_optional_utc(since_str)
    last_run_dt = _parse_optional_utc(last_run_str)
    if since_dt is None:
        since_dt = now_utc
    elif last_run_dt is not None and (now_utc - last_run_dt).total_seconds() > stale_seconds:
        since_dt = now_utc
    return since_dt, _format_datetime_utc(since_dt), _format_datetime_utc(now_utc)


def parse_allowed_domains(raw_value):
    """쉼표 구분 허용 도메인 문자열을 소문자 집합으로 파싱한다."""
    if not raw_value:
        return set()
    return {p.strip().lstrip("@").lower() for p in str(raw_value).split(",") if p and p.strip().lstrip("@")}


def is_domain_allowed(email_addr, allowed_domains):
    """허용 도메인 집합이 비어 있거나 수신 이메일 도메인이 포함되면 True."""
    if not allowed_domains:
        return True
    if not email_addr or "@" not in email_addr:
        return False
    return email_addr.rsplit("@", 1)[-1].strip().lower() in allowed_domains


def sanitize_subject(raw_subject):
    """헤더 인젝션 방지를 위해 제목의 개행 문자를 제거한다."""
    return re.sub(r"[\r\n]+", " ", str(raw_subject or "")).strip()


def render_mail_html(ticket_id, subject, body_preview, base_url=None):
    """이벤트 본문을 안전하게 이스케이프하여 인라인 스타일 HTML 메일로 렌더링한다."""
    root = (base_url if base_url is not None else get_frontend_base_url()).rstrip("/")
    link = f"{root}/?ticket_id={ticket_id}"
    safe_subject = html.escape(sanitize_subject(subject))
    safe_body = html.escape(str(body_preview or "")).replace("\r\n", "\n").replace("\r", "\n").replace("\n", "<br/>")
    safe_link = html.escape(link, quote=True)
    return (
        '<div style="font-family: -apple-system, BlinkMacSystemFont, \'Segoe UI\', sans-serif; '
        'max-width: 600px; margin: 0 auto; padding: 20px; color: #1f2937; border: 1px solid #e5e7eb; border-radius: 8px;">'
        f'<h2 style="font-size: 16px; margin: 0 0 16px; color: #111827;">{safe_subject}</h2>'
        f'<div style="font-size: 14px; line-height: 1.6; color: #374151; margin-bottom: 20px;">{safe_body}</div>'
        '<div style="margin: 24px 0;">'
        f'<a href="{safe_link}" style="display: inline-block; padding: 10px 18px; background-color: #2563eb; '
        'color: #ffffff; text-decoration: none; border-radius: 6px; font-size: 14px; font-weight: 600;">문의 바로가기</a>'
        "</div>"
        '<hr style="border: none; border-top: 1px solid #e5e7eb; margin: 20px 0;"/>'
        f'<p style="font-size: 12px; color: #6b7280; margin: 0;">{FOOTER_TEXT}</p>'
        "</div>"
    )


def resolve_user_email(user):
    """partner_id.email 우선, 없으면 @ 포함 login을 반환한다."""
    if not user:
        return None
    partner_email = (user.partner_id.email or "").strip() if user.partner_id else ""
    login = (user.login or "").strip()
    raw = partner_email or (login if "@" in login else "")
    cleaned = re.sub(r"[\r\n]+", "", raw).strip()
    return cleaned if "@" in cleaned else None


def resolve_event_recipients(env, event):
    """이벤트를 활성 수신자 res.users 레코드셋으로 해석한다."""
    Users = env["res.users"].sudo()
    root_user = env.ref("base.user_root", raise_if_not_found=False)
    root_id = root_user.id if root_user else 1

    recipient_id = event.get("recipient_id")
    if recipient_id:
        user = Users.browse(recipient_id)
        return user if (user.exists() and user.active and user.id != root_id) else Users

    xmlid = AUDIENCE_GROUP_XMLIDS.get(event.get("audience"))
    if not xmlid:
        return Users
    grp = env.ref(xmlid, raise_if_not_found=False)
    return grp.users.filtered(lambda u: u.active and u.id != root_id) if grp else Users


def should_retry_log(log_rec, now_utc):
    """실패 이력의 재시도 가능 여부 (시도 3회 미만 및 직전 시도 후 5분 경과)."""
    if not log_rec or log_rec.state != "failed" or (log_rec.attempts or 0) >= MAX_RETRY_ATTEMPTS:
        return False
    return bool(log_rec.dispatched_at and (now_utc - log_rec.dispatched_at).total_seconds() >= RETRY_COOLDOWN_SECONDS)


def _collect_candidate_tickets(env, cutoff_dt, limit_tickets):
    Ticket = env["it.helpdesk.ticket"].sudo()
    recent_tickets = Ticket.search(
        [("write_date", ">=", cutoff_dt)], order="write_date desc, id desc", limit=limit_tickets
    )
    recent_msgs = env["mail.message"].sudo().search_read(
        [("model", "=", "it.helpdesk.ticket"), ("date", ">=", cutoff_dt), ("res_id", ">", 0)],
        ["res_id"], order="date desc, id desc", limit=limit_tickets,
    )
    msg_ids = [r["res_id"] for r in recent_msgs if r.get("res_id")]
    merged_ids = list(dict.fromkeys(msg_ids + recent_tickets.ids))[:limit_tickets]
    return Ticket.browse(merged_ids).exists()


def _record_dispatch(Dispatch, log_by_key, existing, meta, outcome):
    vals = {
        **meta,
        "email_to": meta["email_to"] or False,
        "state": outcome["state"],
        "attempts": (existing.attempts + 1) if existing else 1,
        "error": outcome.get("error") or False,
        "mail_id": outcome.get("mail_id") or False,
    }
    if existing:
        existing.write(vals)
        return existing
    rec = Dispatch.create(vals)
    log_by_key[(meta["event_key"], meta["recipient_id"])] = rec
    return rec


def _dispatch_ticket_events(env, ticket, since_dt, now_utc, ctx):
    Dispatch = env["it.helpdesk.mail.dispatch"].sudo()
    Mail = env["mail.mail"].sudo()
    existing_logs = Dispatch.search([("ticket_id", "=", ticket.id)])
    log_by_key = {(rec.event_key, rec.recipient_id.id): rec for rec in existing_logs if rec.recipient_id}

    counts = {"sent": 0, "failed": 0, "skipped": 0}
    used = 0
    for ev in collect_outgoing_events(ticket):
        if used >= ctx["remaining"]:
            break
        ev_dt = _parse_optional_utc(ev.get("sent_at"))
        if ev_dt is None or ev_dt < since_dt:
            continue

        for user in resolve_event_recipients(env, ev):
            if used >= ctx["remaining"]:
                break
            existing = log_by_key.get((ev["id"], user.id))
            if existing and not should_retry_log(existing, now_utc):
                continue

            subject = sanitize_subject(ev.get("subject") or "")
            email_to = resolve_user_email(user)
            meta = {"ticket_id": ticket.id, "event_key": ev["id"], "recipient_id": user.id, "email_to": email_to, "subject": subject, "dispatched_at": now_utc}
            if not email_to or not is_domain_allowed(email_to, ctx["allowed_domains"]):
                err_reason = "이메일 주소 없음" if not email_to else "허용되지 않은 도메인"
                _record_dispatch(Dispatch, log_by_key, existing, meta, {"state": "skipped", "error": err_reason})
                counts["skipped"] += 1
                continue

            mail = Mail.create({
                "subject": subject, "body_html": render_mail_html(ticket.id, subject, ev.get("body_preview") or ""),
                "email_from": ctx["email_from"], "email_to": email_to, "auto_delete": False,
            })
            mail.send(raise_exception=False)
            used += 1
            is_failed = mail.state == "exception"
            state = "failed" if is_failed else "sent"
            err_msg = (mail.failure_reason or "메일 발송 실패")[:255] if is_failed else False
            _record_dispatch(Dispatch, log_by_key, existing, meta, {"state": state, "error": err_msg, "mail_id": mail.id})
            counts[state] += 1

    return counts["sent"], counts["failed"], counts["skipped"], used


def cron_send_real_mail(env, limit_tickets=200):
    """실제 알림 메일 발송 크론 본체."""
    Params = env["ir.config_parameter"].sudo()
    if Params.get_param(PARAM_SEND_REAL_MAIL) != "True":
        return {"enabled": False}

    now_utc = fields.Datetime.now()
    since_dt, new_since_str, new_last_run_str = compute_since_window(
        now_utc, Params.get_param(PARAM_SINCE), Params.get_param(PARAM_LAST_RUN)
    )
    Params.set_param(PARAM_SINCE, new_since_str)
    Params.set_param(PARAM_LAST_RUN, new_last_run_str)

    ctx = {
        "email_from": (Params.get_param(PARAM_MAIL_FROM) or "").strip() or SENDER_EMAIL,
        "allowed_domains": parse_allowed_domains(Params.get_param(PARAM_ALLOWED_DOMAINS)),
        "remaining": MAX_MAILS_PER_RUN,
    }
    tickets = _collect_candidate_tickets(env, now_utc - timedelta(days=LOOKBACK_DAYS), limit_tickets)

    total_sent = total_failed = total_skipped = tickets_done = 0
    for ticket in tickets:
        if ctx["remaining"] <= 0:
            break
        try:
            with env.cr.savepoint():
                s, f, k, used = _dispatch_ticket_events(env, ticket, since_dt, now_utc, ctx)
            total_sent += s
            total_failed += f
            total_skipped += k
            ctx["remaining"] -= used
            tickets_done += 1
        except Exception:
            _logger.warning("실제 메일 발송 처리 실패 (건너뜀): ticket_id=%s", ticket.id, exc_info=True)

    return {"enabled": True, "sent": total_sent, "failed": total_failed, "skipped": total_skipped, "tickets": tickets_done}
