# -*- coding: utf-8 -*-
"""중복 문의 병합 실행, 검증 및 유사 후보 추천 유틸."""
from datetime import datetime, timedelta
import html
import re

from odoo import fields
from odoo.exceptions import UserError

from .text_utils import _format_datetime_utc, _safe_html_text
from .validators import ensure_officer

MERGE_NON_SOURCE_STATUSES = ("resolved", "closed", "canceled")
MAX_MERGE_REASON_LENGTH = 500
CANDIDATE_DAYS = 30
CANDIDATE_SCAN_LIMIT = 200
MIN_JACCARD_SCORE = 0.2
_TOKEN_RE = re.compile(r"[0-9a-zA-Z가-힣]{2,}")


def _tokenize_title(title: str) -> set:
    if not title:
        return set()
    return set(_TOKEN_RE.findall(str(title).lower()))


def _jaccard_similarity(tokens_a: set, tokens_b: set) -> float:
    if not tokens_a or not tokens_b:
        return 0.0
    union = tokens_a | tokens_b
    if not union:
        return 0.0
    return len(tokens_a & tokens_b) / len(union)


def merge_tickets(user, source, target, reason=None):
    """중복 문의를 대상 문의에 병합하고 원본을 취소 처리한다."""
    ensure_officer(user)

    if source.id == target.id:
        raise UserError("같은 문의에는 병합할 수 없습니다.")
    if source.merged_into_id:
        raise UserError("이미 다른 문의에 병합된 문의입니다.")
    if source.status in MERGE_NON_SOURCE_STATUSES:
        raise UserError("처리 중인 문의만 병합할 수 있습니다.")
    if target.merged_into_id:
        raise UserError("이미 병합된 문의에는 병합할 수 없습니다.")
    if target.status == "canceled":
        raise UserError("취소된 문의에는 병합할 수 없습니다.")

    clean_reason = str(reason).strip() if reason is not None else ""
    if len(clean_reason) > MAX_MERGE_REASON_LENGTH:
        raise UserError("병합 사유는 최대 500자까지 입력할 수 있습니다.")
    if not clean_reason:
        clean_reason = "중복 문의"

    safe_reason = _safe_html_text(clean_reason)
    safe_target_num = html.escape(target.ticket_number or str(target.id))
    safe_source_num = html.escape(source.ticket_number or str(source.id))
    safe_source_title = html.escape(source.title or "")
    author_name = source.author_id.name if source.author_id else "사원"
    safe_author_name = html.escape(author_name)

    source_sudo = source.sudo()
    source_sudo.action_cancel()
    source_sudo.write({
        "merged_into_id": target.id,
        "resolution_note": f"중복 문의로 {safe_target_num}에 병합되었습니다. (사유: {safe_reason})",
    })

    author_partner_id = user.partner_id.id if user.partner_id else False
    source_sudo.message_post(
        body=(
            f'<div data-msg-type="merge"><b>[문의 병합]</b> '
            f"{safe_target_num} 문의에 병합되었습니다. (사유: {safe_reason})</div>"
        ),
        subtype_xmlid="mail.mt_note",
        author_id=author_partner_id,
    )
    target.sudo().message_post(
        body=(
            f'<div data-msg-type="internal_note"><b>[내부 메모]</b><br/>'
            f"[중복 병합] {safe_source_num} '{safe_source_title}' "
            f"(요청자: {safe_author_name}) 병합됨. 사유: {safe_reason}</div>"
        ),
        subtype_xmlid="mail.mt_note",
        author_id=author_partner_id,
    )
    return source


def find_merge_candidates(user, ticket, limit=5) -> list:
    """동일 분야 최근 30일 티켓 중 제목 토큰 자카드 유사도가 높은 병합 후보를 추천한다."""
    ensure_officer(user)
    if ticket.merged_into_id or ticket.status in MERGE_NON_SOURCE_STATUSES:
        return []

    max_results = max(1, min(int(limit or 5), 20))
    cutoff = fields.Datetime.now() - timedelta(days=CANDIDATE_DAYS)
    ticket_env = ticket.env["it.helpdesk.ticket"].with_user(user)
    candidates = ticket_env.search(
        [
            ("id", "!=", ticket.id),
            ("category", "=", ticket.category),
            ("merged_into_id", "=", False),
            ("status", "!=", "canceled"),
            ("create_date", ">=", cutoff),
        ],
        order="create_date desc, id desc",
        limit=CANDIDATE_SCAN_LIMIT,
    )

    src_tokens = _tokenize_title(ticket.title)
    scored = []
    for cand in candidates:
        score = _jaccard_similarity(src_tokens, _tokenize_title(cand.title))
        if score >= MIN_JACCARD_SCORE:
            scored.append((score, cand.create_date or datetime.min, cand.id, cand))

    scored.sort(key=lambda item: (item[0], item[1], item[2]), reverse=True)

    results = []
    for score, _dt, _cid, cand in scored[:max_results]:
        results.append({
            "id": cand.id,
            "ticket_number": cand.ticket_number,
            "title": cand.title,
            "status": cand.status,
            "author_name": cand.author_id.name if cand.author_id else "사원",
            "create_date": _format_datetime_utc(cand.create_date),
            "score": round(score, 2),
        })
    return results
