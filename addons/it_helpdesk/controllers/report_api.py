# -*- coding: utf-8 -*-
"""기간별 SLA 리포트 조회 API (담당자/관리자 전용)."""
from odoo import http

from ..utils import ensure_officer, get_current_request, verify_gateway_request
from ..utils.sla_report import build_sla_report


class ReportAPIController(http.Controller):
    """SLA Report API for Gateway"""

    @http.route('/api/v1/reports/sla', type='json', auth='none', methods=['POST'], csrf=False)
    def get_sla_report(
        self,
        date_from=None,
        date_to=None,
        unit=None,
        category=None,
        **kwargs,
    ):
        req_env = get_current_request().env
        user = verify_gateway_request()
        ensure_officer(user)

        data = build_sla_report(
            req_env,
            user,
            date_from=date_from,
            date_to=date_to,
            unit=unit,
            category=category,
        )
        return {"status": "success", "data": data}
