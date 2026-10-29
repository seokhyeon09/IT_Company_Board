# -*- coding: utf-8 -*-
"""29단계 MTTR(평균 해결 시간) 기록, 보존, 집계 및 제외 규칙 단위 테스트 (5종)."""
from datetime import timedelta
from odoo import fields
from odoo.tests.common import TransactionCase
from ..utils.stats_calculator import compute_officer_stats_payload


class TestMttrStats(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        Users = cls.env["res.users"].with_context(no_reset_password=True)
        grp_base = cls.env.ref("base.group_user")
        grp_user = cls.env.ref("it_helpdesk.group_helpdesk_user")
        grp_officer = cls.env.ref("it_helpdesk.group_helpdesk_officer")

        cls.emp = Users.create({
            "name": "MTTR사원",
            "login": "mttr_emp@test.com",
            "email": "mttr_emp@test.com",
            "groups_id": [(6, 0, [grp_base.id, grp_user.id])],
        })
        cls.officer = Users.create({
            "name": "MTTR담당자",
            "login": "mttr_officer@test.com",
            "email": "mttr_officer@test.com",
            "groups_id": [(6, 0, [grp_base.id, grp_user.id, grp_officer.id])],
        })
        cls.Ticket = cls.env["it.helpdesk.ticket"]

    def _create_in_progress_ticket(self, category="hw"):
        t = self.Ticket.with_user(self.emp).create({
            "title": "MTTR 테스트 티켓",
            "content": "<p>본문</p>",
            "category": category,
            "priority": "1",
            "author_id": self.emp.id,
        })
        t.with_user(self.officer).action_assign_to_user(self.officer)
        t.with_user(self.officer).action_start_progress()
        return t

    def test_01_action_resolve_sets_first_resolved_date(self):
        """해결 완료(action_resolve) 시 first_resolved_date와 resolution_hours가 기록된다."""
        t = self._create_in_progress_ticket()
        self.assertFalse(t.first_resolved_date)
        t.sudo().write({"resolution_note": "<p>조치 완료</p>"})
        t.with_user(self.officer).action_resolve()
        self.assertTrue(t.first_resolved_date)
        # create_date 대비 2.5시간 후로 설정 시 resolution_hours == 2.5 검증
        t.sudo().write({"first_resolved_date": t.create_date + timedelta(hours=2, minutes=30)})
        self.assertEqual(t.resolution_hours, 2.5)

    def test_02_reopen_and_reresolve_preserves_first_resolved_date(self):
        """재문의 또는 재오픈 후 다시 해결 완료해도 최초 해결 시각(first_resolved_date)은 바뀌지 않는다."""
        t = self._create_in_progress_ticket()
        t.sudo().write({"resolution_note": "<p>1차 조치</p>"})
        t.with_user(self.officer).action_resolve()
        initial_dt = t.create_date + timedelta(hours=1, minutes=30)
        t.sudo().write({"first_resolved_date": initial_dt})

        # 사원 재문의 -> 다시 해결 완료
        t.with_user(self.emp).action_restart_ticket()
        self.assertEqual(t.status, "in_progress")
        t.sudo().write({"resolution_note": "<p>2차 조치</p>"})
        t.with_user(self.officer).action_resolve()
        self.assertEqual(t.first_resolved_date, initial_dt)
        self.assertEqual(t.resolution_hours, 1.5)

    def test_03_direct_close_without_resolve_does_not_set_first_resolved_date(self):
        """resolved를 거치지 않고 in_progress에서 바로 action_close(직권 종결)한 경우 first_resolved_date는 비어 있다."""
        t = self._create_in_progress_ticket()
        t.sudo().write({"resolution_note": "<p>직권 종결 조치</p>"})
        t.with_user(self.officer).action_close()
        self.assertEqual(t.status, "closed")
        self.assertFalse(t.first_resolved_date)
        self.assertEqual(t.resolution_hours, 0.0)

    def test_04_stats_calculator_computes_officer_and_category_mttr(self):
        """담당자별 평균 해결시간과 측정 건수가 정확히 산출된다."""
        t1 = self._create_in_progress_ticket(category="hw")
        t1.sudo().write({"resolution_note": "<p>조치1</p>"})
        t1.with_user(self.officer).action_resolve()
        t1.sudo().write({"first_resolved_date": t1.create_date + timedelta(hours=2)})

        t2 = self._create_in_progress_ticket(category="hw")
        t2.sudo().write({"resolution_note": "<p>조치2</p>"})
        t2.with_user(self.officer).action_resolve()
        t2.sudo().write({"first_resolved_date": t2.create_date + timedelta(hours=4)})

        stats = compute_officer_stats_payload(self.env, self.officer)
        my_row = next(o for o in stats["officers"] if o["officer_id"] == self.officer.id)
        self.assertEqual(my_row["resolved_measured_count"], 2)
        self.assertEqual(my_row["avg_resolution_hours"], 3.0)

    def test_05_canceled_ticket_excluded_from_mttr(self):
        """해결 후 취소(canceled)된 티켓은 MTTR 계산 모수에서 제외된다."""
        t = self._create_in_progress_ticket(category="sw")
        t.sudo().write({"resolution_note": "<p>조치</p>"})
        t.with_user(self.officer).action_resolve()
        t.sudo().write({"first_resolved_date": t.create_date + timedelta(hours=10)})
        t.with_user(self.emp).action_cancel()
        self.assertEqual(t.status, "canceled")

        stats = compute_officer_stats_payload(self.env, self.officer)
        my_row = next(o for o in stats["officers"] if o["officer_id"] == self.officer.id)
        self.assertEqual(my_row["resolved_measured_count"], 0)
        self.assertEqual(my_row["avg_resolution_hours"], 0.0)
