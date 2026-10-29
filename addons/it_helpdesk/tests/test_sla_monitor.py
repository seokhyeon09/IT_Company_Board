# -*- coding: utf-8 -*-
"""27단계 SLA 임박 경고 및 관리자 에스컬레이션 단위 테스트 (8종)."""
from datetime import timedelta
from odoo import fields
from odoo.tests.common import TransactionCase
from ..utils.mock_email import build_mock_emails
from ..utils.ticket_serializer import serialize_ticket_detail


class TestSlaMonitor(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        Users = cls.env["res.users"].with_context(no_reset_password=True)
        grp_base = cls.env.ref("base.group_user")
        grp_user = cls.env.ref("it_helpdesk.group_helpdesk_user")
        grp_officer = cls.env.ref("it_helpdesk.group_helpdesk_officer")
        grp_manager = cls.env.ref("it_helpdesk.group_helpdesk_manager")

        cls.emp = Users.create({
            "name": "SLA사원",
            "login": "sla_emp@test.com",
            "email": "sla_emp@test.com",
            "groups_id": [(6, 0, [grp_base.id, grp_user.id])],
        })
        cls.officer = Users.create({
            "name": "SLA담당자",
            "login": "sla_officer@test.com",
            "email": "sla_officer@test.com",
            "groups_id": [(6, 0, [grp_base.id, grp_user.id, grp_officer.id])],
        })
        cls.manager = Users.create({
            "name": "SLA관리자",
            "login": "sla_manager@test.com",
            "email": "sla_manager@test.com",
            "groups_id": [(6, 0, [grp_base.id, grp_user.id, grp_officer.id, grp_manager.id])],
        })
        cls.Ticket = cls.env["it.helpdesk.ticket"]

    def _make_ticket(self, priority="3", deadline_delta_minutes=180, assignee=None, status="assigned"):
        now = fields.Datetime.now()
        vals = {
            "title": "SLA 모니터 테스트 티켓",
            "content": "<p>테스트 상세 내용</p>",
            "category": "hw",
            "priority": priority,
            "status": status,
            "author_id": self.emp.id,
            "deadline": now + timedelta(minutes=deadline_delta_minutes),
        }
        if assignee:
            vals["assignee_id"] = assignee.id
        return self.Ticket.sudo().create(vals)

    def test_01_ok_ticket_not_warned(self):
        """잔여 시간이 임계 시간보다 많이 남은 티켓은 경고나 에스컬레이션이 발생하지 않는다."""
        # 긴급('3') 임계 1시간(60분) -> 180분 남음은 ok
        t = self._make_ticket(priority="3", deadline_delta_minutes=180, assignee=self.officer)
        self.assertEqual(t.sla_state, "ok")
        self.Ticket._cron_sla_monitor()
        t.invalidate_recordset()
        self.assertFalse(t.sla_warned_at)
        self.assertFalse(t.sla_escalated_at)

    def test_02_imminent_ticket_warned_once(self):
        """임계 시간 이하로 남은 티켓은 임박 경고 노트 1건과 sla_warned_at이 기록된다."""
        t = self._make_ticket(priority="3", deadline_delta_minutes=30, assignee=self.officer)
        self.assertEqual(t.sla_state, "imminent")
        self.Ticket._cron_sla_monitor()
        t.invalidate_recordset()
        self.assertTrue(t.sla_warned_at)
        self.assertFalse(t.sla_escalated_at)
        warn_msgs = t.message_ids.filtered(lambda m: 'data-msg-type="sla_warning"' in (m.body or ""))
        self.assertEqual(len(warn_msgs), 1)

    def test_03_cron_idempotent_no_duplicate_warning(self):
        """크론을 2회 연속 실행해도 임박 경고 노트는 중복 생성되지 않는다."""
        t = self._make_ticket(priority="3", deadline_delta_minutes=30, assignee=self.officer)
        self.Ticket._cron_sla_monitor()
        first_warned_at = t.sla_warned_at
        self.Ticket._cron_sla_monitor()
        t.invalidate_recordset()
        self.assertEqual(t.sla_warned_at, first_warned_at)
        warn_msgs = t.message_ids.filtered(lambda m: 'data-msg-type="sla_warning"' in (m.body or ""))
        self.assertEqual(len(warn_msgs), 1)

    def test_04_overdue_escalation_and_manager_email(self):
        """기한 초과 시 에스컬레이션 노트가 생성되고 Manager 그룹이 모의 이메일을 수신한다."""
        t = self._make_ticket(priority="2", deadline_delta_minutes=-20, assignee=self.officer)
        self.assertEqual(t.sla_state, "overdue")
        self.Ticket._cron_sla_monitor()
        t.invalidate_recordset()
        self.assertTrue(t.sla_escalated_at)

        mgr_emails = build_mock_emails(t, self.manager, is_officer=True)
        esc_mails = [m for m in mgr_emails if m["event_type"] == "sla_escalation"]
        self.assertEqual(len(esc_mails), 1)

    def test_05_overdue_without_prior_warning_skips_warning(self):
        """임박 경고 없이 곧바로 초과된 티켓은 에스컬레이션만 기록하고 임박 경고는 생략한다."""
        t = self._make_ticket(priority="3", deadline_delta_minutes=-10, assignee=self.officer)
        self.Ticket._cron_sla_monitor()
        t.invalidate_recordset()
        self.assertTrue(t.sla_escalated_at)
        self.assertFalse(t.sla_warned_at)
        warn_msgs = t.message_ids.filtered(lambda m: 'data-msg-type="sla_warning"' in (m.body or ""))
        self.assertEqual(len(warn_msgs), 0)

    def test_06_priority_or_deadline_change_resets_flags(self):
        """우선순위 또는 마감기한 변경 시 경고/에스컬레이션 플래그가 초기화되어 재경고 가능하다."""
        t = self._make_ticket(priority="3", deadline_delta_minutes=30, assignee=self.officer)
        self.Ticket._cron_sla_monitor()
        self.assertTrue(t.sla_warned_at)
        # 마감기한을 2시간 뒤로 변경 -> 플래그 초기화
        t.sudo().write({"deadline": fields.Datetime.now() + timedelta(hours=2)})
        self.assertFalse(t.sla_warned_at)
        self.assertEqual(t.sla_state, "ok")

    def test_07_closed_resolved_canceled_excluded(self):
        """해결완료, 종결, 취소 상태 티켓은 마감 시각이 지났어도 sla_state가 none이고 크론에서 제외된다."""
        for st in ("resolved", "closed", "canceled"):
            vals = {
                "title": f"종료 상태 테스트 ({st})",
                "content": "<p>내용</p>",
                "category": "sw",
                "priority": "3",
                "status": st,
                "resolution_note": "<p>조치 완료</p>",
                "author_id": self.emp.id,
                "deadline": fields.Datetime.now() - timedelta(hours=3),
            }
            t = self.Ticket.sudo().create(vals)
            self.assertEqual(t.sla_state, "none")
            self.Ticket._cron_sla_monitor()
            self.assertFalse(t.sla_escalated_at)

    def test_08_employee_never_sees_sla_warning_or_escalation(self):
        """요청 사원(author)에게는 SLA 경고/에스컬레이션 메일과 내부 노트가 노출되지 않는다."""
        t = self._make_ticket(priority="3", deadline_delta_minutes=-15, assignee=self.officer)
        self.Ticket._cron_sla_monitor()
        emp_mails = build_mock_emails(t, self.emp, is_officer=False)
        sla_mails = [m for m in emp_mails if m["event_type"] in ("sla_warning", "sla_escalation")]
        self.assertEqual(len(sla_mails), 0)

        detail = serialize_ticket_detail(t, self.emp, self.env)
        self.assertEqual(detail["logs"], [])
        for item in detail["timeline"]:
            self.assertNotIn("SLA", item.get("content", ""))
