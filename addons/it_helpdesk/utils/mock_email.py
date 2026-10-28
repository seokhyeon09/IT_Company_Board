# -*- coding: utf-8 -*-
"""모의 이메일 알림 생성기 (역할별 수신 규칙 적용).

수신 규칙:
- 요청 직원(author): assigned, pending_request, resolved
- 담당 IT 담당자(assignee): assigned, follow_up, rated
- IT 담당자 전체(officer): new_ticket (미배정 접수대기 티켓)
"""
import html

from .text_utils import _clean_html, _extract_thread_content, _format_datetime_utc

SENDER_EMAIL = "it-helpdesk-noreply@company.com"
SENT_STATUS = "발송완료 (모의)"

AUTHOR_EVENTS = ("assigned", "pending_request", "resolved")
ASSIGNEE_EVENTS = ("assigned", "follow_up", "rated")


def _mail(ticket, suffix, event_type, audience, recipient, subject, body, sent_at):
    return {
        "id": f"{ticket.id}-{suffix}",
        "ticket_id": ticket.id,
        "ticket_number": ticket.ticket_number,
        "ticket_title": ticket.title,
        "event_type": event_type,
        "audience": audience,
        "recipient_id": recipient.id if recipient else None,
        "recipient_name": recipient.name if recipient else "IT 담당자",
        "recipient_email": recipient.login if recipient else "officer@test.com",
        "sender_email": SENDER_EMAIL,
        "subject": subject,
        "body_preview": body,
        "sent_at": sent_at,
        "status": SENT_STATUS,
    }


def _collect_events(ticket):
    """티켓 이력에서 발송 가능한 모든 이벤트 후보를 수집한다 (수신자 필터 이전)."""
    author = ticket.author_id
    assignee = ticket.assignee_id
    a_name = author.name if author else "요청 직원"
    s_name = assignee.name if assignee else "IT 담당자"
    num, title = ticket.ticket_number, ticket.title
    events = []

    # 미배정 신규 접수 -> 담당자 전체 대상
    if not assignee and ticket.status == 'submitted':
        events.append(_mail(
            ticket, "new", "new_ticket", "officer", None,
            f"[IT 헬프데스크] 신규 문의가 접수되었습니다 ({num})",
            f"신규 문의 '{title}' ({num}) 이(가) {a_name}님에 의해 접수되었습니다.\n"
            f"- 처리 기한(SLA): {_format_datetime_utc(ticket.deadline) or '산정 완료'}\n담당자 배정이 필요합니다.",
            _format_datetime_utc(ticket.create_date),
        ))

    has_assigned = has_resolved = False
    for msg in ticket.message_ids.sorted(key=lambda m: (m.date, m.id)):
        body = msg.body or ""
        clean_b = _clean_html(body)
        body_un = html.unescape(body)
        at = _format_datetime_utc(msg.date)
        sfx = f"msg-{msg.id}"

        if "[담당자 배정]" in clean_b or "[처리 시작]" in clean_b:
            if has_assigned:
                continue
            has_assigned = True
            events.append(_mail(
                ticket, sfx, "assigned", "author", author,
                f"[IT 헬프데스크] 담당자({s_name})가 배정되었습니다 ({num})",
                f"안녕하세요 {a_name}님,\n문의하신 '{title}' ({num}) 건에 담당자({s_name})가 배정되어 확인을 시작했습니다.",
                at,
            ))
            # 담당자용 배정 알림: 타인(관리자/동료)이 나를 지정 배정한 경우에만 발송
            # 본인이 스스로 내게 배정한 경우에는 불필요한 알림이므로 담당자 메일 발송 제외
            # msg.author_id는 res.partner이고 assignee는 res.users이므로 partner_id로 비교
            assigner = msg.author_id
            assigner_name = assigner.name if assigner else "관리자"
            is_designated = "지정 배정하였습니다" in clean_b
            is_self_assigned = bool(
                (assigner and assignee and assigner.id == assignee.partner_id.id)
                or not is_designated
            )
            if is_designated and not is_self_assigned:
                events.append(_mail(
                    ticket, sfx + "-s", "assigned", "assignee", assignee,
                    f"[IT 헬프데스크] {assigner_name}님이 회원님을 담당자로 지정했습니다 ({num})",
                    f"{s_name} 담당자님,\n{assigner_name}님이 '{title}' ({num}) 티켓의 담당자로 회원님을 지정 배정하였습니다. 확인 후 처리를 진행해 주세요.",
                    at,
                ))
        elif 'data-msg-type="pending_request"' in body_un or "[답변 대기 요청]" in clean_b:
            c = _extract_thread_content(body, ['data-msg-type="pending_request">', '[답변 대기 요청]']) or clean_b
            events.append(_mail(
                ticket, sfx, "pending_request", "author", author,
                f"[IT 헬프데스크] 추가 정보 확인 요청 안내 ({num})",
                f"안녕하세요 {a_name}님,\n담당자({s_name})가 처리를 위해 추가 정보를 요청했습니다.\n\n[요청 사유]\n{c}",
                at,
            ))
        elif ('data-msg-type="resolution"' in body_un or "IT 담당자 조치 내용:" in body_un
              or "[조치 답변]" in clean_b):
            has_resolved = True
            c = _extract_thread_content(body, [
                'data-msg-type="resolution">', 'IT 담당자 조치 내용:', '[조치 답변]', '[조치 답변 (수정)]',
            ]) or clean_b
            events.append(_mail(
                ticket, sfx, "resolved", "author", author,
                f"[IT 헬프데스크] 문의하신 건의 조치가 완료되었습니다 ({num})",
                f"안녕하세요 {a_name}님,\n'{title}' 문의에 대한 조치가 완료되었습니다.\n\n[조치 내용]\n{c}\n\n"
                f"조치 결과를 확인하시고 만족도 평가를 남겨주세요.",
                at,
            ))
        elif ('data-msg-type="inquiry"' in body or "[추가 재문의]" in clean_b
              or "[답변 대기 회신]" in clean_b):
            c = _extract_thread_content(body, [
                'data-msg-type="inquiry">', '직원 추가 재문의 내용:', '[추가 재문의]',
                'data-msg-type="pending_response">', '[답변 대기 회신]',
            ]) or clean_b
            events.append(_mail(
                ticket, sfx, "follow_up", "assignee", assignee,
                f"[IT 헬프데스크] 요청자({a_name})의 추가 회신이 등록되었습니다 ({num})",
                f"{s_name} 담당자님,\n'{title}' ({num}) 티켓에 요청자의 추가 회신/재문의가 등록되었습니다.\n\n[회신 내용]\n{c}",
                at,
            ))

    if assignee and not has_assigned:
        at = _format_datetime_utc(ticket.write_date)
        events.append(_mail(
            ticket, "assigned-a", "assigned", "author", author,
            f"[IT 헬프데스크] 담당자({s_name})가 배정되었습니다 ({num})",
            f"안녕하세요 {a_name}님,\n문의하신 '{title}' ({num}) 건에 담당자({s_name})가 배정되었습니다.", at,
        ))

    if not has_resolved and ticket.resolution_note:
        events.append(_mail(
            ticket, "resolved-a", "resolved", "author", author,
            f"[IT 헬프데스크] 문의하신 건의 조치가 완료되었습니다 ({num})",
            f"안녕하세요 {a_name}님,\n'{title}' 문의에 대한 조치가 완료되었습니다.\n\n"
            f"[조치 내용]\n{_clean_html(ticket.resolution_note)}",
            _format_datetime_utc(ticket.write_date),
        ))

    # 만족도 평가 등록 -> 담당 IT 담당자 대상
    for r in ticket.rating_ids:
        if r.rating and str(r.rating) in ('1', '2', '3', '4', '5'):
            events.append(_mail(
                ticket, f"rated-{r.id}", "rated", "assignee", assignee,
                f"[IT 헬프데스크] 만족도 평가가 등록되었습니다 ({num})",
                f"{s_name} 담당자님,\n'{title}' ({num}) 건에 {a_name}님이 만족도 {r.rating}점을 남겼습니다.",
                _format_datetime_utc(r.create_date),
            ))
    return events


def build_mock_emails(ticket, user, is_officer):
    """로그인 사용자 본인이 수신자인 모의 이메일만 반환 (최신순)."""
    result = []
    for ev in _collect_events(ticket):
        aud = ev["audience"]
        if aud == "author" and ticket.author_id.id == user.id:
            result.append(ev)
        elif aud == "assignee" and ticket.assignee_id and ticket.assignee_id.id == user.id:
            result.append(ev)
        elif aud == "officer" and is_officer:
            result.append(ev)
    result.sort(key=lambda x: x.get("sent_at") or "", reverse=True)
    return result
