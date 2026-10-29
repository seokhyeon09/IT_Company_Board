# -*- coding: utf-8 -*-
"""자동 배정 모의 이메일 이벤트 생성 (mock_email.py에서 호출)."""


def build_auto_assign_events(ticket, suffix, sent_at, mail_factory):
    """요청 사원용, 배정된 담당자용 메일 2건을 만든다. mail_factory는 mock_email._mail."""
    author = ticket.author_id
    assignee = ticket.assignee_id
    a_name = author.name if author else "요청 직원"
    s_name = assignee.name if assignee else "IT 담당자"
    num, title = ticket.ticket_number, ticket.title
    return [
        mail_factory(
            ticket, suffix + "-a", "assigned", "author", author,
            f"[IT 헬프데스크] 담당자({s_name})가 배정되었습니다 ({num})",
            f"안녕하세요 {a_name}님,\n문의하신 '{title}' ({num}) 건에 담당자({s_name})가 배정되어 확인을 시작합니다.",
            sent_at,
        ),
        mail_factory(
            ticket, suffix + "-s", "assigned", "assignee", assignee,
            f"[IT 헬프데스크] 담당 분야 문의가 자동 배정되었습니다 ({num})",
            f"{s_name} 담당자님,\n카테고리 규칙에 따라 '{title}' ({num}) 건이 자동 배정되었습니다. 확인 후 처리를 진행해 주세요.",
            sent_at,
        ),
    ]
