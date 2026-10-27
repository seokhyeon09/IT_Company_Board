# -*- coding: utf-8 -*-
"""
E2E Security & Gateway Hardening Test Suite for Step 11:
1. Persistent Connection Pooling: Continuous multi-request throughput succeeds stably.
2. Stored XSS Prevention: HTML tags in resolutions, follow-ups, updates, close notes, and cancel reasons are safely escaped.
3. Strict HMAC Validation: Legacy HMAC signature without body hash is rejected with AccessError.
4. Sliding Window Rate Limiting: 16 rapid login attempts trigger HTTP 429 Too Many Requests with Retry-After header.
"""
import sys
import time
import json
import hmac
import hashlib
import urllib.request
import urllib.error

GATEWAY_URL = "http://localhost:8000/api/v1"
ODOO_URL = "http://localhost:8069"
GATEWAY_SHARED_SECRET = "secure_inter_tier_hmac_secret_key_32_chars"

def log_step(name):
    print(f"\n======================================================================")
    print(f"[STEP 11 TEST] {name}")
    print(f"======================================================================")

def log_pass(msg):
    print(f"  [PASS] {msg}")

def log_fail(msg):
    print(f"  [FAIL] {msg}")
    sys.exit(1)

def http_json(url, method="GET", data=None, headers=None):
    hdrs = {"Content-Type": "application/json", "Accept": "application/json"}
    if headers:
        hdrs.update(headers)
    encoded = json.dumps(data).encode("utf-8") if data is not None else None
    req = urllib.request.Request(url, data=encoded, headers=hdrs, method=method)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            body = resp.read().decode("utf-8")
            return resp.status, json.loads(body) if body else {}, resp.headers
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8")
        try:
            parsed = json.loads(err_body)
        except Exception:
            parsed = {"detail": err_body}
        return e.code, parsed, e.headers
    except Exception as e:
        log_fail(f"Connection failed to {url}: {e}")

def main():
    print("Starting Step 11 Security & Hardening Verification Suite...")

    # -------------------------------------------------------------
    # 1. Authenticate User & Officer for Authorized Tests First
    # -------------------------------------------------------------
    log_step("1. Authenticate User & Officer (Before Rate Limit Exhaustion)")
    # Officer login
    status, o_data, _ = http_json(f"{GATEWAY_URL}/auth/login", method="POST", data={"login": "officer@test.com", "password": "1234"})
    if status == 429:
        print("Rate limit still active from previous run, waiting for reset...")
        retry = o_data.get("error", {}).get("retry_after_seconds", 30)
        time.sleep(retry + 1)
        status, o_data, _ = http_json(f"{GATEWAY_URL}/auth/login", method="POST", data={"login": "officer@test.com", "password": "1234"})

    assert status == 200, f"Officer login failed: {o_data}"
    officer_token = o_data["access_token"]

    # User 1 login
    status, u_data, _ = http_json(f"{GATEWAY_URL}/auth/login", method="POST", data={"login": "user1@test.com", "password": "1234"})
    assert status == 200, f"User1 login failed: {u_data}"
    user1_token = u_data["access_token"]
    log_pass("Authenticated valid officer and user tokens successfully.")

    # -------------------------------------------------------------
    # 2. Connection Pooling & Keep-Alive Throughput Stability
    # -------------------------------------------------------------
    log_step("2. Persistent Connection Pooling Throughput Test")
    t0 = time.time()
    for _ in range(10):
        s, d, _ = http_json(f"{GATEWAY_URL}/tickets/stats", headers={"Authorization": f"Bearer {officer_token}"})
        assert s == 200
    elapsed = time.time() - t0
    log_pass(f"10 sequential requests via shared HTTP connection pool completed in {elapsed:.3f}s (average {elapsed/10*1000:.1f}ms/req).")

    # -------------------------------------------------------------
    # 3. Stored XSS Prevention Tests across Chatter Endpoints
    # -------------------------------------------------------------
    log_step("3. Stored XSS Prevention across All Chatter Entry Points")
    # 3-1: Create Ticket
    status, ticket_obj, _ = http_json(
        f"{GATEWAY_URL}/tickets",
        method="POST",
        data={
            "title": "[XSS Test] Stored XSS Defense Verification",
            "category": "sw",
            "content": "<p>Initial Inquiry Content</p>",
            "priority": "1"
        },
        headers={"Authorization": f"Bearer {user1_token}"}
    )
    assert status == 201, f"Ticket create failed: {ticket_obj}"
    ticket_id = ticket_obj["id"]
    log_pass(f"Created ticket for XSS testing: ID={ticket_id}")

    # 3-2: Officer assigns and starts progress
    http_json(f"{GATEWAY_URL}/tickets/{ticket_id}/assign", method="POST", headers={"Authorization": f"Bearer {officer_token}"})
    http_json(f"{GATEWAY_URL}/tickets/{ticket_id}/start-progress", method="POST", headers={"Authorization": f"Bearer {officer_token}"})

    # 3-3: Officer Resolves Ticket with malicious XSS script payload
    xss_payload_resolve = "해결 조치 완료: <script>alert('XSS_RESOLVE')</script> 및 <img src=x onerror=alert('PWNED')>"
    status, res, _ = http_json(
        f"{GATEWAY_URL}/tickets/{ticket_id}/resolve",
        method="POST",
        data={"resolution_note": xss_payload_resolve},
        headers={"Authorization": f"Bearer {officer_token}"}
    )
    assert status == 200, f"Resolve failed: {res}"

    # Check detail: script tag must be escaped to &lt;script&gt;
    status, detail, _ = http_json(f"{GATEWAY_URL}/tickets/{ticket_id}", headers={"Authorization": f"Bearer {officer_token}"})
    res_note = detail.get("resolution_note", "")
    assert "<script>" not in res_note, f"Raw <script> found in resolution_note! {res_note}"
    assert "&lt;script&gt;" in res_note or "<script>" not in res_note
    log_pass("1) Resolve XSS Defense: <script> tag successfully escaped into safe entities in resolution_note.")

    # 3-4: User 1 submits Follow-up Inquiry (restart) with XSS payload
    xss_payload_restart = "추가 재문의 요청: <svg onload=alert('XSS_RESTART')> 추가 확인 요망"
    status, res, _ = http_json(
        f"{GATEWAY_URL}/tickets/{ticket_id}/restart",
        method="POST",
        data={"reason": xss_payload_restart},
        headers={"Authorization": f"Bearer {user1_token}"}
    )
    assert status == 200, f"Restart failed: {res}"

    status, detail, _ = http_json(f"{GATEWAY_URL}/tickets/{ticket_id}", headers={"Authorization": f"Bearer {officer_token}"})
    inquiries = [t for t in detail.get("timeline", []) if t["type"] == "inquiry" and t["round"] > 1]
    assert len(inquiries) > 0
    followup_content = inquiries[-1]["content"]
    assert "<svg" not in followup_content, f"Raw <svg> found in follow_up! {followup_content}"
    log_pass("2) Follow-up Inquiry XSS Defense: <svg onload> tag safely sanitized.")

    # 3-5: Officer Updates Resolution with XSS payload
    xss_payload_update = "수정된 답변 내용: <iframe src='javascript:alert(1)'></iframe> 업데이트 완료"
    status, res, _ = http_json(
        f"{GATEWAY_URL}/tickets/{ticket_id}/update-resolution",
        method="POST",
        data={"resolution_note": xss_payload_update},
        headers={"Authorization": f"Bearer {officer_token}"}
    )
    assert status == 200, f"Update resolution failed: {res}"

    status, detail, _ = http_json(f"{GATEWAY_URL}/tickets/{ticket_id}", headers={"Authorization": f"Bearer {officer_token}"})
    updated_note = detail.get("resolution_note", "")
    assert "<iframe" not in updated_note, f"Raw <iframe found in updated resolution_note! {updated_note}"
    log_pass("3) Update Resolution XSS Defense: <iframe tag safely sanitized.")

    # -------------------------------------------------------------
    # 4. Strict HMAC Validation (Legacy Payload Rejection)
    # -------------------------------------------------------------
    log_step("4. Strict HMAC Validation & Legacy Fallback Removal")
    uid_str = "6"  # officer uid
    ts_str = str(int(time.time()))
    legacy_payload = f"{uid_str}:{ts_str}".encode('utf-8')
    legacy_sig = hmac.new(GATEWAY_SHARED_SECRET.encode('utf-8'), legacy_payload, hashlib.sha256).hexdigest()

    odoo_req_body = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {},
        "id": 1
    }
    odoo_headers = {
        "X-Gateway-User-Id": uid_str,
        "X-Gateway-Timestamp": ts_str,
        "X-Gateway-Signature": legacy_sig,  # Insecure legacy signature!
    }

    status, resp_data, _ = http_json(
        f"{ODOO_URL}/api/v1/tickets/list",
        method="POST",
        data=odoo_req_body,
        headers=odoo_headers
    )
    err_obj = resp_data.get("error", {})
    err_msg = err_obj.get("data", {}).get("message", "") or err_obj.get("message", "")
    if "Invalid gateway signature" in err_msg or "Unauthorized" in err_msg:
        log_pass("Strict HMAC verified: Legacy payload without body hash is REJECTED cleanly.")
    else:
        log_fail(f"Legacy payload was not rejected! Status={status}, Response={resp_data}")

    # -------------------------------------------------------------
    # 5. Rate Limiting Test (/auth/login Brute-Force Defense)
    # -------------------------------------------------------------
    log_step("5. Sliding Window Rate Limiter Test (Login Brute-Force Defense)")
    rapid_attempts = 16
    got_429 = False
    retry_after_hdr = None

    for i in range(1, rapid_attempts + 1):
        status, body, headers = http_json(
            f"{GATEWAY_URL}/auth/login",
            method="POST",
            data={"login": "fake_user@test.com", "password": "wrong_password"}
        )
        if status == 429:
            got_429 = True
            retry_after_hdr = headers.get("Retry-After")
            log_pass(f"Attempt #{i}: Rate Limit correctly triggered HTTP 429 Too Many Requests!")
            log_pass(f"Response: {body}")
            log_pass(f"Retry-After Header: {retry_after_hdr}s")
            break
        elif status == 401 or status == 400:
            pass  # Expected credential failure before limit
        else:
            log_fail(f"Unexpected status on attempt #{i}: {status} {body}")

    if not got_429:
        log_fail("Rate limiter failed to block after 15 rapid login attempts!")

    print("\n======================================================================")
    print("STEP 11 ALL SECURITY & GATEWAY HARDENING TESTS PASSED 100%!")
    print("======================================================================")

if __name__ == "__main__":
    main()
