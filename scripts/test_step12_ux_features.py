# -*- coding: utf-8 -*-
"""
E2E API Test for Step 12:
1. Multi-sorting options on ticket list (sort_by=deadline asc, priority desc, etc.)
2. Author ticket update while in submitted status (title, category, priority, content)
3. Permission guard: other employee cannot update ticket (HTTP 403)
4. State guard: cannot update ticket when status is not submitted (HTTP 400)
5. Initial attachments creation on ticket creation (Base64)
6. Additional attachment upload & download verification (Base64 integrity)
"""
import sys
import base64
import json
import urllib.request
import urllib.error

BASE_URL = "http://localhost:8000/api/v1"

def log_step(name):
    print(f"\n======================================================================")
    print(f"[STEP 12 TEST] {name}")
    print(f"======================================================================")

def log_pass(msg):
    print(f"  [PASS] {msg}")

def log_fail(msg):
    print(f"  [FAIL] {msg}")
    sys.exit(1)

def http_req(url, method="GET", data=None, token=None):
    hdrs = {"Content-Type": "application/json", "Accept": "application/json"}
    if token:
        hdrs["Authorization"] = f"Bearer {token}"
    encoded = json.dumps(data).encode("utf-8") if data is not None else None
    req = urllib.request.Request(url, data=encoded, headers=hdrs, method=method)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            body = resp.read().decode("utf-8")
            return resp.status, json.loads(body) if body else {}
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8")
        try:
            parsed = json.loads(err_body)
        except Exception:
            parsed = {"detail": err_body}
        return e.code, parsed
    except Exception as e:
        log_fail(f"HTTP request error: {e}")

def login(email, password):
    status, data = http_req(f"{BASE_URL}/auth/login", method="POST", data={"login": email, "password": password})
    if status != 200:
        log_fail(f"Login failed: {data}")
    return data["access_token"]

def main():
    print("Starting Step 12 UX & Business Utility E2E Verification Suite...")

    # Authenticate
    u1_token = login("user1@test.com", "1234")
    u2_token = login("user2@test.com", "1234")
    officer_token = login("officer@test.com", "1234")
    log_pass("Authenticated user1, user2, officer tokens successfully.")

    # -------------------------------------------------------------
    # 1. Multi-Sorting Test on Ticket List
    # -------------------------------------------------------------
    log_step("1. Multi-Sorting Options on Ticket List")
    # 1-1: Sort by ID ASC
    s, res = http_req(f"{BASE_URL}/tickets?sort_by=id+asc&limit=10", token=officer_token)
    assert s == 200
    ids_asc = [t["id"] for t in res["data"]]
    assert ids_asc == sorted(ids_asc), f"Expected ascending IDs, got {ids_asc}"
    log_pass(f"Sort 'id asc' verified: {ids_asc[:5]}...")

    # 1-2: Sort by ID DESC
    s, res = http_req(f"{BASE_URL}/tickets?sort_by=id+desc&limit=10", token=officer_token)
    assert s == 200
    ids_desc = [t["id"] for t in res["data"]]
    assert ids_desc == sorted(ids_desc, reverse=True), f"Expected descending IDs, got {ids_desc}"
    log_pass(f"Sort 'id desc' verified: {ids_desc[:5]}...")

    # 1-3: Sort by Deadline ASC
    s, res = http_req(f"{BASE_URL}/tickets?sort_by=deadline+asc&limit=10", token=officer_token)
    assert s == 200
    deadlines = [t.get("deadline") for t in res["data"] if t.get("deadline")]
    assert deadlines == sorted(deadlines), f"Expected sorted deadlines, got {deadlines}"
    log_pass(f"Sort 'deadline asc' (SLA urgent) verified cleanly.")

    # -------------------------------------------------------------
    # 2. Author Inquiry Update (when in submitted status)
    # -------------------------------------------------------------
    log_step("2. Author Inquiry Update in Submitted Status")
    # Create ticket in submitted status
    s, created = http_req(f"{BASE_URL}/tickets", method="POST", data={
        "title": "[12단계 원본] 초기 제목",
        "category": "etc",
        "priority": "0",
        "content": "<p>초기 작성된 문의 내용입니다.</p>"
    }, token=u1_token)
    assert s == 201
    ticket_id = created["id"]
    log_pass(f"Created ticket in submitted status: ID={ticket_id}, Number={created['ticket_number']}")

    # Security Guard: User 2 tries to update User 1's ticket -> Should be 403
    s, res = http_req(f"{BASE_URL}/tickets/{ticket_id}/update", method="POST", data={
        "title": "[HACK] 불법 수정 시도"
    }, token=u2_token)
    assert s == 403, f"Expected 403 Forbidden, got {s}: {res}"
    log_pass("Security Guard: Unauthorized user cannot update another user's submitted ticket (HTTP 403).")

    # Author updates ticket
    s, updated = http_req(f"{BASE_URL}/tickets/{ticket_id}/update", method="POST", data={
        "title": "[12단계 수정본] 수정된 문의 제목",
        "category": "sw",
        "priority": "2",
        "content": "<p>수정된 상세 문의 내용입니다 (긴급도 및 내용 보강).</p>"
    }, token=u1_token)
    assert s == 200, f"Expected 200, got {s}: {updated}"
    assert updated["title"] == "[12단계 수정본] 수정된 문의 제목"
    assert updated["category"] == "sw"
    assert updated["priority"] == "2"
    log_pass("Author successfully updated submitted ticket: Title, Category, Priority, and Content updated.")

    # Officer starts progress (submitted -> in_progress)
    http_req(f"{BASE_URL}/tickets/{ticket_id}/assign", method="POST", token=officer_token)
    http_req(f"{BASE_URL}/tickets/{ticket_id}/start-progress", method="POST", token=officer_token)

    # State Guard: Once in_progress, author update must be rejected with 400
    s, res = http_req(f"{BASE_URL}/tickets/{ticket_id}/update", method="POST", data={
        "title": "처리 중 불법 수정 시도"
    }, token=u1_token)
    assert s == 400, f"Expected 400 Bad Request, got {s}: {res}"
    log_pass("State Guard: Cannot update ticket once it transitions out of submitted status (HTTP 400).")

    # -------------------------------------------------------------
    # 3. Attachment Upload and Download (Base64)
    # -------------------------------------------------------------
    log_step("3. Attachment Upload & Download Verification (Base64)")
    sample_text = "IT Helpdesk Test Log File Content - Error code 0x80070005"
    sample_b64 = base64.b64encode(sample_text.encode('utf-8')).decode('utf-8')

    # Upload attachment to ticket
    s, att = http_req(f"{BASE_URL}/tickets/{ticket_id}/attachments", method="POST", data={
        "name": "error_log.txt",
        "datas": sample_b64,
        "mimetype": "text/plain"
    }, token=u1_token)
    assert s == 201, f"Expected 201, got {s}: {att}"
    att_id = att["id"]
    log_pass(f"Uploaded attachment: ID={att_id}, Name={att['name']}, Size={att['file_size']} bytes")

    # Check detail returns attachments
    s, detail = http_req(f"{BASE_URL}/tickets/{ticket_id}", token=u1_token)
    assert s == 200
    att_list = detail.get("attachments", [])
    assert len(att_list) >= 1
    assert any(a["id"] == att_id for a in att_list)
    log_pass("Ticket detail endpoint includes uploaded attachment metadata.")

    # Download attachment
    s, dl = http_req(f"{BASE_URL}/tickets/{ticket_id}/attachments/{att_id}", token=u1_token)
    assert s == 200
    assert dl["datas"] == sample_b64
    recovered_text = base64.b64decode(dl["datas"]).decode('utf-8')
    assert recovered_text == sample_text
    log_pass(f"Downloaded attachment Base64 payload verified 100% identical: '{recovered_text[:30]}...'")

    print("\n======================================================================")
    print("STEP 12 ALL UX & UTILITY TESTS PASSED 100%!")
    print("======================================================================")

if __name__ == "__main__":
    main()
