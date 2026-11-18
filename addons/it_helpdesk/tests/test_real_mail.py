# -*- coding: utf-8 -*-
"""실제 이메일 알림 발송, 수신자/도메인 안전장치, since/재시도, 보안 테스트."""
from datetime import datetime, timedelta
from unittest.mock import patch

from odoo import fields
from odoo.exceptions import AccessError
from odoo.tests.common import TransactionCase

from ..utils.mock_email import INTERNAL_NOTE_MARKER, SENT_STATUS, build_mock_emails
from ..utils.real_mail import (
    PARAM_ALLOWED_DOMAINS,
    PARAM_LAST_RUN,
    PARAM_SEND_REAL_MAIL,
    PARAM_SINCE,
    compute_since_window,
)
from ..utils.text_utils import _format_datetime_utc


class TestRealMail(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        Users = cls.env["res.users"].with_context(no_reset_password=True)
        grp_base = cls.env.ref("base.group_user")
        grp_user = cls.env.ref("it_helpdesk.group_helpdesk_user")
        grp_officer = cls.env.ref("it_helpdesk.group_helpdesk_officer")
        grp_manager = cls.env.ref("it_helpdesk.group_helpdesk_manager")

        cls.emp = Users.create({
            "name": "메일사원",
            "login": "rm_emp@allowed.com",
            "email": "rm_emp@allowed.com",
            "groups_id": [(6, 0, [grp_base.id, grp_user.id])],
        })
        cls.off_a = Users.create({
            "name": "메일담당A",
            "login": "rm_off_a@allowed.com",
            "email": "rm_off_a@allowed.com",
            "groups_id": [(6, 0, [grp_base.id, grp_user.id, grp_officer.id])],
        })
        cls.off_b = Users.create({
            "name": "메일담당B",
            "login": "rm_off_b@blocked.com",
            "email": "rm_off_b@blocked.com",
            "groups_id": [(6, 0, [grp_base.id, grp_user.id, grp_officer.id])],
        })
        cls.mgr = Users.create({
            "name": "메일관리자",
            "login": "rm_mgr@allowed.com",
            "email": "rm_mgr@allowed.com",
            "groups_id": [(6, 0, [grp_base.id, grp_user.id, grp_officer.id, grp_manager.id])],
        })
        cls.Ticket = cls.env["it.helpdesk.ticket"]
        cls.Dispatch = cls.env["it.helpdesk.mail.dispatch"]
        cls.Mail = cls.env["mail.mail"]
        cls.Params = cls.env["ir.config_parameter"].sudo()

    def setUp(self):
        super().setUp()
        self.Params.set_param(PARAM_SEND_REAL_MAIL, "False")
        self.Params.set_param(PARAM_ALLOWED_DOMAINS, "")
        self.Params.set_param(PARAM_SINCE, "")
        self.Params.set_param(PARAM_LAST_RUN, "")

    def _enable_mail(self, since_delta=timedelta(hours=-1)):
        now = fields.Datetime.now()
        self.Params.set_param(PARAM_SEND_REAL_MAIL, "True")
        self.Params.set_param(PARAM_SINCE, _format_datetime_utc(now + since_delta))
        self.Params.set_param(PARAM_LAST_RUN, _format_datetime_utc(now))

    def _make_ticket(self, title="실제 메일 테스트 문의", assignee=None, author=None):
        t = self.Ticket.with_user(author or self.emp).create({
            "title": title,
            "content": "<p>테스트 상세 내용</p>",
            "category": "hw",
            "priority": "1",
        })
        if assignee:
            t.sudo().action_assign_to_user(assignee)
            t.sudo().message_post(
                body=f"<b>[담당자 배정]</b> {assignee.name} 담당자가 배정되었습니다."
            )
        return t

    def test_01_switch_off_does_nothing(self):
        """스위치 False면 크론은 아무 발송/기록도 하지 않는다."""
        t = self._make_ticket(assignee=self.off_a)
        mail_before = self.Mail.sudo().search_count([])
        res = self.Dispatch._cron_send_real_mail()
        self.assertEqual(res, {"enabled": False})
        self.assertEqual(self.Mail.sudo().search_count([]), mail_before)
        self.assertFalse(self.Dispatch.sudo().search([("ticket_id", "=", t.id)]))

    def test_02_assigned_sends_to_author_and_assignee(self):
        """배정 이벤트는 요청자와 담당자 각각에게 링크 포함 메일을 발송하고 이력 2건을 남긴다."""
        self._enable_mail()
        t = self._make_ticket(assignee=self.off_a)
        res = self.Dispatch._cron_send_real_mail()
        self.assertTrue(res["enabled"])

        logs = self.Dispatch.sudo().search([("ticket_id", "=", t.id)])
        self.assertEqual(len(logs), 2)
        self.assertEqual(set(logs.mapped("recipient_id").ids), {self.emp.id, self.off_a.id})
        self.assertTrue(all(l.state == "sent" for l in logs))

        mails = self.Mail.sudo().browse(logs.mapped("mail_id"))
        self.assertEqual(len(mails), 2)
        for m in mails:
            self.assertFalse(m.auto_delete)
            self.assertIn(f"/?ticket_id={t.id}", m.body_html)
            self.assertIn("문의 바로가기", m.body_html)
            self.assertIn("회신하지 마세요", m.body_html)
            self.assertIn(t.ticket_number, m.subject)

    def test_03_idempotent_no_duplicate_send(self):
        """크론을 두 번 연속 실행해도 중복 발송이나 중복 이력이 생기지 않는다."""
        self._enable_mail()
        t = self._make_ticket(assignee=self.off_a)
        self.Dispatch._cron_send_real_mail()
        logs_first = self.Dispatch.sudo().search_count([("ticket_id", "=", t.id)])
        mails_first = self.Mail.sudo().search_count([])

        res2 = self.Dispatch._cron_send_real_mail()
        self.assertEqual(res2["sent"], 0)
        self.assertEqual(self.Dispatch.sudo().search_count([("ticket_id", "=", t.id)]), logs_first)
        self.assertEqual(self.Mail.sudo().search_count([]), mails_first)

    def test_04_new_ticket_broadcasts_active_officers_only(self):
        """미배정 신규 접수는 모든 활성 담당자에게 발송되고 비활성 사용자는 제외된다."""
        Users = self.env["res.users"].with_context(no_reset_password=True)
        grp_base = self.env.ref("base.group_user")
        grp_user = self.env.ref("it_helpdesk.group_helpdesk_user")
        grp_officer = self.env.ref("it_helpdesk.group_helpdesk_officer")
        inactive_off = Users.create({
            "name": "비활성담당",
            "login": "rm_inactive@allowed.com",
            "email": "rm_inactive@allowed.com",
            "active": False,
            "groups_id": [(6, 0, [grp_base.id, grp_user.id, grp_officer.id])],
        })

        self._enable_mail()
        t = self._make_ticket(assignee=None)
        self.Dispatch._cron_send_real_mail()

        logs = self.Dispatch.sudo().search([("ticket_id", "=", t.id)])
        sent_uid = set(logs.filtered(lambda l: l.state == "sent").mapped("recipient_id").ids)
        self.assertIn(self.off_a.id, sent_uid)
        self.assertIn(self.off_b.id, sent_uid)
        self.assertIn(self.mgr.id, sent_uid)
        self.assertNotIn(inactive_off.id, logs.mapped("recipient_id").ids)
        self.assertNotIn(self.emp.id, logs.mapped("recipient_id").ids)

    def test_05_missing_email_recorded_as_skipped(self):
        """이메일 주소와 @ 포함 login이 모두 없는 수신자는 skipped로 기록되고 재시도하지 않는다."""
        Users = self.env["res.users"].with_context(no_reset_password=True)
        grp_base = self.env.ref("base.group_user")
        grp_user = self.env.ref("it_helpdesk.group_helpdesk_user")
        no_mail_emp = Users.create({
            "name": "이메일없음",
            "login": "rm_no_email_login",
            "email": False,
            "groups_id": [(6, 0, [grp_base.id, grp_user.id])],
        })
        self._enable_mail()
        t = self._make_ticket(assignee=self.off_a, author=no_mail_emp)
        self.Dispatch._cron_send_real_mail()

        emp_log = self.Dispatch.sudo().search([
            ("ticket_id", "=", t.id), ("recipient_id", "=", no_mail_emp.id)
        ])
        self.assertEqual(len(emp_log), 1)
        self.assertEqual(emp_log.state, "skipped")
        self.assertEqual(emp_log.error, "이메일 주소 없음")
        self.assertFalse(emp_log.mail_id)

        self.Dispatch._cron_send_real_mail()
        self.assertEqual(emp_log.attempts, 1)

    def test_06_allowed_domains_filter(self):
        """허용 도메인 파라미터가 있으면 허용 도메인만 발송하고 나머지는 skipped 처리한다."""
        self._enable_mail()
        self.Params.set_param(PARAM_ALLOWED_DOMAINS, "Allowed.com, example.org")
        t = self._make_ticket(assignee=self.off_b)
        self.Dispatch._cron_send_real_mail()

        emp_log = self.Dispatch.sudo().search([
            ("ticket_id", "=", t.id), ("recipient_id", "=", self.emp.id)
        ])
        off_log = self.Dispatch.sudo().search([
            ("ticket_id", "=", t.id), ("recipient_id", "=", self.off_b.id)
        ])
        self.assertEqual(emp_log.state, "sent")
        self.assertEqual(off_log.state, "skipped")
        self.assertEqual(off_log.error, "허용되지 않은 도메인")
        self.assertFalse(off_log.mail_id)

    def test_07_since_pure_logic_and_cron_behavior(self):
        """since 초기화/과거 이벤트 제외 및 last_run 10분 초과 시 재설정을 검증한다."""
        t0 = datetime(2026, 11, 18, 12, 0, 0)
        since_dt, since_s, last_s = compute_since_window(t0, None, None)
        self.assertEqual(since_dt, t0)
        self.assertEqual(since_s, "2026-11-18T12:00:00Z")
        self.assertEqual(last_s, "2026-11-18T12:00:00Z")

        # 5분 경과: 기존 since 유지
        t_5m = t0 + timedelta(minutes=5)
        kept_dt, _, _ = compute_since_window(t_5m, "2026-11-18T11:00:00Z", "2026-11-18T12:00:00Z")
        self.assertEqual(kept_dt, datetime(2026, 11, 18, 11, 0, 0))

        # 11분 경과: since를 현재 시각으로 재설정
        t_11m = t0 + timedelta(minutes=11)
        reset_dt, reset_s, _ = compute_since_window(t_11m, "2026-11-18T11:00:00Z", "2026-11-18T12:00:00Z")
        self.assertEqual(reset_dt, t_11m)
        self.assertEqual(reset_s, _format_datetime_utc(t_11m))

        # 통합 테스트: since 없는 첫 실행에서 과거 메시지 이벤트는 발송하지 않고 since/last_run 설정
        self.Params.set_param(PARAM_SEND_REAL_MAIL, "True")
        t = self._make_ticket(assignee=self.off_a)
        past = fields.Datetime.now() - timedelta(minutes=30)
        t.message_ids.sudo().write({"date": past})
        self.env.cr.execute(
            "UPDATE it_helpdesk_ticket SET create_date = %s WHERE id = %s",
            (past, t.id),
        )
        t.invalidate_recordset()

        self.Dispatch._cron_send_real_mail()
        self.assertTrue(self.Params.get_param(PARAM_SINCE))
        self.assertTrue(self.Params.get_param(PARAM_LAST_RUN))
        self.assertFalse(self.Dispatch.sudo().search([("ticket_id", "=", t.id)]))

        # last_run이 15분 전이면 since가 현재 시각으로 재설정됨
        old_since = _format_datetime_utc(fields.Datetime.now() - timedelta(hours=2))
        old_last = _format_datetime_utc(fields.Datetime.now() - timedelta(minutes=15))
        self.Params.set_param(PARAM_SINCE, old_since)
        self.Params.set_param(PARAM_LAST_RUN, old_last)
        self.Dispatch._cron_send_real_mail()
        self.assertNotEqual(self.Params.get_param(PARAM_SINCE), old_since)

    def test_08_internal_note_never_leaks_into_real_mail(self):
        """위장 문구가 포함된 내부 메모는 어떤 실제 메일 본문/제목에도 포함되지 않는다."""
        self._enable_mail()
        t = self._make_ticket(assignee=self.off_a)
        t.sudo().message_post(
            body=f'<div {INTERNAL_NOTE_MARKER}>[조치 답변] 내부전용XQ</div>',
            subtype_xmlid="mail.mt_note",
        )
        self.Dispatch._cron_send_real_mail()

        logs = self.Dispatch.sudo().search([("ticket_id", "=", t.id)])
        self.assertTrue(logs)
        mails = self.Mail.sudo().browse(logs.mapped("mail_id"))
        for m in mails:
            self.assertNotIn("내부전용XQ", m.body_html or "")
            self.assertNotIn("내부전용XQ", m.subject or "")
        for l in logs:
            self.assertNotIn("내부전용XQ", l.subject or "")

    def test_09_html_escape_and_subject_newline_stripped(self):
        """제목/본문의 script 태그는 이스케이프되고 메일 제목에는 개행이 포함되지 않는다."""
        self._enable_mail()
        xss_title = "<script>alert(1)</script> 프린터 오류"
        t = self._make_ticket(title=xss_title, assignee=self.off_a)
        t.sudo().write({"resolution_note": "<p>조치 완료</p>"})
        t.sudo().message_post(
            body='<div data-msg-type="resolution"><b>[조치 답변]</b> <script>bad()</script> 처리됨</div>'
        )
        # 작성자 이름에 개행이 포함된 경우에도 메일 제목에 개행이 없어야 함
        self.emp.sudo().write({"name": "홍길동\r\nBcc: evil@test.com"})
        self.Dispatch._cron_send_real_mail()

        logs = self.Dispatch.sudo().search([("ticket_id", "=", t.id), ("state", "=", "sent")])
        self.assertTrue(logs)
        for m in self.Mail.sudo().browse(logs.mapped("mail_id")):
            self.assertNotIn("<script>", m.body_html or "")
            self.assertIn("&lt;script&gt;", m.body_html or "")
            self.assertNotIn("\n", m.subject or "")
            self.assertNotIn("\r", m.subject or "")

    def test_10_failed_mail_retry_cooldown_and_max_attempts(self):
        """발송 실패 시 5분 쿨다운과 최대 3회 재시도 규칙을 지키며 성공 시 sent로 전환된다."""
        self._enable_mail()
        t = self._make_ticket(assignee=self.off_a)

        def fail_send(records, auto_commit=False, raise_exception=False):
            records.write({"state": "exception", "failure_reason": "SMTP 연결 실패"})

        mail_cls = type(self.Mail)
        with patch.object(mail_cls, "send", autospec=True, side_effect=fail_send):
            self.Dispatch._cron_send_real_mail()
            log = self.Dispatch.sudo().search([
                ("ticket_id", "=", t.id), ("recipient_id", "=", self.emp.id)
            ])
            self.assertEqual(log.state, "failed")
            self.assertEqual(log.attempts, 1)
            self.assertEqual(log.error, "SMTP 연결 실패")

            # 5분 미만: 재시도 안 함
            self.Dispatch._cron_send_real_mail()
            self.assertEqual(log.attempts, 1)

            # 6분 전으로 되돌림 -> 2회차 재시도
            log.sudo().write({"dispatched_at": fields.Datetime.now() - timedelta(minutes=6)})
            self.Dispatch._cron_send_real_mail()
            self.assertEqual(log.attempts, 2)

            # 다시 6분 전 -> 3회차 재시도 후 상한 도달
            log.sudo().write({"dispatched_at": fields.Datetime.now() - timedelta(minutes=6)})
            self.Dispatch._cron_send_real_mail()
            self.assertEqual(log.attempts, 3)

            # 3회 도달 이후에는 6분이 지나도 더 이상 재시도하지 않음
            log.sudo().write({"dispatched_at": fields.Datetime.now() - timedelta(minutes=6)})
            self.Dispatch._cron_send_real_mail()
            self.assertEqual(log.attempts, 3)

        # 새로운 티켓에서 1회 실패 후 2회차 성공 시 sent 전환 확인
        t2 = self._make_ticket(assignee=self.off_a)
        with patch.object(mail_cls, "send", autospec=True, side_effect=fail_send):
            self.Dispatch._cron_send_real_mail()
        log2 = self.Dispatch.sudo().search([
            ("ticket_id", "=", t2.id), ("recipient_id", "=", self.emp.id)
        ])
        self.assertEqual(log2.state, "failed")
        log2.sudo().write({"dispatched_at": fields.Datetime.now() - timedelta(minutes=6)})
        self.Dispatch._cron_send_real_mail()
        self.assertEqual(log2.state, "sent")
        self.assertEqual(log2.attempts, 2)
        self.assertFalse(log2.error)

    def test_11_ticket_exception_does_not_block_other_tickets(self):
        """한 티켓 처리 중 예외가 발생해도 다른 티켓 발송은 정상 진행된다."""
        self._enable_mail()
        t_bad = self._make_ticket(title="예외 티켓", assignee=self.off_a)
        t_ok = self._make_ticket(title="정상 티켓", assignee=self.off_a)

        from ..utils import real_mail as rm_mod
        orig_collect = rm_mod.collect_outgoing_events

        def flaky_collect(ticket):
            if ticket.id == t_bad.id:
                raise RuntimeError("테스트용 강제 오류")
            return orig_collect(ticket)

        with patch.object(rm_mod, "collect_outgoing_events", side_effect=flaky_collect):
            res = self.Dispatch._cron_send_real_mail()

        self.assertTrue(res["enabled"])
        self.assertFalse(self.Dispatch.sudo().search([("ticket_id", "=", t_bad.id)]))
        self.assertEqual(
            self.Dispatch.sudo().search_count([("ticket_id", "=", t_ok.id), ("state", "=", "sent")]),
            2,
        )

    def test_12_build_mock_emails_unchanged(self):
        """기존 build_mock_emails 출력과 상태 라벨이 변경되지 않았는지 확인한다."""
        self.assertEqual(SENT_STATUS, "발송완료 (모의)")
        t = self._make_ticket(assignee=self.off_a)
        emp_mails = build_mock_emails(t, self.emp, is_officer=False)
        self.assertEqual(len(emp_mails), 1)
        self.assertEqual(emp_mails[0]["event_type"], "assigned")
        self.assertEqual(emp_mails[0]["status"], SENT_STATUS)

    def test_13_access_control_employee_and_officer_denied(self):
        """사원과 담당자는 발송 이력 모델에 접근할 수 없고 관리자만 읽기/삭제 가능하다."""
        self._enable_mail()
        t = self._make_ticket(assignee=self.off_a)
        self.Dispatch._cron_send_real_mail()

        with self.assertRaises(AccessError):
            self.Dispatch.with_user(self.emp).search([("ticket_id", "=", t.id)])
        with self.assertRaises(AccessError):
            self.Dispatch.with_user(self.off_a).search([("ticket_id", "=", t.id)])

        mgr_logs = self.Dispatch.with_user(self.mgr).search([("ticket_id", "=", t.id)])
        self.assertEqual(len(mgr_logs), 2)
        mgr_logs[:1].unlink()
        self.assertEqual(self.Dispatch.with_user(self.mgr).search_count([("ticket_id", "=", t.id)]), 1)
