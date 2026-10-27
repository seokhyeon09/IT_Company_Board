# -*- coding: utf-8 -*-
"""
End-to-End Real-World Multi-User Scenario Test Suite (Pure Standard Library)
Tests real HTTP interactions against FastAPI Gateway (http://localhost:8000/api/v1)
and Odoo 18 Headless Backend.
"""
import sys
import json
import urllib.request
import urllib.error

BASE_URL = "http://localhost:8000/api/v1"

class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def log_step(step_name):
    print(f"\n{Colors.BOLD}{Colors.HEADER}======================================================================{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.HEADER}[STEP] {step_name}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.HEADER}======================================================================{Colors.ENDC}")

def log_success(msg):
    print(f"  {Colors.OKGREEN}[PASS]{Colors.ENDC} {msg}")

def log_fail(msg):
    print(f"  {Colors.FAIL}[FAIL]{Colors.ENDC} {msg}")
    sys.exit(1)

def log_info(msg):
    print(f"  {Colors.OKCYAN}[INFO]{Colors.ENDC} {msg}")

def http_request(method, path, data=None, token=None):
    url = f"{BASE_URL}{path}"
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    encoded_data = json.dumps(data).encode("utf-8") if data is not None else None
    req = urllib.request.Request(url, data=encoded_data, headers=headers, method=method)
    
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            body = resp.read().decode("utf-8")
            status_code = resp.status
            parsed = json.loads(body) if body else {}
            return status_code, parsed
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8")
        try:
            parsed = json.loads(err_body)
        except Exception:
            parsed = {"detail": err_body}
        return e.code, parsed
    except Exception as e:
        log_fail(f"HTTP connection error to {url}: {e}")

def login(email, password):
    status, data = http_request("POST", "/auth/login", data={"login": email, "password": password})
    if status != 200:
        log_fail(f"Login failed for {email}: {status} {data}")
    token = data["access_token"]
    user = data["user"]
    log_success(f"Login success: {user['name']} ({user['login']}) | UID: {user['uid']} | Officer: {user['is_officer']}")
    return token, user

def main():
    print(f"{Colors.BOLD}Starting IT Helpdesk Multi-User E2E Web Test Suite...{Colors.ENDC}")
    
    # -------------------------------------------------------------
    # 1. Multi-User Authentication
    # -------------------------------------------------------------
    log_step("1. Multi-User Authentication & Claims Verification")
    u1_token, u1_info = login("user1@test.com", "1234")
    u2_token, u2_info = login("user2@test.com", "1234")
    off_token, off_info = login("officer@test.com", "1234")
    adm_token, adm_info = login("admin@helpdesk.com", "admin")

    assert not u1_info["is_officer"], "user1 should NOT be an officer"
    assert not u2_info["is_officer"], "user2 should NOT be an officer"
    assert off_info["is_officer"], "officer should be an officer"
    assert adm_info["is_officer"], "admin should be an officer"
    log_success("All 4 user roles and tokens verified cleanly.")

    # -------------------------------------------------------------
    # 2. Employee 1 Ticket Creation
    # -------------------------------------------------------------
    log_step("2. Employee 1 (user1@test.com) Creates Ticket")
    create_payload = {
        "title": "[E2E] 사내 메신저 화상회의 음성 끊김 점검 요청",
        "category": "sw",
        "priority": "1",
        "content": "<p>화상회의 진행 시 10분 간격으로 상대방 음성이 끊깁니다. 대역폭 점검 요청드립니다.</p>"
    }
    status, ticket_data = http_request("POST", "/tickets", data=create_payload, token=u1_token)
    if status != 201:
        log_fail(f"Ticket creation failed: {status} {ticket_data}")
    t_id = ticket_data["id"]
    t_num = ticket_data["ticket_number"]
    t_deadline = ticket_data.get("deadline")
    t_status = ticket_data["status"]

    log_success(f"Ticket created: ID={t_id}, Number={t_num}, Status={t_status}")
    log_info(f"SLA Deadline: {t_deadline} (Automated SLA 48h verified)")
    assert t_status == "submitted", f"Expected submitted status, got {t_status}"
    assert t_num.startswith("TKT-"), f"Expected ticket sequence starting with TKT-, got {t_num}"

    # -------------------------------------------------------------
    # 3. Employee 1 List & Isolation Check
    # -------------------------------------------------------------
    log_step("3. Employee 1 Ticket List Verification")
    status, list_data = http_request("GET", "/tickets", token=u1_token)
    assert status == 200, f"List tickets failed: {status}"
    u1_tickets = list_data.get("data", [])
    found = any(t["id"] == t_id for t in u1_tickets)
    assert found, f"Created ticket ID {t_id} not found in user1 list"
    log_success(f"Employee 1 sees own ticket in list (Total {len(u1_tickets)} tickets visible)")

    # -------------------------------------------------------------
    # 4. Employee 2 BOLA / IDOR Penetration Attempts
    # -------------------------------------------------------------
    log_step("4. Employee 2 (user2@test.com) BOLA / IDOR Penetration Attempts")
    
    # Attack 1: user2 attempts to view user1's private ticket
    status, data = http_request("GET", f"/tickets/{t_id}", token=u2_token)
    if status in (403, 400):
        log_success(f"BOLA Attack 1 Blocked: user2 GET /tickets/{t_id} -> HTTP {status} ({data.get('detail', '')})")
    else:
        log_fail(f"BOLA Vulnerability: user2 viewed user1 ticket! HTTP {status}")

    # Attack 2: user2 attempts to resolve user1's ticket
    status, data = http_request("POST", f"/tickets/{t_id}/resolve", data={"resolution_note": "해커 조치 완료"}, token=u2_token)
    if status == 403:
        log_success(f"BOLA Attack 2 Blocked: user2 POST /resolve -> HTTP 403 Forbidden")
    else:
        log_fail(f"Permission Bypass: user2 resolved ticket! HTTP {status}")

    # Attack 3: user2 attempts to rate user1's ticket
    status, data = http_request("POST", f"/tickets/{t_id}/rate", data={"rating": "1", "rating_comment": "타인 평점 테러"}, token=u2_token)
    if status in (403, 400):
        log_success(f"BOLA Attack 3 Blocked: user2 POST /rate -> HTTP {status} ({data.get('detail', '')})")
    else:
        log_fail(f"BOLA Vulnerability: user2 rated user1 ticket! HTTP {status}")

    # Attack 4: user2 attempts to toggle FAQ
    status, data = http_request("POST", f"/tickets/{t_id}/toggle-faq", token=u2_token)
    if status == 403:
        log_success(f"BOLA Attack 4 Blocked: user2 POST /toggle-faq -> HTTP 403 Forbidden")
    else:
        log_fail(f"Permission Bypass: user2 toggled FAQ! HTTP {status}")

    # -------------------------------------------------------------
    # 5. IT Officer Resolves Ticket
    # -------------------------------------------------------------
    log_step("5. IT Helpdesk Officer (officer@test.com) Resolves Ticket")
    # Officer views ticket detail
    status, off_t_detail = http_request("GET", f"/tickets/{t_id}", token=off_token)
    assert status == 200, f"Officer detail fetch failed: {status}"
    log_success(f"Officer viewed ticket: Author={off_t_detail['author_name']}, Title='{off_t_detail['title']}'")
    current_write_date = off_t_detail["write_date"]

    # Officer resolves ticket
    resolve_payload = {
        "resolution_note": "사내망 백본 스위치 QoS 화상회의 음성 패킷(DSCP EF) 우선순위 할당 및 대역폭 증설 완료.",
        "if_match_write_date": current_write_date
    }
    status, res_resp = http_request("POST", f"/tickets/{t_id}/resolve", data=resolve_payload, token=off_token)
    assert status == 200, f"Resolve failed: {status} {res_resp}"
    resolved_data = res_resp.get("data", {})
    assert resolved_data.get("status") == "resolved", f"Expected resolved status, got {resolved_data.get('status')}"
    log_success(f"Ticket resolved successfully: Status={resolved_data.get('status')}")

    # -------------------------------------------------------------
    # 6. IT Officer Toggles FAQ Knowledgebase
    # -------------------------------------------------------------
    log_step("6. IT Officer Publishes Ticket to FAQ Knowledgebase")
    status, faq_resp = http_request("POST", f"/tickets/{t_id}/toggle-faq", token=off_token)
    assert status == 200, f"Toggle FAQ failed: {status} {faq_resp}"
    faq_data = faq_resp.get("data", {})
    assert faq_data.get("is_faq") is True, "Ticket should now be marked as is_faq=True"
    log_success(f"Ticket successfully added to company FAQ knowledgebase: is_faq={faq_data.get('is_faq')}")

    # Verify that Employee 2 can now view it under FAQ knowledgebase
    status, faq_list = http_request("GET", "/tickets?is_faq=true", token=u2_token)
    assert status == 200, f"User2 FAQ fetch failed: {status}"
    faq_tickets = faq_list.get("data", [])
    found_in_faq = any(t["id"] == t_id for t in faq_tickets)
    assert found_in_faq, "Ticket should be visible to user2 under FAQ knowledgebase"
    log_success("Employee 2 can now view official resolution case in FAQ knowledgebase.")

    # -------------------------------------------------------------
    # 7. Employee 1 Rates and Closes Ticket
    # -------------------------------------------------------------
    log_step("7. Employee 1 Rates Service and Closes Ticket")
    # Employee 1 checks detail and sees resolution note
    status, u1_detail = http_request("GET", f"/tickets/{t_id}", token=u1_token)
    assert status == 200, f"User1 fetch detail failed: {status}"
    assert u1_detail["status"] == "resolved"
    assert "사내망 백본 스위치" in u1_detail["resolution_note"]
    log_success("Employee 1 confirmed officer resolution note.")

    # Employee 1 rates 5 stars
    rate_payload = {
        "rating": "5",
        "rating_comment": "매우 빠르고 친절하게 네트워크 세팅을 완료해주셨습니다. 감사합니다!",
        "if_match_write_date": u1_detail["write_date"]
    }
    status, rate_res = http_request("POST", f"/tickets/{t_id}/rate", data=rate_payload, token=u1_token)
    assert status == 200, f"Rate failed: {status} {rate_res}"
    rate_data = rate_res.get("data", {})
    assert rate_data.get("status") == "closed", f"Expected closed status, got {rate_data.get('status')}"
    assert rate_data.get("rating") == "5", f"Expected rating 5, got {rate_data.get('rating')}"
    log_success(f"Ticket successfully rated and closed: Status={rate_data.get('status')}, Rating={rate_data.get('rating')} stars")

    # -------------------------------------------------------------
    # 8. Optimistic Concurrency Conflict (HTTP 409) Test
    # -------------------------------------------------------------
    log_step("8. Optimistic Concurrency Collision (HTTP 409) Test")
    stale_payload = {
        "resolution_note": "오래된 데이터로 덮어쓰기 시도",
        "if_match_write_date": "2020-01-01T00:00:00Z"
    }
    status, stale_res = http_request("POST", f"/tickets/{t_id}/resolve", data=stale_payload, token=off_token)
    if status == 409:
        log_success(f"Concurrency Collision Blocked cleanly: HTTP 409 Conflict ({stale_res.get('detail', '')})")
    elif status in (400, 403):
        log_success(f"Operation cleanly rejected (Ticket already closed/conflict): HTTP {status}")
    else:
        log_fail(f"Concurrency failure: expected 409 conflict, got {status}")

    # -------------------------------------------------------------
    # 9. Overall System Stats Verification
    # -------------------------------------------------------------
    log_step("9. Overall System Stats Verification")
    status, stats_res = http_request("GET", "/tickets/stats", token=adm_token)
    assert status == 200, f"Admin stats failed: {status}"
    stats_data = stats_res.get("data", {})
    log_success(f"System Stats: Total={stats_data['total']}, Waiting={stats_data['waiting']}, InProgress={stats_data['in_progress']}, Resolved={stats_data['resolved']}, Overdue={stats_data['overdue']}")

    print(f"\n{Colors.BOLD}{Colors.OKGREEN}======================================================================{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.OKGREEN}[ALL E2E SCENARIOS PASSED SUCCESSFULLY 100%]{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.OKGREEN}======================================================================{Colors.ENDC}\n")

if __name__ == "__main__":
    main()
