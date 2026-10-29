# -*- coding: utf-8 -*-
"""
IT Helpdesk Demo Seed Specifications (Layer 1 Data Contract)
All demo account specifications and ticket scenario configurations.
"""
import base64

USERS_SPEC = [
    {
        "login": "admin@helpdesk.com",
        "name": "최관리 (IT 센터장/관리자)",
        "password": "admin",
        "is_officer": True,
        "is_manager": True,
        "is_admin": True,
    },
    {
        "login": "officer@test.com",
        "name": "김담당 (IT 인프라/시스템)",
        "password": "1234",
        "is_officer": True,
        "is_manager": False,
        "is_admin": False,
    },
    {
        "login": "officer2@test.com",
        "name": "박엔지니어 (IT 보안/네트워크)",
        "password": "1234",
        "is_officer": True,
        "is_manager": False,
        "is_admin": False,
    },
    {
        "login": "officer3@test.com",
        "name": "최소프트 (소프트웨어/라이선스)",
        "password": "1234",
        "is_officer": True,
        "is_manager": False,
        "is_admin": False,
    },
    {
        "login": "officer4@test.com",
        "name": "한계정 (계정/권한 관리)",
        "password": "1234",
        "is_officer": True,
        "is_manager": False,
        "is_admin": False,
    },
    {
        "login": "officer5@test.com",
        "name": "오기타 (총무/기타 지원)",
        "password": "1234",
        "is_officer": True,
        "is_manager": False,
        "is_admin": False,
    },
    {
        "login": "user1@test.com",
        "name": "이개발 (백엔드개발팀 사원)",
        "password": "1234",
        "is_officer": False,
        "is_manager": False,
        "is_admin": False,
    },
    {
        "login": "user2@test.com",
        "name": "정기획 (서비스기획팀 사원)",
        "password": "1234",
        "is_officer": False,
        "is_manager": False,
        "is_admin": False,
    },
]

# 분야(카테고리)별 전담 담당자 (분야 -> 담당자 로그인 목록). 복수 지정 시 진행 건수가 적은 담당자에게 배정.
ASSIGN_RULES_SPEC = {
    "hw": ["officer@test.com"],
    "network": ["officer2@test.com"],
    "sw": ["officer3@test.com"],
    "account": ["officer4@test.com"],
    "etc": ["officer5@test.com"],
}

SAMPLE_LOG_B64 = base64.b64encode(
    b"[2026-10-29 08:55:12] ERROR vpn_client: TLS Handshake timeout on 10.10.10.1:809\n"
    b"[2026-10-29 08:55:15] WARN  tap_driver: Network adapter media state disconnected\n"
    b"[2026-10-29 08:55:20] INFO  vpn_client: Retrying connection (attempt 2/5)...\n"
).decode("ascii")

TICKETS_SPEC = [
    {
        "title": "[SEED] 신규 입사자 고성능 개발용 노트북 및 듀얼 모니터 세팅 요청",
        "category": "hw", "priority": "1", "status": "submitted",
        "author": "user1@test.com", "assignee": None,
        "content": "<p>다음 주 입사 예정인 백엔드 개발자용 노트북 및 27인치 모니터 2대 세팅을 요청드립니다.</p>",
        "attachment": {"name": "hardware_spec_req.log", "datas": SAMPLE_LOG_B64, "mimetype": "text/plain"},
    },
    {
        "title": "[SEED] 전사 공용 회의실 프로젝터 리모컨 및 HDMI 젠더 분실 확인",
        "category": "etc", "priority": "0", "status": "submitted",
        "author": "user2@test.com", "assignee": None,
        "content": "<p>5층 중회의실 프로젝터 전원 리모컨이 분실되어 예비품 지급 또는 확인 부탁드립니다.</p>",
    },
    {
        "title": "[SEED] 사내 통합 SSO 로그인 토큰 5분 주기 만료 반복 현상 점검",
        "category": "account", "priority": "3", "status": "assigned",
        "author": "user1@test.com", "assignee": "officer4@test.com",
        "content": "<p>오전부터 포털 접속 시 5분마다 세션이 만료되어 업무 진행이 불가능합니다. 긴급 조치 요청드립니다.</p>",
    },
    {
        "title": "[SEED] ERP 재무회계 결산 모듈 권한 변경 및 접근 제어 검토",
        "category": "sw", "priority": "2", "status": "assigned",
        "author": "user2@test.com", "assignee": "officer3@test.com",
        "initial_assignee": "officer4@test.com",
        "reassign_reason": "ERP 모듈 접근 제어 검토는 소프트웨어 전담 최소프트 담당자가 맡도록 인계합니다.",
        "content": "<p>분기 결산 보고용 재무회계 전표 조회 권한을 서비스기획팀 공용 계정에 추가 요청합니다.</p>",
    },
    {
        "title": "[SEED] 본사 4층 대회의실 Wi-Fi 무선 AP 간헐적 핑튐 및 패킷 로스 점검",
        "category": "network", "priority": "2", "status": "in_progress",
        "author": "user1@test.com", "assignee": "officer2@test.com",
        "overdue_hours": 6,
        "content": "<p>화상회의 진행 중 4층 회의실 무선 네트워크가 끊깁니다. 패킷 분석 및 AP 점검 바랍니다.</p>",
    },
    {
        "title": "[SEED] 사내 그룹웨어 전자결재 양식 인쇄 시 서식 틀어짐 오류",
        "category": "sw", "priority": "1", "status": "in_progress",
        "author": "user1@test.com", "assignee": "officer3@test.com",
        "pending_reason": "오류가 발생하는 브라우저 버전 및 인쇄 미리보기 화면 스크린샷 회신을 부탁드립니다.",
        "pending_response": "Chrome v128 환경이며, 인쇄 CSS 미디어 쿼리가 적용되지 않는 현상 캡처하여 회신드립니다.",
        "content": "<p>휴가신청서 및 기안서 출력 시 결재선 테이블 라인이 페이지 밖으로 밀려 출력됩니다.</p>",
    },
    {
        "title": "[SEED] 프로덕션 DB 읽기 전용 복제본 긴급 접근 권한 신청 (보안 전담)",
        "category": "account", "priority": "3", "status": "in_progress",
        "author": "user2@test.com", "assignee": "officer4@test.com",
        "content": "<p>장애 로그 분석을 위해 프로덕션 Read-Replica DB에 대한 24시간 임시 계정 발급을 신청합니다.</p>",
    },
    {
        "title": "[SEED] 전사 ERP 월간 결산 보고서 PDF 다운로드 시 폰트 깨짐 현상",
        "category": "sw", "priority": "2", "status": "pending",
        "author": "user1@test.com", "assignee": "officer3@test.com",
        "pending_reason": "결산 서식 번호와 문제가 발생하는 특정 월(Month) 표기 양식을 전달해 주시기 바랍니다.",
        "content": "<p>결산 보고서를 PDF 변환 시 한글 고딕 폰트가 네모 박스(ToFu)로 출력됩니다.</p>",
    },
    {
        "title": "[SEED] 재택근무 사내망 SSL-VPN 연결 타임아웃 및 DNS 조회 실패 조치",
        "category": "network", "priority": "2", "status": "resolved",
        "author": "user1@test.com", "assignee": "officer2@test.com",
        "round1_resolution": "사내 내부 DNS(10.10.1.10) 캐시 플러시 및 게이트웨이 정적 라우팅을 등록했습니다.",
        "restart_inquiry": "DNS 초기화 후에도 사내 사설 Git 저장소 접속 시 809 포트 타임아웃이 재발합니다.",
        "resolution_before_edit": "VPN 게이트웨이 MTU 값을 1450으로 임시 하향 조정하였습니다.",
        "resolution_note": "코어 스위치 점보 프레임 패킷 드롭 원인을 파악하여 MTU 1500 원복 및 LACP 트렁크 링크 재동기화를 완료했습니다.",
        "content": "<p>외부 재택 환경에서 VPN 접속 후 사내 내부망 도메인 접속이 지연됩니다.</p>",
    },
    {
        "title": "[SEED] 사내 공용 복합기 네트워크 스캔 SMBv3 공유 폴더 연결 가이드",
        "category": "hw", "priority": "1", "status": "resolved",
        "author": "user2@test.com", "assignee": "officer@test.com",
        "is_faq": True,
        "resolution_note": "복합기 주소록에서 SMBv3 인증 경로(\\\\10.10.20.5\\scan\\사번)를 등록하고 AD 계정 비밀번호를 연동하여 완료했습니다.",
        "content": "<p>Windows 11 업데이트 후 복합기에서 PC로 스캔 파일 전송 시 네트워크 오류가 뜹니다.</p>",
    },
    {
        "title": "[SEED] 재택근무 사내 보안 VPN 클라이언트 809 포트 접속 불가 해결 공식 FAQ",
        "category": "network", "priority": "2", "status": "closed",
        "author": "user1@test.com", "assignee": "officer2@test.com",
        "is_faq": True,
        "rating": "5",
        "rating_comment": "가이드라인이 상세하여 신규 입사자도 5분 만에 재택 환경을 직접 구성할 수 있었습니다.",
        "resolution_note": "1. VPN 클라이언트 종료\n2. 가상 TAP 어댑터 드라이버 재시작\n3. 사내 포털에서 최신 v2.4 프로파일 인증서 재적용",
        "content": "<p>재택근무 중 VPN 에이전트 연결 시 에러코드 809가 발생하여 긴급 문의합니다.</p>",
    },
    {
        "title": "[SEED] 보조 모니터 연결용 USB-C to DP 케이블 신청 (부서 여분 확인 취소)",
        "category": "etc", "priority": "0", "status": "canceled",
        "author": "user1@test.com", "assignee": None,
        "cancel_reason": "팀 내 비품함에서 여분 정품 케이블을 수령하여 본 신청 건을 취소합니다.",
        "content": "<p>노트북과 4K 모니터 연결을 위한 케이블 지급을 신청합니다. (자체 수령으로 취소 예정)</p>",
    },
]
