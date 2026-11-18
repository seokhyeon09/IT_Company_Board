# -*- coding: utf-8 -*-
from typing import Optional, Tuple
from app.client.odoo_client import odoo_client
from app.utils.csv_export import build_ticket_csv_bytes

MAX_EXPORT_ROWS = 5000


class ExportService:
    """티켓 목록 CSV 내보내기 서비스."""

    async def export_tickets_csv(
        self,
        user_id: int,
        category: Optional[str] = None,
        priority: Optional[str] = None,
        status: Optional[str] = None,
        search: Optional[str] = None,
        is_faq: Optional[bool] = None,
        is_overdue: Optional[bool] = None,
        assigned_to_me: Optional[bool] = None,
        sort_by: Optional[str] = "id desc",
    ) -> Tuple[bytes, bool]:
        params = {
            "category": category,
            "priority": priority,
            "status": status,
            "search": search,
            "is_faq": is_faq,
            "is_overdue": is_overdue,
            "assigned_to_me": assigned_to_me,
            "sort_by": sort_by,
            "limit": MAX_EXPORT_ROWS,
        }
        result = await odoo_client.call_json(
            "/api/v1/tickets/export",
            params=params,
            user_id=user_id,
            timeout=30.0,
        )
        tickets = result.get("data", [])
        total = result.get("total", len(tickets))
        truncated = total > MAX_EXPORT_ROWS
        return build_ticket_csv_bytes(tickets[:MAX_EXPORT_ROWS]), truncated


export_service = ExportService()
