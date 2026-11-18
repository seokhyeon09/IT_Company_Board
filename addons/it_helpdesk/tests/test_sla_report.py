# -*- coding: utf-8 -*-
import hashlib
import hmac
import time
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

from odoo.exceptions import AccessError, UserError
from odoo.tests.common import TransactionCase

from ..controllers.report_api import ReportAPIController
from ..utils.security import GATEWAY_SHARED_SECRET
from ..utils.stats_calculator import compute_officer_stats_payload


class TestSlaReport(TransactionCase):

    @classmethod
    def _make_user(cls, login, groups):
        return cls.env['res.users'].with_context(no_reset_password=True).create({
            'name': login,
            'login': login,
            'email': f'{login}@test.com',
            'groups_id': [(6, 0, [g.id for g in groups])],
        })

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Ticket = cls.env['it.helpdesk.ticket']
        cls.ctrl = ReportAPIController()
        g_base = cls.env.ref('base.group_user')
        g_user = cls.env.ref('it_helpdesk.group_helpdesk_user')
        g_officer = cls.env.ref('it_helpdesk.group_helpdesk_officer')

        cls.emp = cls._make_user('sla_rep_emp', [g_base, g_user])
        cls.officer = cls._make_user('sla_rep_off', [g_base, g_user, g_officer])

    def _mock_request(self, user, path='/api/v1/reports/sla'):
        ts = str(int(time.time()))
        uid_str = str(user.id)
        body_hash = hashlib.sha256(b'').hexdigest()
        payload = f"POST:{path}:{uid_str}:{ts}:{body_hash}".encode('utf-8')
        sig = hmac.new(GATEWAY_SHARED_SECRET.encode('utf-8'), payload, hashlib.sha256).hexdigest()
        mock_req = MagicMock()
        mock_req.httprequest.headers = {
            'X-Gateway-User-Id': uid_str,
            'X-Gateway-Timestamp': ts,
            'X-Gateway-Signature': sig,
        }
        mock_req.httprequest.method = 'POST'
        mock_req.httprequest.path = path
        mock_req.httprequest.get_data.return_value = b''
        mock_req.env = self.env
        mock_req.session.uid = None
        return mock_req

    def _call_report(self, user=None, **params):
        target = user or self.officer
        with patch('odoo.addons.it_helpdesk.controllers.main_api.request', self._mock_request(target)):
            return self.ctrl.get_sla_report(**params)

    def _create_ticket_at(self, create_utc, category='hw', priority='1', status='submitted',
                          resolved_utc=None, on_time=None, paused_sec=0, deadline_utc=None, assignee=None):
        vals = {
            'title': f'SLA리포트_{category}_{priority}',
            'content': '<p>내용</p>',
            'category': category,
            'priority': priority,
            'author_id': self.emp.id,
        }
        if assignee:
            vals['assignee_id'] = assignee.id
        t = self.Ticket.sudo().create(vals)
        self.env.cr.execute(
            "UPDATE it_helpdesk_ticket SET create_date = %s WHERE id = %s",
            (create_utc, t.id),
        )
        self.env.invalidate_all()
        write_vals = {'status': status}
        if paused_sec:
            write_vals['sla_paused_seconds'] = paused_sec
        if deadline_utc:
            write_vals['deadline'] = deadline_utc
        if resolved_utc:
            write_vals['resolution_note'] = '<p>조치완료</p>'
            write_vals['first_resolved_date'] = resolved_utc
            write_vals['first_resolved_on_time'] = bool(on_time)
        t.sudo().write(write_vals)
        return t

    def test_01_week_buckets_and_zero_fill(self):
        """(1) 주 단위 버킷 개수와 빈 버킷 0/None 채움을 검증한다."""
        res = self._call_report(date_from='2024-01-01', date_to='2024-01-21', unit='week')
        series = res['data']['series']
        self.assertEqual([s['period'] for s in series], ['2024-01-01', '2024-01-08', '2024-01-15'])
        for row in series:
            self.assertEqual(row['created'], 0)
            self.assertEqual(row['resolved'], 0)
            self.assertIsNone(row['on_time_rate'])
            self.assertIsNone(row['avg_resolution_hours'])

    def test_02_03_counts_rates_and_avg_hours(self):
        """(2)(3) 접수/해결/기한내/지연 집계, 준수율(해결 0건시 None), 평균 해결시간을 검증한다."""
        # 2024-02-05 (월) KST = 2024-02-04 15:00 UTC 이후
        self._create_ticket_at('2024-02-05 01:00:00', category='hw', priority='2', status='resolved',
                               resolved_utc='2024-02-05 03:00:00', on_time=True)
        self._create_ticket_at('2024-02-05 02:00:00', category='sw', priority='3', status='closed',
                               resolved_utc='2024-02-05 06:00:00', on_time=False)
        self._create_ticket_at('2024-02-12 01:00:00', category='hw', priority='0', status='canceled')

        res = self._call_report(date_from='2024-02-05', date_to='2024-02-18', unit='week')
        data = res['data']
        self.assertEqual(data['summary']['created'], 3)
        self.assertEqual(data['summary']['resolved'], 2)
        self.assertEqual(data['summary']['on_time'], 1)
        self.assertEqual(data['summary']['breached'], 1)
        self.assertEqual(data['summary']['on_time_rate'], 50.0)
        self.assertEqual(data['summary']['avg_resolution_hours'], 3.0)

        w1, w2 = data['series']
        self.assertEqual((w1['created'], w1['resolved'], w1['on_time_rate'], w1['avg_resolution_hours']), (2, 2, 50.0, 3.0))
        self.assertEqual((w2['created'], w2['resolved']), (1, 0))
        self.assertIsNone(w2['on_time_rate'])
        self.assertIsNone(w2['avg_resolution_hours'])

    def test_04_10_category_filter_and_full_dimensions(self):
        """(4)(10) 분야 필터 적용 및 by_category 5개/by_priority 4개 전체 포함을 검증한다."""
        self._create_ticket_at('2024-03-04 01:00:00', category='hw', priority='1', status='resolved',
                               resolved_utc='2024-03-04 02:00:00', on_time=True)
        self._create_ticket_at('2024-03-04 02:00:00', category='network', priority='3', status='submitted')

        res_hw = self._call_report(date_from='2024-03-04', date_to='2024-03-10', unit='week', category='hw')
        data_hw = res_hw['data']
        self.assertEqual(data_hw['summary']['created'], 1)
        self.assertEqual(data_hw['summary']['resolved'], 1)
        self.assertEqual(len(data_hw['by_category']), 5)
        self.assertEqual(len(data_hw['by_priority']), 4)
        net_row = next(c for c in data_hw['by_category'] if c['category'] == 'network')
        self.assertEqual(net_row['created'], 0)

    def test_05_kst_week_boundary(self):
        """(5) UTC 2026-11-15 16:00(=KST 2026-11-16 01:00 월요일) 접수 티켓이 2026-11-16 주에 포함된다."""
        before = self._call_report(date_from='2026-11-09', date_to='2026-11-22', unit='week')['data']['series']
        before_map = {s['period']: s['created'] for s in before}

        self._create_ticket_at('2026-11-15 16:00:00', category='etc', priority='0', status='submitted')

        after = self._call_report(date_from='2026-11-09', date_to='2026-11-22', unit='week')['data']['series']
        after_map = {s['period']: s['created'] for s in after}
        self.assertEqual(after_map['2026-11-09'], before_map['2026-11-09'])
        self.assertEqual(after_map['2026-11-16'], before_map['2026-11-16'] + 1)

    def test_06_month_unit(self):
        """(6) 월 단위 집계 버킷과 KST 경계를 검증한다."""
        self._create_ticket_at('2024-04-30 16:00:00', category='account', priority='1', status='submitted')  # KST 05-01 01:00
        res = self._call_report(date_from='2024-04-01', date_to='2024-05-31', unit='month')
        series = {s['period']: s['created'] for s in res['data']['series']}
        self.assertEqual(list(series.keys()), ['2024-04-01', '2024-05-01'])
        self.assertEqual(series['2024-04-01'], 0)
        self.assertEqual(series['2024-05-01'], 1)

    def test_07_08_validation_errors_and_employee_forbidden(self):
        """(7)(8) 검증 오류 5종 한글 메시지 및 사원 AccessError를 검증한다."""
        with self.assertRaises(AccessError):
            self._call_report(user=self.emp)

        bad_cases = [
            ({'date_from': '2026/11/01', 'date_to': '2026-11-10'}, '날짜 형식이 올바르지 않습니다. (YYYY-MM-DD)'),
            ({'date_from': '2026-11-10', 'date_to': '2026-11-01'}, '시작일이 종료일보다 늦을 수 없습니다.'),
            ({'date_from': '2025-01-01', 'date_to': '2026-01-02'}, '조회 기간은 최대 366일입니다.'),
            ({'date_from': '2026-11-01', 'date_to': '2026-11-10', 'unit': 'day'}, '집계 단위는 week 또는 month여야 합니다.'),
            ({'date_from': '2026-11-01', 'date_to': '2026-11-10', 'category': 'bad'}, '유효하지 않은 분야입니다.'),
        ]
        for kwargs, msg in bad_cases:
            with self.assertRaises(UserError) as ctx:
                self._call_report(**kwargs)
            self.assertIn(msg, str(ctx.exception))

    def test_09_now_counts_and_avg_paused_hours(self):
        """(9) 현재 시점 상태 건수(open/overdue/paused)와 평균 일시정지 시간을 검증한다."""
        before = self._call_report(date_from='2024-06-01', date_to='2024-06-30', unit='month')['data']['summary']
        past_dl = (datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(hours=2)).strftime('%Y-%m-%d %H:%M:%S')

        self._create_ticket_at('2024-06-05 01:00:00', category='hw', status='in_progress',
                               deadline_utc=past_dl, paused_sec=3600)
        self._create_ticket_at('2024-06-06 01:00:00', category='hw', status='pending',
                               deadline_utc=past_dl, paused_sec=7200)

        after = self._call_report(date_from='2024-06-01', date_to='2024-06-30', unit='month')['data']['summary']
        self.assertEqual(after['open_now'], before['open_now'] + 2)
        self.assertEqual(after['overdue_now'], before['overdue_now'] + 1)
        self.assertEqual(after['paused_now'], before['paused_now'] + 1)
        self.assertEqual(after['avg_paused_hours'], 1.5)

    def test_11_stats_calculator_uses_first_resolved_on_time(self):
        """(11) stats_calculator의 sla_compliance_rate가 지연 해결 건을 미준수로 반영한다."""
        self._create_ticket_at('2024-07-01 01:00:00', status='resolved',
                               resolved_utc='2024-07-01 02:00:00', on_time=True, assignee=self.officer)
        self._create_ticket_at('2024-07-01 01:00:00', status='resolved',
                               resolved_utc='2024-07-05 02:00:00', on_time=False, assignee=self.officer)

        stats = compute_officer_stats_payload(self.env, self.officer)
        my_row = next(o for o in stats['officers'] if o['officer_id'] == self.officer.id)
        self.assertEqual(my_row['sla_compliance_rate'], 50.0)
        self.assertLess(stats['overall_sla_rate'], 100.0)
