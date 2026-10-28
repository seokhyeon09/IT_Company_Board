# -*- coding: utf-8 -*-
"""
IT Helpdesk 3-Tier System - Idempotent Demo Data Seed Script
Usage: python scripts/seed_demo_data.py
"""
import os
import sys
import subprocess
from datetime import datetime, timedelta

try:
    import odoo
except ImportError:
    script_path = os.path.abspath(__file__)
    with open(script_path, "rb") as f:
        res = subprocess.run(
            ["docker", "exec", "-i", "it_helpdesk_odoo", "python3", "-"],
            input=f.read(),
        )
    sys.exit(res.returncode)

DB_NAME = os.environ.get("ODOO_DB", "helpdesk_db")
DB_HOST = os.environ.get("HOST", "db")
DB_USER = os.environ.get("USER", "odooU")
DB_PASSWORD = os.environ.get("PASSWORD", "odooPW")

USERS_SPEC = [
    {"login": "admin@helpdesk.com", "name": "Administrator", "password": "admin", "is_officer": True, "is_admin": True},
    {"login": "officer@test.com", "name": "officer@test.com", "password": "1234", "is_officer": True, "is_admin": False},
    {"login": "officer2@test.com", "name": "박엔지니어 (IT 보안/네트워크)", "password": "1234", "is_officer": True, "is_admin": False},
    {"login": "user1@test.com", "name": "user1@test.com", "password": "1234", "is_officer": False, "is_admin": False},
    {"login": "user2@test.com", "name": "User 2 (사원)", "password": "1234", "is_officer": False, "is_admin": False},
]

TICKETS_SPEC = [
    {
        "title": "[SEED] 신규 입사자 개발용 노트북 및 듀얼 모니터 지급 요청",
        "category": "hw", "priority": "1", "status": "submitted",
        "author": "user1@test.com", "assignee": None,
        "content": "<p>다음 주 월요일 입사 예정인 백엔드 개발자용 장비(노트북 1대, 27인치 모니터 2대) 세팅을 요청드립니다.</p>",
    },
    {
        "title": "[SEED] 사내 그룹웨어 SSO 인증 토큰 만료 반복 현상 점검",
        "category": "account", "priority": "3", "status": "assigned",
        "author": "user2@test.com", "assignee": "officer@test.com",
        "content": "<p>오전부터 그룹웨어 접속 시 5분마다 SSO 세션이 만료되어 재로그인 창이 뜹니다. 긴급 확인 부탁드립니다.</p>",
    },
    {
        "title": "[SEED] 본사 4층 대회의실 무선 Wi-Fi AP 간헐적 끊김 현상",
        "category": "network", "priority": "2", "status": "in_progress",
        "author": "user1@test.com", "assignee": "officer@test.com", "overdue_hours": 6,
        "content": "<p>화상회의 진행 중 4층 대회의실 Wi-Fi 신호가 자주 끊깁니다. 채널 간섭 및 AP 장비 점검 요청드립니다.</p>",
    },
    {
        "title": "[SEED] ERP 결산 보고서 PDF 변환 시 폰트 깨짐 오류",
        "category": "sw", "priority": "2", "status": "pending",
        "author": "user1@test.com", "assignee": "officer2@test.com",
        "pending_reason": "오류가 발생하는 문서 양식 번호와 사용 중인 브라우저 버전을 회신 부탁드립니다.",
        "content": "<p>월간 결산 보고서를 PDF로 내보내기 하면 한글 표 헤더가 네모 박스로 깨져서 출력됩니다.</p>",
    },
    {
        "title": "[SEED] 재택근무 사내 VPN 클라이언트 접속 불가 시 해결 방법",
        "category": "network", "priority": "2", "status": "resolved",
        "author": "user1@test.com", "assignee": "officer@test.com", "is_faq": True,
        "resolution_note": "1. 기존 VPN 클라이언트를 종료합니다.\n2. 네트워크 어댑터 설정에서 가상 TAP 드라이버를 재시작합니다.\n3. 사내 포털에서 최신 인증서 프로파일(v2.4)을 내려받아 재적용하면 정상 접속됩니다.",
        "content": "<p>재택근무 환경에서 VPN 접속 시 809 포트 연결 시간 초과 오류가 발생합니다.</p>",
    },
    {
        "title": "[SEED] 사내 공용 복합기 네트워크 스캔 폴더(SMB) 연결 가이드",
        "category": "hw", "priority": "1", "status": "closed",
        "author": "user2@test.com", "assignee": "officer@test.com", "is_faq": True,
        "rating": "5", "rating_comment": "단계별 설명이 명확해서 바로 스캔 폴더 연결을 완료했습니다. 감사합니다.",
        "resolution_note": "복합기 주소록에서 본인 사번 폴더 경로(\\\\10.10.20.5\\scan\\사번)를 등록하고 SMBv3 자격증명에 AD 계정 비밀번호를 입력하여 조치 완료했습니다.",
        "content": "<p>윈도우 비밀번호 변경 이후 복합기에서 PC로 스캔 파일 전송이 되지 않습니다.</p>",
    },
    {
        "title": "[SEED] 외부 협력사 임시 계정 발급 및 방화벽 예외 신청 절차 안내",
        "category": "account", "priority": "1", "status": "closed",
        "author": "user1@test.com", "assignee": "officer2@test.com", "is_faq": True,
        "rating": "4", "rating_comment": "임시 계정 발급 절차를 빠르게 안내해 주셔서 프로젝트 일정에 도움이 되었습니다.",
        "resolution_note": "보안서약서 징구 확인 후 협력사 전용 VLAN 계정 발급을 완료했습니다. 계정 유효기간은 최대 90일이며 만료 7일 전 연장 신청이 필요합니다.",
        "content": "<p>신규 외주 개발 인력 2명에 대한 사내 테스트 서버 접근 계정 발급 절차를 문의합니다.</p>",
    },
    {
        "title": "[SEED] 보조 모니터 연결용 HDMI 케이블 추가 신청 (자체 해결 취소)",
        "category": "etc", "priority": "0", "status": "canceled",
        "author": "user2@test.com", "assignee": None,
        "content": "<p>자리 이동 후 HDMI 케이블이 부족하여 신청합니다. (부서 내 여분 확인으로 취소)</p>",
    },
]


def ensure_users(env):
    Users = env["res.users"].sudo()
    grp_user = env.ref("base.group_user")
    grp_officer = env.ref("it_helpdesk.group_helpdesk_officer")
    grp_system = env.ref("base.group_system")
    user_map = {}

    for spec in USERS_SPEC:
        user = Users.search([("login", "=", spec["login"])], limit=1)
        groups = [(4, grp_user.id), (4 if spec["is_officer"] else 3, grp_officer.id)]
        if spec["is_admin"]:
            groups.append((4, grp_system.id))

        if not user:
            user = Users.create({
                "name": spec["name"],
                "login": spec["login"],
                "email": spec["login"],
                "password": spec["password"],
                "groups_id": groups,
            })
            print(f"[SEED] Created user: {spec['login']} (ID={user.id})")
        else:
            user.write({"password": spec["password"], "groups_id": groups})
            print(f"[SEED] Verified user: {spec['login']} (ID={user.id})")
        user_map[spec["login"]] = user
    return user_map


def ensure_tickets(env, user_map):
    Ticket = env["it.helpdesk.ticket"].sudo()
    now = datetime.utcnow()

    for spec in TICKETS_SPEC:
        existing = Ticket.search([("title", "=", spec["title"])], limit=1)
        if existing:
            print(f"[SEED] Ticket already exists: {existing.ticket_number} - {spec['title']}")
            continue

        author = user_map[spec["author"]]
        assignee = user_map[spec["assignee"]] if spec.get("assignee") else False
        ticket = Ticket.with_user(author).create({
            "title": spec["title"],
            "category": spec["category"],
            "priority": spec["priority"],
            "status": "submitted",
            "author_id": author.id,
            "content": spec["content"],
            "is_faq": spec.get("is_faq", False),
        }).sudo()

        if assignee:
            ticket.action_assign_to_user(assignee)

        target_status = spec["status"]
        if target_status in ("in_progress", "pending", "resolved", "closed"):
            ticket.action_start_progress()
        if target_status == "pending":
            ticket.pending_reason = spec.get("pending_reason", "추가 확인 요청")
            ticket.action_pending()
            ticket.message_post(body=f'<div data-msg-type="pending_request"><b>[답변 대기 요청]</b><br/>{ticket.pending_reason}</div>')
        if target_status in ("resolved", "closed"):
            ticket.resolution_note = spec.get("resolution_note", "조치 완료")
            ticket.action_resolve()
            ticket.message_post(body=f'<div data-msg-type="resolution"><b>[조치 답변]</b><br/>{ticket.resolution_note}</div>')
        if target_status == "closed":
            if spec.get("rating"):
                ticket.rating = spec["rating"]
                ticket.rating_comment = spec.get("rating_comment", "")
                ticket.with_user(author).action_submit_rating()
            else:
                ticket.action_close()
        if target_status == "canceled":
            ticket.with_user(author).action_cancel()

        if spec.get("overdue_hours"):
            ticket.write({"deadline": now - timedelta(hours=int(spec["overdue_hours"])), "is_overdue": True})

        print(f"[SEED] Created ticket: {ticket.ticket_number} ({target_status}) - {spec['title']}")


def main():
    odoo.tools.config.parse_config(["-d", DB_NAME, f"--db_host={DB_HOST}", "-r", DB_USER, "-w", DB_PASSWORD])
    registry = odoo.modules.registry.Registry(DB_NAME)
    with registry.cursor() as cr:
        env = odoo.api.Environment(cr, odoo.SUPERUSER_ID, {})
        print("=" * 68)
        print("[SEED] Starting Idempotent Demo Data Seeding for IT Helpdesk...")
        print("=" * 68)
        user_map = ensure_users(env)
        ensure_tickets(env, user_map)
        cr.commit()
        print("=" * 68)
        print("[SEED] Demo Data Seeding Completed Successfully.")
        print("=" * 68)


if __name__ == "__main__":
    main()
