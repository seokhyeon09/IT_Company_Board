# -*- coding: utf-8 -*-
"""에스컬레이션 규칙 모델, 크론 실행, 제약/권한 및 시드 데이터 테스트."""
from datetime import timedelta
import html
from unittest.mock import patch

from psycopg2 import IntegrityError

from odoo import fields
from odoo.exceptions import AccessError, ValidationError
from odoo.tests.common import TransactionCase
from odoo.tools import mute_logger

from ..utils.mock_email import build_mock_emails


class TestEscalationRules(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        Users = cls.env["res.users"].with_context(no_reset_password=True)
        grp_base = cls.env.ref("base.group_user")
        grp_user = cls.env.ref("it_helpdesk.group_helpdesk_user")
        grp_officer = cls.env.ref("it_helpdesk.group_helpdesk_officer")
        grp_manager = cls.env.ref("it_helpdesk.group_helpdesk_manager")

        cls.emp = Users.create({
            "name": "규칙사원",
            "login": "esc_emp@test.com",
            "email": "esc_emp@test.com",
            "groups_id": [(6, 0, [grp_base.id, grp_user.id])],
        })
        cls.off_a = Users.create({
            "name": "규칙담당A",
            "login": "esc_off_a@test.com",
            "email": "esc_off_a@test.com",
            "groups_id": [(6, 0, [grp_base.id, grp_user.id, grp_officer.id])],
        })
        cls.off_b = Users.create({
            "name": "규칙담당B",
            "login": "esc_off_b@test.com",
            "email": "esc_off_b@test.com",
            "groups_id": [(6, 0, [grp_base.id, grp_user.id, grp_officer.id])],
        })
        cls.mgr = Users.create({
            "name": "규칙관리자",
            "login": "esc_mgr@test.com",
            "email": "esc_mgr@test.com",
            "groups_id": [(6, 0, [grp_base.id, grp_user.id, grp_officer.id, grp_manager.id])],
        })
        cls.Ticket = cls.env["it.helpdesk.ticket"]
        cls.Rule = cls.env["it.helpdesk.escalation.rule"]
        cls.Log = cls.env["it.helpdesk.escalation.log"]
        cls.AssignRule = cls.env["it.helpdesk.assign.rule"]

        # 테스트 격리를 위해 기존 활성 에스컬레이션 규칙/배정 규칙 정리
        cls.Rule.with_context(active_test=False).search([]).write({"active": False})
        cls.AssignRule.with_context(active_test=False).search([]).unlink()
        cls.AssignRule.create({
            "category": "hw",
            "officer_ids": [(6, 0, [cls.off_a.id, cls.off_b.id])],
            "active": True,
        })

    def _make_ticket(self, category="hw", priority="3", status="assigned", assignee=None, deadline_delta=timedelta(hours=-5), title="에스컬레이션 테스트"):
        now = fields.Datetime.now()
        vals = {
            "title": title,
            "content": "<p>테스트 내용</p>",
            "category": category,
            "priority": priority,
            "status": status,
            "author_id": self.emp.id,
            "deadline": now + deadline_delta,
        }
        if assignee:
            vals["assignee_id"] = assignee.id
        if status in ("resolved", "closed", "canceled"):
            vals["resolution_note"] = "<p>조치 완료</p>"
        return self.Ticket.sudo().create(vals)

    def test_01_overdue_after_hours_filter(self):
        """overdue + after_hours=4 규칙은 기한 5시간 초과 건만 대상으로 하고 3시간 초과 건은 제외한다."""
        rule = self.Rule.create({
            "name": "4시간 초과 알림",
            "trigger": "overdue",
            "after_hours": 4,
            "action": "notify",
            "notify_user_ids": [(6, 0, [self.mgr.id])],
        })
        t_hit = self._make_ticket(deadline_delta=timedelta(hours=-5))
        t_miss = self._make_ticket(deadline_delta=timedelta(hours=-3))

        res = self.Rule._run_escalation_rules()
        self.assertGreaterEqual(res["executed"], 1)
        self.assertTrue(self.Log.search([("rule_id", "=", rule.id), ("ticket_id", "=", t_hit.id)]))
        self.assertFalse(self.Log.search([("rule_id", "=", rule.id), ("ticket_id", "=", t_miss.id)]))

    def test_02_idempotent_cron_and_unique_log_constraint(self):
        """같은 규칙으로 크론을 2회 실행해도 1회만 실행되며 활동/노트가 중복 생성되지 않는다."""
        rule = self.Rule.create({
            "name": "중복 방지 규칙",
            "trigger": "overdue",
            "after_hours": 1,
            "action": "notify",
            "notify_user_ids": [(6, 0, [self.mgr.id])],
        })
        t = self._make_ticket(deadline_delta=timedelta(hours=-2))

        self.Ticket._cron_sla_monitor()
        self.Ticket._cron_sla_monitor()
        logs = self.Log.search([("rule_id", "=", rule.id), ("ticket_id", "=", t.id)])
        self.assertEqual(len(logs), 1)
        rule_msgs = t.message_ids.filtered(lambda m: 'data-msg-type="escalation_rule"' in html.unescape(m.body or ""))
        self.assertEqual(len(rule_msgs), 1)
        activities = t.activity_ids.filtered(lambda a: a.user_id == self.mgr and "[에스컬레이션]" in (a.summary or ""))
        self.assertEqual(len(activities), 1)

        with mute_logger("odoo.sql_db"), self.assertRaises(IntegrityError):
            with self.env.cr.savepoint():
                self.Log.create({"rule_id": rule.id, "ticket_id": t.id, "result": "done"})

    def test_03_category_and_priority_min_filter(self):
        """category와 priority_min 조건을 모두 만족하는 티켓만 실행 대상이 된다."""
        rule = self.Rule.create({
            "name": "HW 높음 이상 규칙",
            "trigger": "overdue",
            "after_hours": 0,
            "category": "hw",
            "priority_min": "2",
            "action": "notify",
            "notify_user_ids": [(6, 0, [self.mgr.id])],
        })
        t_match_high = self._make_ticket(category="hw", priority="2", deadline_delta=timedelta(hours=-1))
        t_match_urgent = self._make_ticket(category="hw", priority="3", deadline_delta=timedelta(hours=-1))
        t_wrong_prio = self._make_ticket(category="hw", priority="1", deadline_delta=timedelta(hours=-1))
        t_wrong_cat = self._make_ticket(category="sw", priority="3", deadline_delta=timedelta(hours=-1))

        self.Rule._run_escalation_rules()
        self.assertTrue(self.Log.search([("rule_id", "=", rule.id), ("ticket_id", "=", t_match_high.id)]))
        self.assertTrue(self.Log.search([("rule_id", "=", rule.id), ("ticket_id", "=", t_match_urgent.id)]))
        self.assertFalse(self.Log.search([("rule_id", "=", rule.id), ("ticket_id", "=", t_wrong_prio.id)]))
        self.assertFalse(self.Log.search([("rule_id", "=", rule.id), ("ticket_id", "=", t_wrong_cat.id)]))

    def test_04_pending_and_closed_statuses_excluded(self):
        """pending(일시정지) 및 resolved/closed/canceled 티켓은 규칙 실행 대상에서 제외된다."""
        rule = self.Rule.create({
            "name": "종료·대기 제외 규칙",
            "trigger": "overdue",
            "after_hours": 0,
            "action": "notify",
            "notify_user_ids": [(6, 0, [self.mgr.id])],
        })
        excluded = [
            self._make_ticket(status=st, deadline_delta=timedelta(hours=-2))
            for st in ("pending", "resolved", "closed", "canceled")
        ]
        self.Rule._run_escalation_rules()
        for t in excluded:
            self.assertFalse(self.Log.search([("rule_id", "=", rule.id), ("ticket_id", "=", t.id)]))

    def test_05_inactive_rule_ignored(self):
        """비활성(active=False) 규칙은 실행되지 않는다."""
        rule = self.Rule.create({
            "name": "비활성 규칙",
            "active": False,
            "trigger": "overdue",
            "after_hours": 0,
            "action": "notify",
            "notify_user_ids": [(6, 0, [self.mgr.id])],
        })
        t = self._make_ticket(deadline_delta=timedelta(hours=-2))
        self.Rule._run_escalation_rules()
        self.assertFalse(self.Log.search([("rule_id", "=", rule.id), ("ticket_id", "=", t.id)]))

    def test_06_notify_activities_chatter_and_default_managers(self):
        """notify_user_ids 미지정 시 활성 관리자 전원에게 활동/노트 및 모의 이메일이 발송되고 사원은 볼 수 없다."""
        rule = self.Rule.create({
            "name": "관리자 전원 알림",
            "trigger": "overdue",
            "after_hours": 0,
            "action": "notify",
        })
        t = self._make_ticket(deadline_delta=timedelta(hours=-1))
        self.Rule._run_escalation_rules()

        mgr_group = self.env.ref("it_helpdesk.group_helpdesk_manager")
        active_mgrs = mgr_group.users.filtered(lambda u: u.active)
        for m in active_mgrs:
            self.assertTrue(t.activity_ids.filtered(lambda a: a.user_id == m))

        mgr_mails = build_mock_emails(t, self.mgr, is_officer=True)
        self.assertTrue(any(m["event_type"] == "escalation_rule" for m in mgr_mails))
        emp_mails = build_mock_emails(t, self.emp, is_officer=False)
        self.assertFalse(any(m["event_type"] == "escalation_rule" for m in emp_mails))

    def test_07_reassign_auto_designated_absent_and_constraints(self):
        """자동/지정 재배정(현재 담당자 제외), 부재 대상 건너뜀, 제약 검증을 확인한다."""
        with self.assertRaises(ValidationError):
            self.Rule.create({"name": "잘못된 재배정", "trigger": "imminent", "action": "reassign"})
        with self.assertRaises(ValidationError):
            self.Rule.create({"name": "음수 시간", "trigger": "overdue", "after_hours": -1, "action": "notify"})
        with self.assertRaises(ValidationError):
            self.Rule.create({
                "name": "사원 수신 불가",
                "trigger": "overdue",
                "action": "notify",
                "notify_user_ids": [(6, 0, [self.emp.id])],
            })

        # 자동 선택: 현재 담당자가 off_a이면 제외하고 off_b로 재배정
        rule_auto = self.Rule.create({
            "name": "자동 재배정",
            "sequence": 10,
            "trigger": "overdue",
            "after_hours": 2,
            "action": "reassign",
        })
        t_auto = self._make_ticket(category="hw", assignee=self.off_a, deadline_delta=timedelta(hours=-3))
        self.Rule._run_escalation_rules()
        t_auto.invalidate_recordset()
        self.assertEqual(t_auto.assignee_id, self.off_b)
        log_auto = self.Log.search([("rule_id", "=", rule_auto.id), ("ticket_id", "=", t_auto.id)])
        self.assertEqual(log_auto.result, "done")
        chatter = " ".join(html.unescape(m.body or "") for m in t_auto.message_ids)
        self.assertIn("[담당자 변경]", chatter)
        self.assertIn("에스컬레이션 규칙 '자동 재배정'", chatter)

        # 지정 대상이 부재 중이면 건너뛰고 skipped 로그 남김
        rule_auto.active = False
        self.off_b.write({"helpdesk_absent": True, "helpdesk_absent_until": False})
        rule_target = self.Rule.create({
            "name": "부재 대상 재배정",
            "sequence": 20,
            "trigger": "overdue",
            "after_hours": 1,
            "action": "reassign",
            "target_user_id": self.off_b.id,
        })
        t_skip = self._make_ticket(category="hw", assignee=self.off_a, deadline_delta=timedelta(hours=-3))
        self.Rule._run_escalation_rules()
        t_skip.invalidate_recordset()
        self.assertEqual(t_skip.assignee_id, self.off_a)
        log_skip = self.Log.search([("rule_id", "=", rule_target.id), ("ticket_id", "=", t_skip.id)])
        self.assertEqual(log_skip.result, "skipped")

    def test_08_imminent_trigger(self):
        """imminent 트리거 규칙은 마감 임박 상태 티켓만 대상으로 실행한다."""
        rule = self.Rule.create({
            "name": "마감 임박 알림",
            "trigger": "imminent",
            "action": "notify",
            "notify_user_ids": [(6, 0, [self.off_a.id])],
        })
        t_imminent = self._make_ticket(priority="3", deadline_delta=timedelta(minutes=30))
        t_ok = self._make_ticket(priority="3", deadline_delta=timedelta(hours=3))
        t_overdue = self._make_ticket(priority="3", deadline_delta=timedelta(minutes=-10))

        self.Rule._run_escalation_rules()
        self.assertTrue(self.Log.search([("rule_id", "=", rule.id), ("ticket_id", "=", t_imminent.id)]))
        self.assertFalse(self.Log.search([("rule_id", "=", rule.id), ("ticket_id", "=", t_ok.id)]))
        self.assertFalse(self.Log.search([("rule_id", "=", rule.id), ("ticket_id", "=", t_overdue.id)]))

    def test_09_exception_on_one_ticket_does_not_block_others(self):
        """한 티켓 처리 중 예외가 발생해도 savepoint로 격리되어 나머지 티켓은 정상 처리된다."""
        rule = self.Rule.create({
            "name": "예외 격리 테스트",
            "trigger": "overdue",
            "after_hours": 1,
            "action": "notify",
            "notify_user_ids": [(6, 0, [self.mgr.id])],
        })
        t_bad = self._make_ticket(deadline_delta=timedelta(hours=-3), title="예외 티켓")
        t_good = self._make_ticket(deadline_delta=timedelta(hours=-2), title="정상 티켓")

        orig_exec = type(rule)._execute_on_ticket

        def flaky_exec(rec, ticket, root_partner_id):
            if ticket.id == t_bad.id:
                raise RuntimeError("강제 예외")
            return orig_exec(rec, ticket, root_partner_id)

        with mute_logger("odoo.addons.it_helpdesk.models.escalation_rule"):
            with patch.object(type(rule), "_execute_on_ticket", autospec=True, side_effect=flaky_exec):
                res = self.Rule._run_escalation_rules()

        # 라이브 DB의 다른 기한 초과 티켓에도 규칙이 실행될 수 있으므로 건수 대신 티켓별 로그로 검증한다.
        self.assertGreaterEqual(res["executed"], 1)
        self.assertFalse(self.Log.search([("rule_id", "=", rule.id), ("ticket_id", "=", t_bad.id)]))
        self.assertTrue(self.Log.search([("rule_id", "=", rule.id), ("ticket_id", "=", t_good.id)]))

    def test_10_cron_sla_monitor_returns_rules_and_keeps_keys(self):
        """_cron_sla_monitor 반환값은 warned/escalated 키를 유지하고 rules 건수를 포함한다."""
        self.Rule.create({
            "name": "크론 통합 알림",
            "trigger": "overdue",
            "after_hours": 1,
            "action": "notify",
            "notify_user_ids": [(6, 0, [self.mgr.id])],
        })
        self._make_ticket(deadline_delta=timedelta(hours=-2))
        res = self.Ticket._cron_sla_monitor()
        self.assertIn("warned", res)
        self.assertIn("escalated", res)
        self.assertIn("rules", res)
        self.assertGreaterEqual(res["rules"]["executed"], 1)

    def test_11_seed_rules_exist_and_inactive(self):
        """기본 시드 규칙 2건은 존재하며 기본 비활성(active=False)이다."""
        r1 = self.env.ref("it_helpdesk.escalation_rule_urgent_overdue_notify")
        r2 = self.env.ref("it_helpdesk.escalation_rule_overdue_24h_reassign")
        self.assertFalse(r1.active)
        self.assertFalse(r2.active)
        self.assertEqual(r1.action, "notify")
        self.assertEqual(r2.action, "reassign")

    def test_12_employee_cannot_access_rules_or_logs(self):
        """일반 사원은 에스컬레이션 규칙 및 실행 이력 모델에 접근할 수 없다."""
        with self.assertRaises(AccessError):
            self.Rule.with_user(self.emp).search([])
        with self.assertRaises(AccessError):
            self.Log.with_user(self.emp).search([])
