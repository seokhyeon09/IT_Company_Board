# -*- coding: utf-8 -*-
"""중복 문의 병합, 후보 추천, 보안 격리 및 SLA 통계 제외 테스트."""
from datetime import timedelta
import hmac
import hashlib
import html
import json
import time
from unittest.mock import MagicMock, patch

from odoo import fields
from odoo.exceptions import AccessError, UserError
from odoo.tests.common import TransactionCase

from ..controllers.ticket_merge_api import TicketMergeAPIController
from ..controllers.ticket_query_api import TicketQueryAPIController
from ..utils.security import GATEWAY_SHARED_SECRET
from ..utils.sla_report import build_sla_report
from ..utils.ticket_merge import find_merge_candidates, merge_tickets
from ..utils.ticket_serializer import serialize_ticket_detail, serialize_ticket_summary


class TestTicketMerge(TransactionCase):

    @classmethod
    def _make_user(cls, login, groups):
        return cls.env["res.users"].with_context(no_reset_password=True).create({
            "name": login,
            "login": login,
            "email": f"{login}@test.com",
            "groups_id": [(6, 0, [g.id for g in groups])],
        })

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        g_base = cls.env.ref("base.group_user")
        g_user = cls.env.ref("it_helpdesk.group_helpdesk_user")
        g_officer = cls.env.ref("it_helpdesk.group_helpdesk_officer")

        cls.emp_a = cls._make_user("merge_emp_a", [g_base, g_user])
        cls.emp_b = cls._make_user("merge_emp_b", [g_base, g_user])
        cls.officer = cls._make_user("merge_officer", [g_base, g_user, g_officer])
        cls.Ticket = cls.env["it.helpdesk.ticket"]
        cls.merge_ctrl = TicketMergeAPIController()
        cls.query_ctrl = TicketQueryAPIController()

    def _create_ticket(self, author, title, category="sw", status="submitted", deadline_delta=None):
        vals = {
            "title": title,
            "content": "<p>상세 테스트 내용입니다.</p>",
            "category": category,
            "priority": "1",
        }
        t = self.Ticket.with_user(author).create(vals)
        write_vals = {}
        if status != "submitted":
            write_vals["status"] = status
        if status in ("resolved", "closed"):
            write_vals["resolution_note"] = "<p>기존 해결 내용</p>"
        if deadline_delta is not None:
            write_vals["deadline"] = fields.Datetime.now() + deadline_delta
        if write_vals:
            t.sudo().write(write_vals)
        return t

    def _mock_request(self, user, path):
        ts = str(int(time.time()))
        uid_str = str(user.id)
        body_hash = hashlib.sha256(b"").hexdigest()
        payload = f"POST:{path}:{uid_str}:{ts}:{body_hash}".encode("utf-8")
        sig = hmac.new(GATEWAY_SHARED_SECRET.encode("utf-8"), payload, hashlib.sha256).hexdigest()

        mock_req = MagicMock()
        mock_req.httprequest.headers = {
            "X-Gateway-User-Id": uid_str,
            "X-Gateway-Timestamp": ts,
            "X-Gateway-Signature": sig,
        }
        mock_req.httprequest.method = "POST"
        mock_req.httprequest.path = path
        mock_req.httprequest.get_data.return_value = b""
        mock_req.env = self.env
        mock_req.session.uid = None
        return mock_req

    def test_01_merge_validation_errors(self):
        """중복 병합 6종 검증 오류 메시지가 한글 UserError로 반환된다."""
        t1 = self._create_ticket(self.emp_a, "VPN 접속 오류")
        t2 = self._create_ticket(self.emp_b, "VPN 인증 실패")
        t_resolved = self._create_ticket(self.emp_a, "해결 완료 건", status="resolved")
        t_canceled = self._create_ticket(self.emp_a, "취소 건", status="canceled")

        # 1. 자기 자신
        with self.assertRaisesRegex(UserError, "같은 문의에는 병합할 수 없습니다."):
            merge_tickets(self.officer, t1, t1)

        # 2. 처리 불가 상태 source
        with self.assertRaisesRegex(UserError, "처리 중인 문의만 병합할 수 있습니다."):
            merge_tickets(self.officer, t_resolved, t2)

        # 3. 취소된 target
        with self.assertRaisesRegex(UserError, "취소된 문의에는 병합할 수 없습니다."):
            merge_tickets(self.officer, t1, t_canceled)

        # 4. 사유 500자 초과
        with self.assertRaisesRegex(UserError, "병합 사유는 최대 500자까지 입력할 수 있습니다."):
            merge_tickets(self.officer, t1, t2, reason="가" * 501)

        # 정상 병합: t1 -> t2
        merge_tickets(self.officer, t1, t2, reason="")

        # 5. 이미 병합된 source 재병합
        t3 = self._create_ticket(self.emp_a, "또 다른 VPN 문의")
        with self.assertRaisesRegex(UserError, "이미 다른 문의에 병합된 문의입니다."):
            merge_tickets(self.officer, t1, t3)

        # 6. 이미 병합된 문을 target으로 (체인 및 순환 금지)
        with self.assertRaisesRegex(UserError, "이미 병합된 문의에는 병합할 수 없습니다."):
            merge_tickets(self.officer, t3, t1)
        # 순환 케이스: t2를 자기 하위(t1)로 병합 시도해도 체인 규칙으로 차단
        with self.assertRaisesRegex(UserError, "이미 병합된 문의에는 병합할 수 없습니다."):
            merge_tickets(self.officer, t2, t1)

    def test_02_merge_effects_no_leak_and_privacy(self):
        """정상 병합 효과, 내부 노트 사원 비노출, 원본 작성자에 대상 제목/내용 비노출을 검증한다."""
        src = self._create_ticket(self.emp_a, "비밀제목XYZ 사내 메신저 로그인 실패", status="pending")
        tgt = self._create_ticket(self.emp_b, "타사원 비밀제목ABC 메신저 서버 장애", status="in_progress")
        mail_before = self.env["mail.mail"].sudo().search_count([])

        with patch("odoo.addons.it_helpdesk.controllers.main_api.request",
                   self._mock_request(self.officer, "/api/v1/tickets/merge")):
            res = self.merge_ctrl.merge_ticket(ticket_id=src.id, target_id=tgt.id, reason="동일 서버 장애")

        self.assertEqual(res["status"], "success")
        self.assertEqual(res["data"]["status"], "canceled")
        self.assertEqual(res["data"]["merged_into_id"], tgt.id)
        self.assertEqual(res["data"]["merged_into_number"], tgt.ticket_number)

        src.invalidate_recordset()
        tgt.invalidate_recordset()
        self.assertEqual(src.status, "canceled")
        self.assertFalse(src.sla_paused_at)
        self.assertEqual(src.merged_into_id, tgt)
        self.assertIn(tgt.ticket_number, str(src.resolution_note))
        self.assertIn("동일 서버 장애", str(src.resolution_note))
        self.assertEqual(mail_before, self.env["mail.mail"].sudo().search_count([]))

        # target 작성자(사원B) 상세 응답에 내부 병합 노트가 절대 노출되지 않아야 함
        tgt_emp_detail = serialize_ticket_detail(tgt, self.emp_b, self.env)
        self.assertEqual(tgt_emp_detail["internal_notes"], [])
        self.assertEqual(tgt_emp_detail["merged_tickets"], [])
        self.assertNotIn("중복 병합", json.dumps(tgt_emp_detail, ensure_ascii=False))
        self.assertNotIn("비밀제목XYZ", json.dumps(tgt_emp_detail, ensure_ascii=False))

        # 담당자 상세 응답에는 merged_tickets와 내부 노트가 모두 포함됨
        tgt_off_detail = serialize_ticket_detail(tgt, self.officer, self.env)
        self.assertEqual(len(tgt_off_detail["merged_tickets"]), 1)
        self.assertEqual(tgt_off_detail["merged_tickets"][0]["ticket_number"], src.ticket_number)
        self.assertTrue(any("[중복 병합]" in n["content"] for n in tgt_off_detail["internal_notes"]))

        # 원본 작성자(사원A) 요약/상세에는 merged_into_number만 있고 타깃 제목/내용은 없음
        src_summary = serialize_ticket_summary(src)
        self.assertEqual(src_summary["merged_into_number"], tgt.ticket_number)
        src_emp_detail = serialize_ticket_detail(src, self.emp_a, self.env)
        self.assertEqual(src_emp_detail["merged_into_id"], tgt.id)
        self.assertEqual(src_emp_detail["merged_into_number"], tgt.ticket_number)
        self.assertNotIn("타사원 비밀제목ABC", json.dumps(src_emp_detail, ensure_ascii=False))

        # list_tickets API에서도 사원A가 AccessError 없이 merged_into_number를 수신
        with patch("odoo.addons.it_helpdesk.controllers.main_api.request",
                   self._mock_request(self.emp_a, "/api/v1/tickets/list")):
            list_res = self.query_ctrl.list_tickets(limit=50)
        matched = [row for row in list_res["data"] if row["id"] == src.id]
        self.assertEqual(len(matched), 1)
        self.assertEqual(matched[0]["merged_into_number"], tgt.ticket_number)

    def test_03_employee_forbidden_on_merge_apis(self):
        """사원이 병합 또는 후보 조회 API를 호출하면 AccessError가 발생한다."""
        t1 = self._create_ticket(self.emp_a, "사원 테스트 1")
        t2 = self._create_ticket(self.emp_a, "사원 테스트 2")

        with patch("odoo.addons.it_helpdesk.controllers.main_api.request",
                   self._mock_request(self.emp_a, "/api/v1/tickets/merge")):
            with self.assertRaises(AccessError):
                self.merge_ctrl.merge_ticket(ticket_id=t1.id, target_id=t2.id)

        with patch("odoo.addons.it_helpdesk.controllers.main_api.request",
                   self._mock_request(self.emp_a, "/api/v1/tickets/merge-candidates")):
            with self.assertRaises(AccessError):
                self.merge_ctrl.get_merge_candidates(ticket_id=t1.id)

    def test_04_candidate_recommendations_scoring_and_filters(self):
        """후보 추천은 같은 분야/최근 30일/자카드 유사도>=0.2/정렬/제외조건/limit을 지킨다."""
        src = self._create_ticket(self.emp_a, "사내 와이파이 인증서 접속 오류", category="network")
        best = self._create_ticket(self.emp_b, "사내 와이파이 인증서 접속 오류 발생", category="network")
        mid = self._create_ticket(self.emp_b, "사내 와이파이 로그인 불가", category="network")
        low = self._create_ticket(self.emp_b, "프린터 토너 교체 요청", category="network")
        diff_cat = self._create_ticket(self.emp_b, "사내 와이파이 인증서 접속 오류", category="sw")
        canceled = self._create_ticket(self.emp_b, "사내 와이파이 인증서 접속 오류", category="network", status="canceled")
        merged_cand = self._create_ticket(self.emp_b, "사내 와이파이 인증서 접속 오류", category="network")
        merged_cand.sudo().write({"merged_into_id": best.id})

        old = self._create_ticket(self.emp_b, "사내 와이파이 인증서 접속 오류", category="network")
        old_dt = fields.Datetime.to_string(fields.Datetime.now() - timedelta(days=31))
        self.env.cr.execute("UPDATE it_helpdesk_ticket SET create_date = %s WHERE id = %s", (old_dt, old.id))
        old.invalidate_recordset()

        cands = find_merge_candidates(self.officer, src, limit=2)
        cand_ids = [c["id"] for c in cands]
        self.assertEqual(cand_ids, [best.id, mid.id])
        self.assertGreater(cands[0]["score"], cands[1]["score"])
        for excluded_id in (src.id, low.id, diff_cat.id, canceled.id, merged_cand.id, old.id):
            self.assertNotIn(excluded_id, cand_ids)

        # 병합 불가 상태 티켓은 빈 목록
        src_done = self._create_ticket(self.emp_a, "사내 와이파이 인증서 접속 오류", category="network", status="resolved")
        self.assertEqual(find_merge_candidates(self.officer, src_done), [])

    def test_05_merged_ticket_excluded_from_sla_report_and_overdue(self):
        """병합된 문의는 기한이 지나도 overdue 필터와 SLA 리포트 해결/미처리 집계에서 제외된다."""
        src = self._create_ticket(
            self.emp_a,
            "병합 SLA 제외 테스트 원본",
            category="etc",
            status="in_progress",
            deadline_delta=timedelta(hours=-3),
        )
        tgt = self._create_ticket(self.emp_b, "병합 SLA 제외 테스트 대상", category="etc", status="in_progress")

        today_str = fields.Date.to_string(fields.Date.today())
        before_report = build_sla_report(
            self.env, self.officer, date_from=today_str, date_to=today_str, category="etc"
        )
        self.assertTrue(src.is_overdue)

        merge_tickets(self.officer, src, tgt, reason="중복 정리")
        src.invalidate_recordset()

        self.assertFalse(src.is_overdue)
        self.assertNotIn(src.id, self.Ticket.search([("is_overdue", "=", True)]).ids)
        after_report = build_sla_report(
            self.env, self.officer, date_from=today_str, date_to=today_str, category="etc"
        )
        self.assertEqual(after_report["summary"]["resolved"], before_report["summary"]["resolved"])
        self.assertEqual(after_report["summary"]["open_now"], before_report["summary"]["open_now"] - 1)
        self.assertEqual(after_report["summary"]["overdue_now"], before_report["summary"]["overdue_now"] - 1)
