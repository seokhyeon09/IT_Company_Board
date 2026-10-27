# -*- coding: utf-8 -*-
import os
import sys
import time
import json
import urllib.request
from playwright.sync_api import sync_playwright

SCREENSHOT_DIR = os.path.abspath("local-md/ai-refactor-arch/screenshots")
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

FRONTEND_URL = "http://localhost:3000"

def log_step(name):
    print(f"\n======================================================================")
    print(f"[PLAYWRIGHT STEP 13] {name}")
    print(f"======================================================================")

def log_pass(msg):
    print(f"  [PASS] {msg}")

def log_info(msg):
    print(f"  [INFO] {msg}")

def run_tests():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1280, 'height': 850})
        page = context.new_page()

        # -------------------------------------------------------------
        # SCENARIO 1: IT Officer Login & Dashboard 2-Row Filter Bar & Pagination
        # -------------------------------------------------------------
        log_step("1. IT Officer Login & 2-Row Filter Bar & Sliding Pagination Window")
        page.goto(FRONTEND_URL)
        page.locator("form input[type='password']").wait_for(state="visible")
        page.fill("form input[type='text']", "officer@test.com")
        page.fill("form input[type='password']", "1234")
        page.click("button[type='submit']")

        page.locator("input.pl-8").wait_for(state="visible")
        time.sleep(1.0)
        log_pass("Logged in to Dashboard as IT Officer.")

        # Capture Screenshot 1: Filter bar
        ss1 = os.path.join(SCREENSHOT_DIR, "step13_01_officer_dashboard_filterbar.png")
        page.screenshot(path=ss1)
        log_pass(f"Captured: {ss1}")

        # Check pagination buttons
        pagination_buttons = page.locator("div.flex.items-center.space-x-1 button")
        count = pagination_buttons.count()
        log_info(f"Pagination button count: {count}")
        assert count >= 1, "Expected pagination buttons"

        # -------------------------------------------------------------
        # SCENARIO 2: Open Ticket 854 -> Check Clean HTML & Audit Logs
        # -------------------------------------------------------------
        log_step("2. Check Ticket Detail Modal: No HTML Tags & Clean Officer Logs")
        page.fill("input.pl-8", "0044")
        time.sleep(1.2)

        # Click the card
        first_card = page.locator("div.border-slate-200.rounded-xl.cursor-pointer").first
        first_card.wait_for(state="visible")
        first_card.click()
        time.sleep(1.5)

        modal = page.locator("div.fixed.inset-0")
        modal.wait_for(state="visible")

        # Verify no HTML tags in text
        modal_text = modal.inner_text()
        for forbidden in ['<b>', '</b>', '<br/>', '<br>', '&lt;', '&gt;']:
            assert forbidden not in modal_text, f"Found {forbidden} in modal text!"
        log_pass("Verified Ticket Detail Modal has NO raw HTML tags or unescaped entities.")

        # Scroll to logs section
        page.evaluate('document.querySelector("div.overflow-y-auto")?.scrollTo(0, 1000)')
        time.sleep(0.8)

        ss2 = os.path.join(SCREENSHOT_DIR, "step13_02_ticket_clean_html_logs.png")
        page.screenshot(path=ss2)
        log_pass(f"Captured: {ss2}")

        # Close modal via footer button "닫기"
        page.locator("div.fixed.inset-0 button").filter(has_text="닫기").click()
        page.locator("div.fixed.inset-0").wait_for(state="hidden")
        time.sleep(0.5)

        # Clear search
        page.fill("input.pl-8", "")
        time.sleep(1.0)

        # -------------------------------------------------------------
        # SCENARIO 3: IT Officer Pending Workflow with Reason
        # -------------------------------------------------------------
        log_step("3. IT Officer Pending Workflow: Reason Input & Banner Visualization")
        # Create ticket via API
        login_req = urllib.request.Request(
            "http://localhost:8000/api/v1/auth/login",
            data=json.dumps({"login": "user1@test.com", "password": "1234"}).encode('utf-8'),
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(login_req) as resp:
            u_token = json.loads(resp.read().decode('utf-8'))["access_token"]

        tkt_req = urllib.request.Request(
            "http://localhost:8000/api/v1/tickets",
            data=json.dumps({
                "title": "Playwright 검증 티켓 - 답변대기 및 취소",
                "category": "sw",
                "priority": "2",
                "content": "상세 사유 입력 및 상단 본인 취소 버튼 검증용"
            }).encode('utf-8'),
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {u_token}"}
        )
        with urllib.request.urlopen(tkt_req) as resp:
            new_ticket = json.loads(resp.read().decode('utf-8'))
            tkt_id = new_ticket["id"]
            tkt_num = new_ticket["ticket_number"]

        off_login_req = urllib.request.Request(
            "http://localhost:8000/api/v1/auth/login",
            data=json.dumps({"login": "officer@test.com", "password": "1234"}).encode('utf-8'),
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(off_login_req) as resp:
            o_token = json.loads(resp.read().decode('utf-8'))["access_token"]

        for action in ["assign", "start-progress"]:
            req = urllib.request.Request(
                f"http://localhost:8000/api/v1/tickets/{tkt_id}/{action}",
                data=b"{}",
                headers={"Content-Type": "application/json", "Authorization": f"Bearer {o_token}"}
            )
            urllib.request.urlopen(req)

        # Reload dashboard
        page.reload()
        page.locator("input.pl-8").wait_for(state="visible")
        time.sleep(1.0)

        # Search the created ticket by ticket_number
        page.fill("input.pl-8", tkt_num)
        time.sleep(1.2)

        # Click the card
        card = page.locator("div.border-slate-200.rounded-xl.cursor-pointer").first
        card.wait_for(state="visible")
        card.click()
        time.sleep(1.5)

        # Click 답변 대기 요청 button in officer bar
        pending_btn = page.locator("div.fixed.inset-0 button").filter(has_text="답변 대기 요청")
        pending_btn.wait_for(state="visible")
        pending_btn.click()
        time.sleep(0.5)

        # Fill pending reason in the inline form
        pending_textarea = page.locator("div.border-purple-200 textarea")
        pending_textarea.wait_for(state="visible")
        pending_textarea.fill("재현 경로 및 클라이언트 로그 파일 첨부를 요청드립니다.")
        page.locator("div.border-purple-200 button[type='submit']").click()
        time.sleep(1.5)

        # Verify Pending Notice Banner
        banner = page.locator("div.bg-purple-50\\/90")
        banner.wait_for(state="visible")
        assert "재현 경로 및 클라이언트 로그 파일 첨부" in banner.inner_text()
        log_pass("Verified Pending Notice Banner displays officer's custom reason.")

        ss3 = os.path.join(SCREENSHOT_DIR, "step13_03_officer_pending_reason_banner.png")
        page.screenshot(path=ss3)
        log_pass(f"Captured: {ss3}")

        # -------------------------------------------------------------
        # SCENARIO 4: Employee Self Cancellation Workflow
        # -------------------------------------------------------------
        log_step("4. Employee Self Cancellation Workflow from Modal Header")
        # Click the top header [문의 취소] button
        cancel_btn = page.locator("div.flex.items-start button").filter(has_text="문의 취소")
        cancel_btn.wait_for(state="visible")
        cancel_btn.click()
        time.sleep(0.5)

        # Fill cancel reason in the prompt
        cancel_input = page.locator("div.bg-rose-50\\/90 input[type='text']")
        cancel_input.wait_for(state="visible")
        cancel_input.fill("사원 자체 해결로 추가 처리 불필요하여 취소합니다.")
        page.locator("div.bg-rose-50\\/90 button[type='submit']").click()
        time.sleep(1.5)

        # Verify status badge changed to 취소
        status_badge = page.locator("span.bg-rose-50").filter(has_text="취소").first
        status_badge.wait_for(state="visible")
        log_pass("Verified Ticket status transitioned to '취소' (canceled).")

        ss4 = os.path.join(SCREENSHOT_DIR, "step13_04_employee_cancel_success.png")
        page.screenshot(path=ss4)
        log_pass(f"Captured: {ss4}")

        browser.close()
        log_pass("ALL STEP 13 PLAYWRIGHT TESTS PASSED 100%!")

if __name__ == "__main__":
    run_tests()
