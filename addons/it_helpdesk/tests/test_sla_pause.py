# -*- coding: utf-8 -*-
"""SLA 일시정지, 기한 연장, 최초 해결 준수 스냅샷 및 백필 테스트."""
from datetime import timedelta
from odoo import fields
from odoo.tests.common import TransactionCase
from ..utils.sla_backfill import backfill_sla_fields
from ..utils.ticket_serializer import serialize_ticket_detail


class TestSlaPause(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        Users = cls.env["res.users"].with_context(no_reset_password=True)
        grp_base = cls.env.ref("base.group_user")
        grp_user = cls.env.ref("it_helpdesk.group_helpdesk_user")
        grp_officer = cls.env.ref("it_helpdesk.group_helpdesk_officer")

        cls.emp = Users.create({
            "name": "일시정지사원",
            "login": "sla_pause_emp@test.com",
            "email": "sla_pause_emp@test.com",
            "groups_id": [(6, 0, [grp_base.id, grp_user.id])],
        })
        cls.officer = Users.create({
            "name": "일시정지담당자",
            "login": "sla_pause_officer@test.com",
            "email": "sla_pause_officer@test.com",
            "groups_id": [(6, 0, [grp_base.id, grp_user.id, grp_officer.id])],
        })
        cls.Ticket = cls.env["it.helpdesk.ticket"]

    def _create_in_progress(self, priority="3", deadline_delta=timedelta(hours=4)):
        now = fields.Datetime.now()
        t = self.Ticket.with_user(self.emp).create({
            "title": "SLA 일시정지 테스트 티켓",
            "content": "<p>테스트 상세 내용</p>",
            "category": "hw",
            "priority": priority,
        })
        t.with_user(self.officer).action_assign_to_me()
        t.with_user(self.officer).action_start_progress()
        t.sudo().write({"deadline": now + deadline_delta})
        return t

    def test_01_pending_pauses_sla_and_excludes_overdue_and_cron(self):
        """답변 대기 전환 시 일시정지 시작이 기록되고 과거 기한이어도 초과/크론 대상에서 제외된다."""
        now = fields.Datetime.now()
        t = self._create_in_progress(deadline_delta=timedelta(minutes=-30))
        t.with_user(self.officer).action_pending()

        self.assertTrue(t.sla_paused_at)
        self.assertEqual(t.sla_state, "paused")
        self.assertFalse(t.is_overdue)
        self.assertNotIn(t.id, self.Ticket.search([("is_overdue", "=", True)]).ids)
        self.assertIn(t.id, self.Ticket.search([("sla_state", "=", "paused")]).ids)

        self.Ticket._cron_sla_monitor()
        t.invalidate_recordset()
        self.assertFalse(t.sla_warned_at)
        self.assertFalse(t.sla_escalated_at)
        self.assertGreaterEqual((now + timedelta(minutes=5)), t.sla_paused_at)

    def test_02_resume_extends_deadline_and_resets_flags(self):
        """2시간 일시정지 후 재개하면 마감 기한이 약 2시간 연장되고 경고 플래그가 초기화된다."""
        now = fields.Datetime.now()
        t = self._create_in_progress(deadline_delta=timedelta(hours=2))
        orig_deadline = t.deadline

        t.with_user(self.officer).action_pending()
        t.sudo().write({
            "sla_paused_at": now - timedelta(hours=2),
            "sla_warned_at": now - timedelta(minutes=30),
            "sla_escalated_at": now - timedelta(minutes=10),
        })
        t.with_user(self.officer).action_start_progress()

        self.assertFalse(t.sla_paused_at)
        self.assertFalse(t.sla_warned_at)
        self.assertFalse(t.sla_escalated_at)
        self.assertAlmostEqual(t.sla_paused_seconds, 7200, delta=60)
        diff = (t.deadline - orig_deadline).total_seconds()
        self.assertAlmostEqual(diff, 7200, delta=60)

    def test_03_multiple_pauses_accumulate_seconds(self):
        """답변 대기 2회 반복 시 누적 일시정지 초가 합산된다."""
        now = fields.Datetime.now()
        t = self._create_in_progress(deadline_delta=timedelta(hours=4))
        orig_deadline = t.deadline

        for _ in range(2):
            t.with_user(self.officer).action_pending()
            t.sudo().write({"sla_paused_at": now - timedelta(hours=1)})
            t.with_user(self.officer).action_start_progress()

        self.assertAlmostEqual(t.sla_paused_seconds, 7200, delta=60)
        self.assertAlmostEqual((t.deadline - orig_deadline).total_seconds(), 7200, delta=60)

    def test_04_resolve_from_pending_and_first_resolved_snapshot(self):
        """대기 중 해결 시 유효 기한 기준으로 최초 해결 준수 여부가 기록되고 재해결 시 불변이다."""
        now = fields.Datetime.now()
        # Case A: deadline은 1시간 전이지만 3시간 전부터 일시정지 -> 유효 기한 +2시간 -> 준수(True)
        t_ok = self._create_in_progress(deadline_delta=timedelta(hours=-1))
        t_ok.with_user(self.officer).action_pending()
        t_ok.sudo().write({
            "sla_paused_at": now - timedelta(hours=3),
            "resolution_note": "<p>조치 완료</p>",
        })
        t_ok.with_user(self.officer).action_resolve()
        self.assertTrue(t_ok.first_resolved_on_time)
        self.assertAlmostEqual(t_ok.sla_paused_seconds, 10800, delta=60)
        self.assertGreater(t_ok.deadline, now)

        # Case B: 일시정지 없이 기한 초과 해결 -> False, 이후 기한 늘려 재해결해도 False 유지
        t_late = self._create_in_progress(deadline_delta=timedelta(hours=-2))
        t_late.sudo().write({"resolution_note": "<p>지연 조치</p>"})
        t_late.with_user(self.officer).action_resolve()
        self.assertFalse(t_late.first_resolved_on_time)

        t_late.with_user(self.emp).action_restart_ticket()
        t_late.sudo().write({"deadline": now + timedelta(hours=10)})
        t_late.with_user(self.officer).action_resolve()
        self.assertFalse(t_late.first_resolved_on_time)

    def test_05_priority_change_preserves_paused_seconds(self):
        """긴급도 변경 시 create_date + 새 SLA 시간 + 누적 일시정지 시간으로 마감 기한이 재산정된다."""
        now = fields.Datetime.now()
        t = self._create_in_progress(priority="0", deadline_delta=timedelta(hours=72))
        t.with_user(self.officer).action_pending()
        t.sudo().write({"sla_paused_at": now - timedelta(hours=2)})
        t.with_user(self.officer).action_start_progress()

        t.with_user(self.officer).write({"priority": "3"})
        expected = t.create_date + timedelta(hours=4) + timedelta(seconds=t.sla_paused_seconds)
        self.assertAlmostEqual((t.deadline - expected).total_seconds(), 0, delta=5)

    def test_06_employee_restart_from_pending_extends_deadline_without_access_error(self):
        """요청 직원이 답변 대기 회신으로 재개해도 권한 오류 없이 마감 기한이 연장된다."""
        now = fields.Datetime.now()
        t = self._create_in_progress(deadline_delta=timedelta(hours=3))
        orig_deadline = t.deadline
        t.with_user(self.officer).action_pending()
        t.sudo().write({"sla_paused_at": now - timedelta(hours=1)})

        t.with_user(self.emp).action_restart_ticket()
        self.assertEqual(t.status, "in_progress")
        self.assertFalse(t.sla_paused_at)
        self.assertAlmostEqual(t.sla_paused_seconds, 3600, delta=60)
        self.assertAlmostEqual((t.deadline - orig_deadline).total_seconds(), 3600, delta=60)

    def test_07_detail_serialization_includes_pause_fields(self):
        """상세 직렬화 결과에 sla_state='paused', sla_paused_at, sla_paused_seconds가 포함된다."""
        t = self._create_in_progress(deadline_delta=timedelta(hours=2))
        t.with_user(self.officer).action_pending()
        detail = serialize_ticket_detail(t, self.officer, self.env)
        self.assertEqual(detail["sla_state"], "paused")
        self.assertTrue(detail["sla_paused_at"])
        self.assertEqual(detail["sla_paused_seconds"], 0)

    def test_08_backfill_sla_fields_idempotent(self):
        """백필 함수는 pending 시작 시각과 최초 해결 준수 스냅샷을 채우며 재실행 시 멱등이다."""
        now = fields.Datetime.now()
        msg_dt = now - timedelta(hours=5)
        t_pend = self.Ticket.sudo().create({
            "title": "백필 대기 티켓",
            "content": "<p>대기</p>",
            "status": "pending",
            "author_id": self.emp.id,
            "deadline": now + timedelta(hours=4),
        })
        msg = t_pend.sudo().message_post(
            body='<div data-msg-type="pending_request"><b>[답변 대기 요청]</b></div>'
        )
        msg.sudo().write({"date": msg_dt})
        t_pend.sudo().write({"sla_paused_at": False})

        t_res_ok = self.Ticket.sudo().create({
            "title": "백필 준수 해결 티켓",
            "content": "<p>해결</p>",
            "status": "resolved",
            "resolution_note": "<p>완료</p>",
            "author_id": self.emp.id,
            "deadline": now + timedelta(hours=2),
            "first_resolved_date": now - timedelta(hours=1),
        })
        t_res_late = self.Ticket.sudo().create({
            "title": "백필 초과 해결 티켓",
            "content": "<p>해결</p>",
            "status": "resolved",
            "resolution_note": "<p>완료</p>",
            "author_id": self.emp.id,
            "deadline": now - timedelta(hours=3),
            "first_resolved_date": now - timedelta(hours=1),
        })

        backfill_sla_fields(self.env)
        t_pend.invalidate_recordset()
        t_res_ok.invalidate_recordset()
        t_res_late.invalidate_recordset()

        self.assertEqual(t_pend.sla_paused_at, msg_dt)
        self.assertTrue(t_res_ok.first_resolved_on_time)
        self.assertFalse(t_res_late.first_resolved_on_time)

        # 두 번째 실행 시에도 값 불변(멱등)
        backfill_sla_fields(self.env)
        t_pend.invalidate_recordset()
        t_res_ok.invalidate_recordset()
        t_res_late.invalidate_recordset()
        self.assertEqual(t_pend.sla_paused_at, msg_dt)
        self.assertTrue(t_res_ok.first_resolved_on_time)
        self.assertFalse(t_res_late.first_resolved_on_time)
