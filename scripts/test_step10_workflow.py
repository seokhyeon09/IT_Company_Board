# -*- coding: utf-8 -*-
"""
E2E Scenario Test for Step 10:
- IT Helpdesk Officer Step-by-Step Workflow Transitions:
  submitted -> assign -> assigned -> start-progress -> in_progress -> pending -> pending -> start-progress -> in_progress -> close -> closed
- Access Control: Regular user cannot trigger officer workflow actions (HTTP 403)
- Employee / Officer Ticket Cancellation:
  author cancels own ticket -> status=canceled, message_post recorded
  other employee cannot cancel (HTTP 403)
- Status filter: 'canceled' status filter works properly
"""
import sys
import json
import urllib.request
import urllib.error

BASE_URL = "http://localhost:8000/api/v1"

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
        print(f"[FAIL] HTTP error to {url}: {e}")
        sys.exit(1)

def login(email, password):
    status, data = http_request("POST", "/auth/login", data={"login": email, "password": password})
    if status != 200:
        print(f"[FAIL] Login failed for {email}: {status} {data}")
        sys.exit(1)
    return data["access_token"], data["user"]

def main():
    print("======================================================================")
    print("STEP 10 E2E Verification: Workflow Actions & Ticket Cancellation")
    print("======================================================================")

    # 1. Login
    u1_token, u1_info = login("user1@test.com", "1234")
    u2_token, u2_info = login("user2@test.com", "1234")
    officer_token, officer_info = login("officer@test.com", "1234")
    print(f"  [PASS] Logged in: u1={u1_info['name']}, u2={u2_info['name']}, officer={officer_info['name']}")

    # 2. User 1 creates Ticket A
    status, ticket_a = http_request("POST", "/tickets", data={
        "title": "[10단계] 상태 전이 워크플로우 테스트 티켓",
        "category": "sw",
        "content": "<p>담당자 배정 및 처리시작, 답변대기, 직권종결 테스트를 진행합니다.</p>",
        "priority": "2"
    }, token=u1_token)
    assert status == 201, f"Expected 201, got {status}: {ticket_a}"
    ticket_id = ticket_a["id"]
    print(f"  [PASS] Created Ticket A: ID={ticket_id}, Number={ticket_a['ticket_number']}, Status={ticket_a['status']}")

    # 3. Security: User 2 tries officer actions on Ticket A -> Should be 403
    status, res = http_request("POST", f"/tickets/{ticket_id}/assign", token=u2_token)
    assert status == 403, f"Expected 403, got {status}: {res}"
    print(f"  [PASS] Security Guard: Regular user cannot assign ticket (HTTP 403)")

    status, res = http_request("POST", f"/tickets/{ticket_id}/start-progress", token=u2_token)
    assert status == 403, f"Expected 403, got {status}: {res}"
    print(f"  [PASS] Security Guard: Regular user cannot start progress (HTTP 403)")

    status, res = http_request("POST", f"/tickets/{ticket_id}/pending", token=u2_token)
    assert status == 403, f"Expected 403, got {status}: {res}"
    print(f"  [PASS] Security Guard: Regular user cannot set pending (HTTP 403)")

    status, res = http_request("POST", f"/tickets/{ticket_id}/close", data={"note": "hack"}, token=u2_token)
    assert status == 403, f"Expected 403, got {status}: {res}"
    print(f"  [PASS] Security Guard: Regular user cannot close ticket (HTTP 403)")

    # 4. Officer assigns ticket to me
    status, res = http_request("POST", f"/tickets/{ticket_id}/assign", token=officer_token)
    assert status == 200, f"Expected 200, got {status}: {res}"
    assert res["data"]["status"] == "assigned"
    print(f"  [PASS] Officer assigned ticket: Status={res['data']['status']}, Assignee={res['data']['assignee_name']}")

    # 5. Officer starts progress (assigned -> in_progress)
    status, res = http_request("POST", f"/tickets/{ticket_id}/start-progress", token=officer_token)
    assert status == 200, f"Expected 200, got {status}: {res}"
    assert res["data"]["status"] == "in_progress"
    print(f"  [PASS] Officer started progress: Status={res['data']['status']}")

    # 6. Officer requests user response (in_progress -> pending)
    status, res = http_request("POST", f"/tickets/{ticket_id}/pending", token=officer_token)
    assert status == 200, f"Expected 200, got {status}: {res}"
    assert res["data"]["status"] == "pending"
    print(f"  [PASS] Officer requested user pending response: Status={res['data']['status']}")

    # 7. Officer resumes work (pending -> in_progress)
    status, res = http_request("POST", f"/tickets/{ticket_id}/start-progress", token=officer_token)
    assert status == 200, f"Expected 200, got {status}: {res}"
    assert res["data"]["status"] == "in_progress"
    print(f"  [PASS] Officer resumed work: Status={res['data']['status']}")

    # 8. Officer closes ticket authoritatively (in_progress -> closed)
    status, res = http_request("POST", f"/tickets/{ticket_id}/close", data={
        "note": "장비 펌웨어 업데이트 및 정상 동작 확인 완료되어 직권 종결 처리합니다."
    }, token=officer_token)
    assert status == 200, f"Expected 200, got {status}: {res}"
    assert res["data"]["status"] == "closed"
    print(f"  [PASS] Officer authoritatively closed ticket: Status={res['data']['status']}")

    # Verify detail
    status, detail = http_request("GET", f"/tickets/{ticket_id}", token=officer_token)
    assert status == 200
    assert detail["status"] == "closed"
    assert "장비 펌웨어 업데이트" in detail["resolution_note"]
    print(f"  [PASS] Verified ticket detail after close: Note confirmed in ticket detail")

    # 9. User 1 creates Ticket B to test cancellation
    status, ticket_b = http_request("POST", "/tickets", data={
        "title": "[10단계] 문의 취소 기능 검증용 티켓",
        "category": "hw",
        "content": "<p>단순 변심 또는 자가 해결로 인해 취소할 문의입니다.</p>",
        "priority": "0"
    }, token=u1_token)
    assert status == 201
    ticket_b_id = ticket_b["id"]
    print(f"  [PASS] Created Ticket B: ID={ticket_b_id}, Status={ticket_b['status']}")

    # 10. Security: User 2 tries to cancel User 1's ticket -> Should be 403
    status, res = http_request("POST", f"/tickets/{ticket_b_id}/cancel", data={"reason": "malicious cancel"}, token=u2_token)
    assert status == 403, f"Expected 403, got {status}: {res}"
    print(f"  [PASS] Security Guard: Unauthorized employee cannot cancel another user's ticket (HTTP 403)")

    # 11. User 1 cancels own ticket
    status, res = http_request("POST", f"/tickets/{ticket_b_id}/cancel", data={
        "reason": "사내 매뉴얼 확인 후 자가 조치 완료하여 문의 취소합니다."
    }, token=u1_token)
    assert status == 200, f"Expected 200, got {status}: {res}"
    assert res["data"]["status"] == "canceled"
    print(f"  [PASS] Author successfully canceled own ticket: Status={res['data']['status']}")

    # 12. List tickets with status=canceled filter
    status, list_res = http_request("GET", "/tickets?status=canceled", token=u1_token)
    assert status == 200
    canceled_ids = [t["id"] for t in list_res["data"]]
    assert ticket_b_id in canceled_ids
    print(f"  [PASS] Canceled filter verified: Ticket B ({ticket_b_id}) visible in status=canceled list")

    print("\n======================================================================")
    print("STEP 10 ALL WORKFLOW & CANCELLATION TESTS PASSED 100%!")
    print("======================================================================")

if __name__ == "__main__":
    main()
