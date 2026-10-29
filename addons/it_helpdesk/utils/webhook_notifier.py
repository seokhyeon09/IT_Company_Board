# -*- coding: utf-8 -*-
"""Slack 인커밍 웹훅 알림 어댑터 (Layer 2 유틸).

규칙 (D5):
- SLACK_WEBHOOK_URL 환경변수가 비어 있으면 완전히 비활성(호출 0회, 로그 0회).
- 본문(content), 첨부파일, 이메일 주소는 페이로드에 절대 포함하지 않는다.
- 전송 실패/타임아웃이 발생해도 티켓 생성이나 크론 실행은 항상 성공해야 한다.
"""
import logging
import os
from urllib.parse import urlparse

import requests

from .related_tickets import CATEGORY_LABELS
from .text_utils import _format_datetime_utc

_logger = logging.getLogger(__name__)

ALLOWED_SLACK_HOSTS = ("hooks.slack.com", "hooks.slack-gov.com")
WEBHOOK_TIMEOUT_SEC = 3.0
MAX_TITLE_LEN = 80


def get_slack_webhook_url() -> str:
    return (os.environ.get("SLACK_WEBHOOK_URL") or "").strip()


def get_frontend_base_url() -> str:
    base = (os.environ.get("FRONTEND_BASE_URL") or "http://localhost:3000").strip()
    return base.rstrip("/")


def is_valid_slack_webhook_url(url: str) -> bool:
    if not url:
        return False
    try:
        parsed = urlparse(url)
        if parsed.scheme != "https":
            return False
        host = (parsed.hostname or "").lower()
        return host in ALLOWED_SLACK_HOSTS
    except Exception:
        return False


def _truncate_title(title: str) -> str:
    clean = (title or "").strip().replace("\n", " ")
    if len(clean) > MAX_TITLE_LEN:
        return clean[:MAX_TITLE_LEN] + "..."
    return clean


def _format_slack_urgent_created(snapshot: dict) -> dict:
    """긴급(priority == '3') 티켓 접수 Slack 메시지 포맷 (본문/이메일 제외)."""
    text = (
        f"[IT 헬프데스크 긴급 문의 접수] {snapshot['ticket_number']}\n"
        f"- 제목: {snapshot['title']}\n"
        f"- 분류: {snapshot['category_label']}\n"
        f"- 요청자: {snapshot['author_name']}\n"
        f"- 담당자: {snapshot['assignee_name']}\n"
        f"- 처리 기한(SLA): {snapshot['deadline_utc']}\n"
        f"- 바로가기: {snapshot['link']}"
    )
    return {"text": text}


def _format_slack_sla_escalated(snapshot: dict) -> dict:
    """SLA 기한 초과 에스컬레이션 Slack 메시지 포맷 (본문/이메일 제외)."""
    text = (
        f"[IT 헬프데스크 SLA 기한 초과 에스컬레이션] {snapshot['ticket_number']}\n"
        f"- 제목: {snapshot['title']}\n"
        f"- 분류: {snapshot['category_label']}\n"
        f"- 현재 담당자: {snapshot['assignee_name']}\n"
        f"- 초과된 기한(SLA): {snapshot['deadline_utc']}\n"
        f"- 바로가기: {snapshot['link']}"
    )
    return {"text": text}


def _build_ticket_snapshot(ticket) -> dict:
    cat_code = ticket.category or "etc"
    return {
        "ticket_id": ticket.id,
        "ticket_number": ticket.ticket_number or f"ID-{ticket.id}",
        "title": _truncate_title(ticket.title or ""),
        "category_label": CATEGORY_LABELS.get(cat_code, cat_code),
        "author_name": ticket.author_id.name if ticket.author_id else "사원",
        "assignee_name": ticket.assignee_id.name if ticket.assignee_id else "미배정",
        "deadline_utc": _format_datetime_utc(ticket.deadline) or "미정",
        "link": f"{get_frontend_base_url()}/?ticket_id={ticket.id}",
    }


def _send_slack_payload(payload: dict) -> bool:
    url = get_slack_webhook_url()
    if not url:
        return False
    if not is_valid_slack_webhook_url(url):
        _logger.warning("Slack 웹훅 전송 생략: 유효하지 않은 URL 형식 또는 허용되지 않은 호스트입니다.")
        return False
    try:
        resp = requests.post(url, json=payload, timeout=WEBHOOK_TIMEOUT_SEC)
        if resp.status_code >= 400:
            _logger.warning("Slack 웹훅 응답 오류: status_code=%s", resp.status_code)
            return False
        return True
    except Exception:
        _logger.warning("Slack 웹훅 전송 실패 (요청 흐름은 정상 유지)", exc_info=True)
        return False


def _dispatch_webhook(env, payload: dict, use_postcommit: bool = False) -> bool:
    if not get_slack_webhook_url():
        return False
    if use_postcommit and env is not None and hasattr(env, "cr") and hasattr(env.cr, "postcommit"):
        env.cr.postcommit.add(lambda: _send_slack_payload(payload))
        return True
    return _send_slack_payload(payload)


def notify_urgent_ticket_created(ticket, use_postcommit: bool = False) -> bool:
    """긴급('3') 티켓 생성 시 Slack 인커밍 웹훅 발송."""
    if not ticket or ticket.priority != "3":
        return False
    if not get_slack_webhook_url():
        return False
    snapshot = _build_ticket_snapshot(ticket)
    payload = _format_slack_urgent_created(snapshot)
    return _dispatch_webhook(ticket.env, payload, use_postcommit=use_postcommit)


def notify_sla_escalated(ticket, use_postcommit: bool = False) -> bool:
    """SLA 초과 에스컬레이션 시점 Slack 인커밍 웹훅 발송."""
    if not ticket:
        return False
    if not get_slack_webhook_url():
        return False
    snapshot = _build_ticket_snapshot(ticket)
    payload = _format_slack_sla_escalated(snapshot)
    return _dispatch_webhook(ticket.env, payload, use_postcommit=use_postcommit)
