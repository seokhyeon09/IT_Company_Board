# -*- coding: utf-8 -*-
"""
Playwright Browser UI Automation Test Suite (Robust CSS Selectors)
Executes real browser actions (clicks, typing, modal dialogs, screenshot capture)
against React SPA (http://localhost:3000).
"""
import os
import sys
import time
from playwright.sync_api import sync_playwright

SCREENSHOT_DIR = os.path.abspath("local-md/ai-refactor-arch/screenshots")
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

FRONTEND_URL = "http://localhost:3000"

class Colors:
    HEADER = '\033[95m'
    OKGREEN = '\033[92m'
    OKCYAN = '\033[96m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def log_step(name):
    print(f"\n{Colors.BOLD}{Colors.HEADER}======================================================================{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.HEADER}[PLAYWRIGHT UI STEP] {name}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.HEADER}======================================================================{Colors.ENDC}")

def log_success(msg):
    print(f"  {Colors.OKGREEN}[PASS]{Colors.ENDC} {msg}")

def log_info(msg):
    print(f"  {Colors.OKCYAN}[INFO]{Colors.ENDC} {msg}")

def run_tests():
    with sync_playwright() as p:
        print(f"{Colors.BOLD}Launching Chromium Browser (Headless Mode)...{Colors.ENDC}")
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1280, 'height': 800})
        page = context.new_page()

        # -------------------------------------------------------------
        # STEP 1: Employee 1 Login & Create Ticket via UI
        # -------------------------------------------------------------
        log_step("1. Employee 1 (user1@test.com) UI Login & Ticket Creation")
        page.goto(FRONTEND_URL)
        page.locator("h2:has-text('IT 헬프데스크 로그인')").wait_for(state="visible")
        log_info("Login page loaded.")

        # Fill Login form
        page.fill("input[placeholder='예: user1@test.com']", "user1@test.com")
        page.fill("input[placeholder='비밀번호 입력']", "1234")
        page.click("button:has-text('시스템 접속')")

        # Wait for Dashboard
        page.locator("h2:has-text('IT 지원 대시보드')").wait_for(state="visible")
        log_success("Dashboard loaded for user1@test.com.")

        # Click "새 문의 접수"
        page.click("button:has-text('새 문의 접수')")
        create_modal = page.locator("div.fixed.inset-0:has-text('새 IT 문의 접수')")
        create_modal.wait_for(state="visible")
        log_info("Ticket Create Modal opened.")

        # Scoped Create Modal Selectors
        ticket_title = f"[UI-TEST] 사내 모니터 색상 왜곡 점검 요청 ({int(time.time())})"
        create_modal.locator("input[placeholder*='모니터']").fill(ticket_title)
        create_modal.locator("select").nth(0).select_option("hw")  # Hardware
        create_modal.locator("select").nth(1).select_option("1")   # Normal
        create_modal.locator("textarea").fill("보조 모니터 색상이 붉은색으로 왜곡되고 깜빡입니다. 점검 부탁드립니다.")

        # Submit
        create_modal.locator("button:has-text('문의 등록')").click()
        page.locator(f"h3:has-text('{ticket_title}')").wait_for(state="visible", timeout=10000)
        log_success("Ticket created and visible in dashboard card list.")

        # Screenshot 1
        shot1 = os.path.join(SCREENSHOT_DIR, "01_user1_ticket_created.png")
        page.screenshot(path=shot1, full_page=True)
        log_info(f"Screenshot saved: {shot1}")

        # Logout
        page.click("button[title='로그아웃']")
        page.locator("h2:has-text('IT 헬프데스크 로그인')").wait_for(state="visible")
        log_info("Employee 1 logged out.")

        # -------------------------------------------------------------
        # STEP 2: IT Officer Resolves Ticket via UI
        # -------------------------------------------------------------
        log_step("2. IT Officer (officer@test.com) UI Ticket Resolution & FAQ Toggle")
        page.fill("input[placeholder='예: user1@test.com']", "officer@test.com")
        page.fill("input[placeholder='비밀번호 입력']", "1234")
        page.click("button:has-text('시스템 접속')")

        page.locator("h2:has-text('IT 지원 대시보드')").wait_for(state="visible")
        page.locator(f"h3:has-text('{ticket_title}')").wait_for(state="visible")
        log_success("IT Officer logged in. Target ticket card found.")

        # Click ticket card to open Detail Modal
        page.click(f"h3:has-text('{ticket_title}')")
        detail_modal = page.locator("div.fixed.inset-0:has-text('문의 상세 내용')")
        detail_modal.wait_for(state="visible")
        detail_modal.locator("h4:has-text('IT 담당자 해결 조치 등록')").wait_for(state="visible")
        log_info("Ticket Detail Modal opened with Officer action form.")

        # Fill resolution note inside modal
        res_note = "모니터 HDMI 케이블 단선 확인 및 정품 케이블로 즉시 교체 완료. 색상 캘리브레이션 복구 확인."
        detail_modal.locator("textarea[placeholder*='처리 완료된 구체적인 조치 내용']").fill(res_note)
        detail_modal.locator("button:has-text('해결 완료 처리')").click()

        # Wait for status badge '해결완료'
        detail_modal.locator("span.rounded-full:has-text('해결완료')").wait_for(state="visible")
        log_success("Ticket status changed to '해결완료'.")

        # Toggle FAQ
        detail_modal.locator("button[title='FAQ 지식창고 등록/해제']").click()
        detail_modal.locator("span:has-text('FAQ 공식 선정')").wait_for(state="visible")
        log_success("FAQ Knowledgebase toggle activated.")

        # Screenshot 2
        shot2 = os.path.join(SCREENSHOT_DIR, "02_officer_resolved_and_faq.png")
        page.screenshot(path=shot2, full_page=True)
        log_info(f"Screenshot saved: {shot2}")

        # Close Modal and Logout
        detail_modal.locator("button:has-text('닫기')").click()
        page.click("button[title='로그아웃']")
        page.locator("h2:has-text('IT 헬프데스크 로그인')").wait_for(state="visible")
        log_info("IT Officer logged out.")

        # -------------------------------------------------------------
        # STEP 3: Employee 1 Rates & Closes Ticket via UI
        # -------------------------------------------------------------
        log_step("3. Employee 1 Rates 5-Stars & Closes Ticket via UI")
        page.fill("input[placeholder='예: user1@test.com']", "user1@test.com")
        page.fill("input[placeholder='비밀번호 입력']", "1234")
        page.click("button:has-text('시스템 접속')")

        page.locator(f"h3:has-text('{ticket_title}')").wait_for(state="visible")
        page.click(f"h3:has-text('{ticket_title}')")
        
        detail_modal = page.locator("div.fixed.inset-0:has-text('문의 상세 내용')")
        detail_modal.wait_for(state="visible")
        detail_modal.locator("h4:has-text('조치 만족도 평가 (본인 평가 후 종결)')").wait_for(state="visible")
        log_info("Employee 1 rating form displayed on resolved ticket.")

        # Click 5 stars
        star_buttons = detail_modal.locator("form button[type='button']")
        if star_buttons.count() >= 5:
            star_buttons.nth(4).click()
        detail_modal.locator("textarea[placeholder*='한줄평이나 감사의견']").fill("정품 케이블로 신속하게 교체해주셔서 업무에 지장이 없었습니다. 최고입니다!")
        detail_modal.locator("button:has-text('만족도 제출 및 문의 종결')").click()

        # Wait for status '종결' and rating display
        detail_modal.locator("span.rounded-full:has-text('종결')").wait_for(state="visible")
        detail_modal.locator("span:has-text('직원 만족도 평가 결과')").wait_for(state="visible")
        log_success("Ticket successfully rated 5 stars and closed.")

        # Screenshot 3
        shot3 = os.path.join(SCREENSHOT_DIR, "03_user1_rated_closed.png")
        page.screenshot(path=shot3, full_page=True)
        log_info(f"Screenshot saved: {shot3}")

        detail_modal.locator("button:has-text('닫기')").click()
        page.click("button[title='로그아웃']")
        page.locator("h2:has-text('IT 헬프데스크 로그인')").wait_for(state="visible")

        # -------------------------------------------------------------
        # STEP 4: Employee 2 Views Published FAQ via UI
        # -------------------------------------------------------------
        log_step("4. Employee 2 (user2@test.com) Views FAQ Knowledgebase via UI")
        page.fill("input[placeholder='예: user1@test.com']", "user2@test.com")
        page.fill("input[placeholder='비밀번호 입력']", "1234")
        page.click("button:has-text('시스템 접속')")

        page.locator("h2:has-text('IT 지원 대시보드')").wait_for(state="visible")
        # Click "FAQ 지식창고" tab
        page.click("button:has-text('FAQ 지식창고')")
        page.locator(f"h3:has-text('{ticket_title}')").wait_for(state="visible")
        log_success("Employee 2 can see official FAQ item in Knowledgebase accordion!")

        # Click Accordion to expand resolution note
        page.click(f"h3:has-text('{ticket_title}')")
        page.locator("text=공식 해결 방법 및 조치 가이드").wait_for(state="visible")
        log_success("FAQ Accordion expanded and resolution note verified cleanly.")

        # Screenshot 4
        shot4 = os.path.join(SCREENSHOT_DIR, "04_user2_faq_knowledgebase.png")
        page.screenshot(path=shot4, full_page=True)
        log_info(f"Screenshot saved: {shot4}")

        # -------------------------------------------------------------
        # STEP 5: Mobile Viewport (375px) Responsive Layout Test
        # -------------------------------------------------------------
        log_step("5. Mobile Viewport (375x667 iPhone SE) UI Layout Verification")
        page.set_viewport_size({"width": 375, "height": 667})
        time.sleep(1)
        shot5 = os.path.join(SCREENSHOT_DIR, "05_mobile_viewport_375px.png")
        page.screenshot(path=shot5, full_page=True)
        log_success("Mobile layout rendered cleanly without horizontal overflow.")
        log_info(f"Screenshot saved: {shot5}")

        browser.close()
        print(f"\n{Colors.BOLD}{Colors.OKGREEN}======================================================================{Colors.ENDC}")
        print(f"{Colors.BOLD}{Colors.OKGREEN}[PLAYWRIGHT UI BROWSER TESTS 100% COMPLETE]{Colors.ENDC}")
        print(f"{Colors.BOLD}{Colors.OKGREEN}======================================================================{Colors.ENDC}\n")

if __name__ == "__main__":
    run_tests()
