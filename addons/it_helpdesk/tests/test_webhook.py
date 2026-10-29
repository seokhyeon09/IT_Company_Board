# -*- coding: utf-8 -*-
"""28단계 Slack 인커밍 웹훅 알림 단위 테스트 (6종)."""
from datetime import timedelta
from unittest.mock import patch, MagicMock

from odoo import fields
from odoo.tests.common import TransactionCase

from ..utils.auto_assign import create_ticket_with_auto_assign
from ..utils.webhook_notifier import notify_urgent_ticket_created

VALID_SLACK_URL = "https://hooks.slack.com/services/TEST/TEST/TEST"


class TestSlackWebhook(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        Users = cls.env["res.users"].with_context(no_reset_password=True)
        grp_base = cls.env.ref("base.group_user")
        grp_user = cls.env.ref("it_helpdesk.group_helpdesk_user")
        grp_officer = cls.env.ref("it_helpdesk.group_helpdesk_officer")

        cls.emp = Users.create({
            "name": "웹훅사원",
            "login": "webhook_emp@test.com",
            "email": "webhook_emp@test.com",
            "groups_id": [(6, 0, [grp_base.id, grp_user.id])],
        })
        cls.officer = Users.create({
            "name": "웹훅담당자",
            "login": "webhook_officer@test.com",
            "email": "webhook_officer@test.com",
            "groups_id": [(6, 0, [grp_base.id, grp_user.id, grp_officer.id])],
        })
        cls.Ticket = cls.env["it.helpdesk.ticket"]

    def test_01_disabled_when_url_empty(self):
        """SLACK_WEBHOOK_URL이 비어 있으면 긴급 티켓 접수 시에도 requests.post를 호출하지 않는다."""
        with patch.dict("os.environ", {"SLACK_WEBHOOK_URL": ""}, clear=False), \
             patch("requests.post") as mock_post:
            ticket = create_ticket_with_auto_assign(self.Ticket.with_user(self.emp), {
                "title": "긴급 VPN 접속 불가",
                "content": "<p>기밀 본문 데이터입니다</p>",
                "category": "network",
                "priority": "3",
                "author_id": self.emp.id,
            })
            self.assertTrue(ticket.exists())
            mock_post.assert_not_called()

    def test_02_urgent_ticket_sends_webhook_once(self):
        """SLACK_WEBHOOK_URL이 설정된 상태에서 긴급('3') 티켓 접수 시 1회 호출된다."""
        mock_resp = MagicMock(status_code=200)
        with patch.dict("os.environ", {"SLACK_WEBHOOK_URL": VALID_SLACK_URL}, clear=False), \
             patch("requests.post", return_value=mock_resp) as mock_post:
            ticket = create_ticket_with_auto_assign(self.Ticket.with_user(self.emp), {
                "title": "전사 네트워크 마비 긴급 신고",
                "content": "<p>민감 본문 내용 시크릿</p>",
                "category": "network",
                "priority": "3",
                "author_id": self.emp.id,
            })
            self.assertEqual(mock_post.call_count, 1)
            _, kwargs = mock_post.call_args
            sent_text = kwargs["json"]["text"]
            self.assertIn(ticket.ticket_number, sent_text)
            self.assertIn("전사 네트워크 마비 긴급 신고", sent_text)

    def test_03_non_urgent_priorities_do_not_send_webhook(self):
        """긴급('3')이 아닌 낮음/보통/높음('0','1','2') 티켓은 접수 시 웹훅을 보내지 않는다."""
        with patch.dict("os.environ", {"SLACK_WEBHOOK_URL": VALID_SLACK_URL}, clear=False), \
             patch("requests.post") as mock_post:
            for prio in ("0", "1", "2"):
                create_ticket_with_auto_assign(self.Ticket.with_user(self.emp), {
                    "title": f"일반 우선순위 문의 ({prio})",
                    "content": "<p>내용</p>",
                    "category": "sw",
                    "priority": prio,
                    "author_id": self.emp.id,
                })
            mock_post.assert_not_called()

    def test_04_webhook_exception_does_not_break_ticket_creation(self):
        """웹훅 전송 중 네트워크 예외가 발생해도 티켓 생성은 실패하지 않는다."""
        with patch.dict("os.environ", {"SLACK_WEBHOOK_URL": VALID_SLACK_URL}, clear=False), \
             patch("requests.post", side_effect=RuntimeError("Network unreachable")):
            ticket = create_ticket_with_auto_assign(self.Ticket.with_user(self.emp), {
                "title": "네트워크 예외 내성 테스트",
                "content": "<p>내용</p>",
                "category": "hw",
                "priority": "3",
                "author_id": self.emp.id,
            })
            self.assertTrue(ticket.exists())

    def test_05_payload_excludes_content_and_email_and_truncates_title(self):
        """페이로드에 본문(content)과 이메일 주소가 포함되지 않고, 80자 초과 제목은 잘린다."""
        mock_resp = MagicMock(status_code=200)
        long_title = "가" * 100
        secret_body = "SECRET_BODY_TOKEN_99999"
        with patch.dict("os.environ", {"SLACK_WEBHOOK_URL": VALID_SLACK_URL}, clear=False), \
             patch("requests.post", return_value=mock_resp) as mock_post:
            ticket = self.Ticket.sudo().create({
                "title": long_title,
                "content": f"<p>{secret_body}</p>",
                "category": "account",
                "priority": "3",
                "author_id": self.emp.id,
            })
            notify_urgent_ticket_created(ticket)
            sent_text = mock_post.call_args[1]["json"]["text"]
            self.assertNotIn(secret_body, sent_text)
            self.assertNotIn("webhook_emp@test.com", sent_text)
            self.assertIn("...", sent_text)

    def test_06_sla_escalation_triggers_webhook_and_rejects_non_slack_host(self):
        """SLA 에스컬레이션 시 웹훅이 호출되며, 허용되지 않은 호스트(http 등)는 차단된다."""
        mock_resp = MagicMock(status_code=200)
        t = self.Ticket.sudo().create({
            "title": "SLA 초과 웹훅 테스트",
            "content": "<p>내용</p>",
            "category": "hw",
            "priority": "2",
            "status": "assigned",
            "author_id": self.emp.id,
            "assignee_id": self.officer.id,
            "deadline": fields.Datetime.now() - timedelta(minutes=30),
        })
        # 1) 비허용 호스트 차단 확인
        with patch.dict("os.environ", {"SLACK_WEBHOOK_URL": "http://evil.example.com/webhook"}, clear=False), \
             patch("requests.post") as mock_post_bad:
            self.assertFalse(notify_urgent_ticket_created(t))
            mock_post_bad.assert_not_called()

        # 2) 정상 Slack URL로 에스컬레이션 크론 실행 시 1회 전송
        with patch.dict("os.environ", {"SLACK_WEBHOOK_URL": VALID_SLACK_URL}, clear=False), \
             patch("requests.post", return_value=mock_resp) as mock_post_ok:
            self.Ticket._cron_sla_monitor()
            self.assertEqual(mock_post_ok.call_count, 1)
            sent_text = mock_post_ok.call_args[1]["json"]["text"]
            self.assertIn("SLA 기한 초과 에스컬레이션", sent_text)
