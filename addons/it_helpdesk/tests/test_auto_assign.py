# -*- coding: utf-8 -*-
from unittest.mock import patch

from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError

from ..utils.auto_assign import (
    AUTO_ASSIGN_PARAM,
    create_ticket_with_auto_assign,
    try_auto_assign,
)
from ..utils.mock_email import build_mock_emails

PICK_PATH = 'odoo.addons.it_helpdesk.utils.auto_assign.pick_officer'


class TestAutoAssign(TransactionCase):

    @classmethod
    def _make_user(cls, login, groups):
        return cls.env['res.users'].create({
            'name': login,
            'login': login,
            'email': f'{login}@audit.com',
            'groups_id': [(6, 0, [g.id for g in groups])],
        })

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Ticket = cls.env['it.helpdesk.ticket']
        cls.Rule = cls.env['it.helpdesk.assign.rule']
        g_user = cls.env.ref('it_helpdesk.group_helpdesk_user')
        g_officer = cls.env.ref('it_helpdesk.group_helpdesk_officer')
        cls.employee = cls._make_user('aa_employee', [g_user])
        cls.off_a = cls._make_user('aa_officer_a', [g_user, g_officer])
        cls.off_b = cls._make_user('aa_officer_b', [g_user, g_officer])
        cls.Rule.with_context(active_test=False).search([]).unlink()
        cls.env['ir.config_parameter'].sudo().set_param(AUTO_ASSIGN_PARAM, 'True')

    def _rule(self, category, officers, active=True):
        return self.Rule.create({
            'category': category,
            'officer_ids': [(6, 0, [u.id for u in officers])],
            'active': active,
        })

    def _new_ticket(self, category='hw'):
        return create_ticket_with_auto_assign(
            self.Ticket.with_user(self.employee),
            {'title': '자동 배정 테스트', 'content': '<p>본문</p>', 'category': category},
        )

    def _load(self, officer, status, count=1):
        for _ in range(count):
            self.Ticket.create({
                'title': '부하 티켓', 'content': '<p>본문</p>', 'category': 'etc',
                'assignee_id': officer.id, 'status': status,
            })

    def test_01_switch_off_keeps_submitted(self):
        self.env['ir.config_parameter'].sudo().set_param(AUTO_ASSIGN_PARAM, 'False')
        self._rule('hw', [self.off_a])
        ticket = self._new_ticket('hw')
        self.assertEqual(ticket.status, 'submitted')
        self.assertFalse(ticket.assignee_id)

    def test_02_no_rule_keeps_submitted(self):
        ticket = self._new_ticket('hw')
        self.assertEqual(ticket.status, 'submitted')
        self.assertFalse(ticket.assignee_id)

    def test_03_single_officer_rule_assigns(self):
        self._rule('hw', [self.off_a])
        ticket = self._new_ticket('hw')
        self.assertEqual(ticket.status, 'assigned')
        self.assertEqual(ticket.assignee_id, self.off_a)
        notes = ticket.sudo().message_ids.filtered(
            lambda m: 'data-msg-type="auto_assign"' in (m.body or '')
        )
        self.assertEqual(len(notes), 1)

    def test_04_least_load_sequence(self):
        self._rule('network', [self.off_a, self.off_b])
        self._load(self.off_a, 'in_progress', count=2)
        picked = [self._new_ticket('network').assignee_id for _ in range(4)]
        self.assertEqual(picked, [self.off_b, self.off_b, self.off_a, self.off_b])

    def test_05_tie_picks_lowest_user_id(self):
        self._rule('sw', [self.off_a, self.off_b])
        ticket = self._new_ticket('sw')
        self.assertEqual(ticket.assignee_id, self.off_a)
        self.assertLess(self.off_a.id, self.off_b.id)

    def test_06_finished_tickets_not_counted(self):
        self._rule('account', [self.off_a, self.off_b])
        for status in ('resolved', 'closed', 'canceled'):
            self._load(self.off_a, status)
        self._load(self.off_b, 'in_progress')
        ticket = self._new_ticket('account')
        self.assertEqual(ticket.assignee_id, self.off_a)

    def test_07_inactive_officer_excluded(self):
        self._rule('hw', [self.off_a, self.off_b])
        self.off_a.active = False
        self.assertEqual(self._new_ticket('hw').assignee_id, self.off_b)
        self.off_b.active = False
        ticket = self._new_ticket('hw')
        self.assertEqual(ticket.status, 'submitted')
        self.assertFalse(ticket.assignee_id)

    def test_08_rule_constraints(self):
        with self.assertRaises(ValidationError):
            self._rule('hw', [self.employee])
        self._rule('sw', [self.off_a])
        with self.assertRaises(ValidationError):
            self._rule('sw', [self.off_b])
        self._rule('sw', [self.off_b], active=False)

    def test_09_failure_does_not_break_creation(self):
        with patch(PICK_PATH, side_effect=Exception('boom')):
            ticket = self._new_ticket('hw')
        self.assertTrue(ticket.exists())
        self.assertEqual(ticket.status, 'submitted')
        self.assertFalse(ticket.assignee_id)

    def test_10_mock_emails_for_auto_assign(self):
        self._rule('hw', [self.off_a])
        ticket = self._new_ticket('hw').sudo()
        author_mails = build_mock_emails(ticket, self.employee, False)
        self.assertTrue(any(m['event_type'] == 'assigned' for m in author_mails))
        officer_mails = build_mock_emails(ticket, self.off_a, True)
        self.assertTrue(any(m['event_type'] == 'assigned' for m in officer_mails))
        self.assertFalse(any(m['event_type'] == 'new_ticket' for m in officer_mails))

    def test_11_category_values_match_ticket(self):
        ticket_keys = list(dict(self.Ticket._fields['category'].selection).keys())
        rule_keys = list(dict(self.Rule._fields['category'].selection).keys())
        self.assertEqual(ticket_keys, rule_keys)

    def test_12_already_assigned_ticket_untouched(self):
        self._rule('hw', [self.off_a])
        ticket = self.Ticket.create({
            'title': '이미 배정', 'content': '<p>본문</p>', 'category': 'hw',
            'assignee_id': self.off_b.id, 'status': 'assigned',
        })
        self.assertFalse(try_auto_assign(ticket))
        self.assertEqual(ticket.assignee_id, self.off_b)
