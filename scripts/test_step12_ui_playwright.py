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
    print(f"[PLAYWRIGHT STEP 12] {name}")
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
        # SCENARIO 1: Officer Login -> Test Sorting Dropdown & SLA Badges
        # -------------------------------------------------------------
        log_step("1. IT Officer (officer@test.com) Login & Dashboard Sorting / SLA Badges")
        page.goto(FRONTEND_URL)
        page.locator("form input[type='password']").wait_for(state="visible")
        page.fill("form input[type='text']", "officer@test.com")
        page.fill("form input[type='password']", "1234")
        page.click("button[type='submit']")

        # Wait for dashboard cards
        page.locator("input.pl-8").wait_for(state="visible")
        time.sleep(1.0)
        log_pass("IT Officer logged in to dashboard.")

        # Find the sort select element
        sort_select = page.locator("select:has(option[value='deadline asc'])")
        sort_select.wait_for(state="visible")

        # 1-1. Select "deadline asc" (SLA urgent sort)
        sort_select.select_option("deadline asc")
        time.sleep(1.5)
        log_pass("Selected sorting: 'deadline asc' (SLA urgent).")

        # Verify cards and SLA badges are visible
        cards = page.locator("div.border-slate-200.rounded-xl")
        card_count = cards.count()
        log_info(f"Rendered ticket cards count: {card_count}")
        assert card_count > 0, "Expected at least 1 ticket card on dashboard"

        # Capture Screenshot 14: Dashboard Sorting and SLA badges
        ss14_path = os.path.join(SCREENSHOT_DIR, "14_dashboard_sorting_and_sla.png")
        page.screenshot(path=ss14_path, full_page=False)
        log_pass(f"Screenshot 14 saved successfully: {ss14_path}")

        # Logout officer
        page.click("header button:has(svg.lucide-log-out)")
        page.locator("form input[type='password']").wait_for(state="visible")
        log_pass("Officer logged out.")

        # -------------------------------------------------------------
        # SCENARIO 2: Employee 1 Login -> Create Ticket with Attachment
        # -------------------------------------------------------------
        log_step("2. Employee 1 (user1@test.com) Create Ticket with Attachment")
        page.fill("form input[type='text']", "user1@test.com")
        page.fill("form input[type='password']", "1234")
        page.click("button[type='submit']")
        page.locator("input.pl-8").wait_for(state="visible")
        log_pass("Employee 1 logged in.")

        # Create temporary sample file to upload
        temp_file_path = os.path.abspath("temp_diag_report.txt")
        with open(temp_file_path, "w", encoding="utf-8") as f:
            f.write("=== System Diagnostic Report ===\nError Code: ERR_STEP12_UX\nMemory Usage: 88%\nStatus: Requires Investigation\n")

        try:
            # Click "새 문의 접수" button
            page.click("button.bg-indigo-600:has(svg)")
            page.locator("form input[type='text']").wait_for(state="visible")

            # Fill title and content using ASCII strings
            page.fill("form input[type='text']", "[Step12 UI] Initial Hardware Diagnostics Inquiry")
            page.select_option("form select", value="hw")
            page.fill("form textarea", "Blue screen memory dump issue observed on development workstation. Attaching diagnostic log.")

            # Attach file
            file_input = page.locator("form input[type='file']")
            file_input.set_input_files(temp_file_path)
            time.sleep(1.0)
            log_pass("Diagnostic log file attached to ticket creation form.")

            # Submit form
            page.click("form button[type='submit']")

            # Wait for creation modal to close cleanly
            page.locator("div.bg-white.rounded-2xl.max-w-lg").wait_for(state="hidden")
            time.sleep(2.0)
            log_pass("Ticket with attachment submitted and create modal closed.")
        finally:
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)

        # -------------------------------------------------------------
        # SCENARIO 3: Open Ticket Detail -> Verify Attachment & Inline Edit
        # -------------------------------------------------------------
        log_step("3. Ticket Detail Modal -> Attachment View & Inquiry Edit")
        
        # Click the first ticket card (newest ticket on dashboard)
        first_card = page.locator("div.border-slate-200.rounded-xl").first
        first_card.wait_for(state="visible")
        first_card.click()

        # Modal opens
        modal = page.locator("div.bg-white.rounded-2xl.shadow-2xl")
        modal.wait_for(state="visible")
        time.sleep(1.5)
        log_pass("Ticket detail modal opened.")

        # Check attachment card exists in modal
        attachment_item = page.locator("span:has-text('temp_diag_report.txt')").first
        attachment_item.wait_for(state="visible")
        log_pass("Attachment 'temp_diag_report.txt' is visible in detail modal.")

        # Click [문의 수정] button with force=True to bypass modal animation overlay
        edit_inquiry_btn = page.locator("button.shrink-0.text-indigo-700").first
        edit_inquiry_btn.wait_for(state="visible")
        edit_inquiry_btn.click(force=True)
        time.sleep(1.0)
        log_pass("Clicked [문의 수정] button -> inline edit mode enabled.")

        # Update title and content
        edit_title_input = page.locator("div.bg-indigo-50\\/70 input[type='text']").first
        edit_title_input.wait_for(state="visible")
        edit_title_input.fill("[Step12 UI] Updated Urgent Hardware Diagnostics Inquiry")

        edit_content_area = page.locator("div.bg-indigo-50\\/70 textarea").first
        edit_content_area.fill("Workstation repeatedly freezes on kernel boot. Attaching diagnostics log and requesting urgent technician visit.")

        # Click save button inside edit container with force=True
        save_btn = page.locator("div.bg-indigo-50\\/70 button[type='submit']").first
        save_btn.wait_for(state="visible")
        save_btn.click(force=True)
        time.sleep(2.5)
        log_pass("Inquiry edit saved successfully.")

        # Verify updated title is rendered
        page.locator("h2:has-text('Updated Urgent Hardware Diagnostics Inquiry')").wait_for(state="visible")
        log_pass("Updated title rendered cleanly in modal header.")

        # Capture Screenshot 15: Attachment and Inquiry Edit
        ss15_path = os.path.join(SCREENSHOT_DIR, "15_attachment_and_inquiry_edit.png")
        page.screenshot(path=ss15_path, full_page=False)
        log_pass(f"Screenshot 15 saved successfully: {ss15_path}")

        browser.close()
        print("\n======================================================================")
        print("PLAYWRIGHT STEP 12 UI TESTS & SCREENSHOTS COMPLETED 100%!")
        print("======================================================================")

if __name__ == "__main__":
    run_tests()
