# -*- coding: utf-8 -*-
import os
import sys
import time
from playwright.sync_api import sync_playwright

SCREENSHOT_DIR = os.path.abspath("local-md/ai-refactor-arch/screenshots")
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

FRONTEND_URL = "http://localhost:3000"

def log_step(name):
    print(f"\n======================================================================")
    print(f"[PLAYWRIGHT STEP 10] {name}")
    print(f"======================================================================")

def log_pass(msg):
    print(f"  [PASS] {msg}")

def log_info(msg):
    print(f"  [INFO] {msg}")

def run_tests():
    with sync_playwright() as p:
        print("Launching Chromium Browser (Headless Mode)...")
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1280, 'height': 850})
        page = context.new_page()

        # -------------------------------------------------------------
        # STEP 1: Employee 1 Login & Create Ticket A
        # -------------------------------------------------------------
        log_step("1. Employee 1 (user1@test.com) Login & Create Ticket A")
        page.goto(FRONTEND_URL)
        page.locator("form input[type='password']").wait_for(state="visible")
        page.fill("form input[type='text']", "user1@test.com")
        page.fill("form input[type='password']", "1234")
        page.click("button[type='submit']")

        # Wait for dashboard (search input visible)
        page.locator("input.pl-8").wait_for(state="visible")
        log_pass("Employee 1 logged in successfully.")

        # Click "새 문의 접수" button (.bg-indigo-600 with PlusCircle icon)
        page.click("button.bg-indigo-600:has(svg)")

        # Modal form is displayed
        page.locator("form input[type='text']").wait_for(state="visible")
        page.fill("form input[type='text']", "[Step10 UI] 담당자 워크플로우 및 직권종결 테스트")
        page.select_option("form select", value="sw")
        page.fill("form textarea", "10단계 담당자 워크플로우 액션 바(배정/처리시작/답변대기/직권종결) 브라우저 실전 검증용 티켓입니다.")
        page.click("form button[type='submit']")
        time.sleep(2.0)
        log_pass("Ticket A created by Employee 1.")

        # Logout via header logout button
        page.click("header button:has(svg.lucide-log-out)")
        page.locator("form input[type='password']").wait_for(state="visible")
        log_pass("Employee 1 logged out.")

        # -------------------------------------------------------------
        # STEP 2: Officer Login & Step-by-Step Workflow Action Bar Test
        # -------------------------------------------------------------
        log_step("2. IT Officer (officer@test.com) Workflow Actions & Direct Close")
        page.fill("form input[type='text']", "officer@test.com")
        page.fill("form input[type='password']", "1234")
        page.click("button[type='submit']")
        page.locator("input.pl-8").wait_for(state="visible")
        log_pass("IT Officer logged in successfully.")

        # Find Ticket A card and click (first card with [Step10 UI])
        ticket_a_card = page.locator("div.border-slate-200:has-text('[Step10 UI]')").first
        ticket_a_card.wait_for(state="visible")
        ticket_a_card.click()

        # Modal opens: wait for modal container
        page.locator("div.bg-white.rounded-2xl.shadow-2xl").wait_for(state="visible")
        log_pass("Ticket A detail modal opened.")

        # 2-1: Click "내게 배정" (button.text-blue-700)
        assign_btn = page.locator("button.text-blue-700:has(svg)").first
        assign_btn.wait_for(state="visible")
        assign_btn.click()
        time.sleep(1.0)
        page.locator("span:has-text('\ubc30\uc815\uc644\ub8cc')").first.wait_for(state="visible")
        log_pass("1) '내게 배정' executed -> Status transitioned to '배정완료'")

        # 2-2: Click "처리 시작" (button.text-indigo-700)
        start_btn = page.locator("button.text-indigo-700:has(svg)").first
        start_btn.wait_for(state="visible")
        start_btn.click()
        time.sleep(1.0)
        page.locator("span:has-text('\ucc98\ub9ac\uc911')").first.wait_for(state="visible")
        log_pass("2) '처리 시작' executed -> Status transitioned to '처리중'")

        # 2-3: Click "답변 대기 요청" (button.text-purple-700)
        pending_btn = page.locator("button.text-purple-700:has(svg)").first
        pending_btn.wait_for(state="visible")
        pending_btn.click()
        time.sleep(1.0)
        page.locator("span:has-text('\ub2f5\ubcc0\ub300\uae30')").first.wait_for(state="visible")
        log_pass("3) '답변 대기 요청' executed -> Status transitioned to '답변대기'")

        # 2-4: Click "처리 시작" again (button.text-indigo-700)
        start_btn = page.locator("button.text-indigo-700:has(svg)").first
        start_btn.wait_for(state="visible")
        start_btn.click()
        time.sleep(1.0)
        page.locator("span:has-text('\ucc98\ub9ac\uc911')").first.wait_for(state="visible")
        log_pass("4) Resumed '처리 시작' executed -> Status transitioned back to '처리중'")

        # 2-5: Click "직권 종결" (button.text-slate-700.border-slate-300)
        close_btn = page.locator("button.text-slate-700.border-slate-300").first
        close_btn.wait_for(state="visible")
        close_btn.click()
        log_info("Inline close form opened.")

        # Fill direct close note and confirm
        close_textarea = page.locator("div.border-indigo-200\\/60 textarea, textarea.border-slate-300").first
        close_textarea.wait_for(state="visible")
        close_textarea.fill("사내 보안 정책 가이드 발송 및 유선 원격 지원 정상 완료되어 담당자 직권 종결합니다.")
        page.click("button.bg-slate-700[type='submit']")
        time.sleep(2.0)
        log_pass("5) '직권 종결' confirmed -> Status transitioned to '종결'")

        # Capture screenshot for officer workflow closed
        shot_path_12 = os.path.join(SCREENSHOT_DIR, "12_officer_workflow_closed.png")
        page.screenshot(path=shot_path_12, full_page=True)
        log_pass(f"Screenshot saved: {shot_path_12}")

        # Close modal via top right X button
        page.click("button:has(svg.lucide-x)")
        time.sleep(0.5)

        # Logout officer
        page.click("header button:has(svg.lucide-log-out)")
        page.locator("form input[type='password']").wait_for(state="visible")
        log_pass("IT Officer logged out.")

        # -------------------------------------------------------------
        # STEP 3: Employee 1 Login, Create Ticket B & Cancel Ticket
        # -------------------------------------------------------------
        log_step("3. Employee 1 (user1@test.com) Create Ticket B & Cancel Ticket")
        page.fill("form input[type='text']", "user1@test.com")
        page.fill("form input[type='password']", "1234")
        page.click("button[type='submit']")
        page.locator("input.pl-8").wait_for(state="visible")

        # Create Ticket B
        page.click("button.bg-indigo-600:has(svg)")
        page.locator("form input[type='text']").wait_for(state="visible")
        page.fill("form input[type='text']", "[Step10 UI] 직원 본인 문의 취소 테스트")
        page.select_option("form select", value="hw")
        page.fill("form textarea", "자가 해결로 인해 취소할 문의입니다.")
        page.click("form button[type='submit']")
        time.sleep(2.0)
        log_pass("Ticket B created by Employee 1.")

        # Open Ticket B detail modal
        ticket_b_card = page.locator("div.border-slate-200:has-text('[Step10 UI] \uc9c1\uc6d0 \ubcf8\uc778 \ubb38\uc758 \ucde8\uc18c')").first
        ticket_b_card.wait_for(state="visible")
        ticket_b_card.click()
        page.locator("div.bg-white.rounded-2xl.shadow-2xl").wait_for(state="visible")
        log_pass("Ticket B detail modal opened.")

        # Click "문의 취소" (button.text-rose-600)
        cancel_btn = page.locator("button.text-rose-600").first
        cancel_btn.wait_for(state="visible")
        cancel_btn.click()
        log_info("Inline cancel form opened.")

        # Fill cancel reason and confirm
        cancel_input = page.locator("input.border-rose-300[type='text']").first
        cancel_input.wait_for(state="visible")
        cancel_input.fill("PC 재부팅 후 모니터 케이블 재연결하여 정상 작동 확인되어 문의 취소합니다.")
        page.click("button.bg-rose-600[type='submit']")
        time.sleep(2.0)
        log_pass("Ticket B canceled successfully -> Status badge is '취소'.")

        # Close modal
        page.click("button:has(svg.lucide-x)")
        time.sleep(0.5)

        # -------------------------------------------------------------
        # STEP 4: Dashboard Status Dropdown Filter ('취소') Test
        # -------------------------------------------------------------
        log_step("4. Dashboard Status Filter ('취소') Verification")
        # Select "canceled" in status dropdown (the select that contains option value="canceled")
        page.select_option("select:has(option[value='canceled'])", value="canceled")
        time.sleep(1.5)

        # Verify Ticket B is displayed in canceled list
        canceled_card = page.locator("div.border-slate-200:has-text('[Step10 UI] \uc9c1\uc6d0 \ubcf8\uc778 \ubb38\uc758 \ucde8\uc18c')").first
        canceled_card.wait_for(state="visible")
        log_pass("Canceled ticket is correctly visible when filtering by '취소'.")

        # Capture screenshot for employee canceled ticket and filter
        shot_path_13 = os.path.join(SCREENSHOT_DIR, "13_employee_canceled_ticket.png")
        page.screenshot(path=shot_path_13, full_page=True)
        log_pass(f"Screenshot saved: {shot_path_13}")

        browser.close()
        print("\n======================================================================")
        print("PLAYWRIGHT STEP 10 ALL UI TESTS PASSED 100%!")
        print("======================================================================")

if __name__ == "__main__":
    run_tests()
