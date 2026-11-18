# -*- coding: utf-8 -*-
from odoo import api, SUPERUSER_ID
from odoo.addons.it_helpdesk.utils.sla_backfill import backfill_sla_fields


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    backfill_sla_fields(env)
