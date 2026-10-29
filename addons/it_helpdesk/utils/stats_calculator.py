# -*- coding: utf-8 -*-
"""담당자별 처리 실적, SLA 준수율 및 MTTR(평균 해결 시간) 계산기 (Layer 2 유틸)."""
from collections import defaultdict
from odoo import fields
from .related_tickets import CATEGORY_LABELS

CLOSED_STATUSES = ("resolved", "closed", "canceled")


def _calc_avg_hours(measured_items) -> float:
    if not measured_items:
        return 0.0
    vals = []
    for item in measured_items:
        fr = item.get("first_resolved_date")
        cr = item.get("create_date")
        if fr and cr:
            if isinstance(fr, str):
                fr = fields.Datetime.from_string(fr)
            if isinstance(cr, str):
                cr = fields.Datetime.from_string(cr)
            hrs = max(0.0, (fr - cr).total_seconds() / 3600.0)
            vals.append(hrs)
    return round(sum(vals) / len(vals), 1) if vals else 0.0


def compute_officer_stats_payload(req_env, user) -> dict:
    """/api/v1/tickets/officer-stats 응답의 data 딕셔너리를 단일 패스로 계산한다."""
    read_fields = [
        "id", "status", "category", "is_overdue", "assignee_id",
        "rating", "first_resolved_date", "create_date"
    ]
    raw_tickets = req_env["it.helpdesk.ticket"].sudo().search_read(
        [("status", "!=", "canceled")], fields=read_fields
    )

    by_officer = defaultdict(list)
    by_category = defaultdict(list)
    unassigned_count = 0
    all_measured = []

    for t in raw_tickets:
        ass = t.get("assignee_id")
        uid = ass[0] if ass and isinstance(ass, (list, tuple)) else None
        if uid:
            by_officer[uid].append(t)
        elif t.get("status") == "submitted":
            unassigned_count += 1

        cat = t.get("category")
        if cat:
            by_category[cat].append(t)

        if t.get("first_resolved_date") and t.get("create_date"):
            all_measured.append(t)

    officer_group = user.env.ref("it_helpdesk.group_helpdesk_officer", raise_if_not_found=False)
    officer_users = officer_group.users.filtered(lambda u: u.active) if officer_group else req_env["res.users"]
    officer_ids = set(officer_users.ids) | set(by_officer.keys())

    root_user = user.env.ref("base.user_root", raise_if_not_found=False)
    root_id = root_user.id if root_user else 1

    officers = []
    rated_sum, rated_cnt, assigned_all, overdue_all = 0, 0, 0, 0

    for u in req_env["res.users"].sudo().browse(sorted(officer_ids)):
        if not u.exists() or u.id == root_id or (u._is_admin() and not u.has_group("it_helpdesk.group_helpdesk_officer")):
            continue
        mine = by_officer.get(u.id, [])
        n = len(mine)
        overdue = sum(1 for t in mine if t.get("is_overdue") and t.get("status") not in ("resolved", "closed"))
        scores = [int(t["rating"]) for t in mine if t.get("rating") in ("1", "2", "3", "4", "5")]
        rated_sum += sum(scores)
        rated_cnt += len(scores)
        assigned_all += n
        overdue_all += overdue

        mine_measured = [t for t in mine if t.get("first_resolved_date") and t.get("create_date")]
        officers.append({
            "officer_id": u.id,
            "officer_name": u.name,
            "officer_email": u.login,
            "total_assigned": n,
            "in_progress_count": sum(1 for t in mine if t.get("status") in ("assigned", "in_progress", "pending")),
            "resolved_count": sum(1 for t in mine if t.get("status") in ("resolved", "closed")),
            "overdue_count": overdue,
            "sla_compliance_rate": round((n - overdue) / n * 100.0, 1) if n else 100.0,
            "avg_rating": round(sum(scores) / len(scores), 2) if scores else 0.0,
            "rating_count": len(scores),
            "avg_resolution_hours": _calc_avg_hours(mine_measured),
            "resolved_measured_count": len(mine_measured),
        })

    officers.sort(key=lambda x: (x["resolved_count"], x["total_assigned"]), reverse=True)

    total = len(raw_tickets)
    categories = []
    for code, label in CATEGORY_LABELS.items():
        cat_tickets = by_category.get(code, [])
        cnt = len(cat_tickets)
        cat_measured = [t for t in cat_tickets if t.get("first_resolved_date") and t.get("create_date")]
        categories.append({
            "category": code,
            "label": label,
            "count": cnt,
            "percentage": round(cnt / total * 100.0, 1) if total else 0.0,
            "avg_resolution_hours": _calc_avg_hours(cat_measured),
        })

    return {
        "officers": officers,
        "category_breakdown": categories,
        "unassigned_count": unassigned_count,
        "total_active_tickets": total,
        "overall_avg_rating": round(rated_sum / rated_cnt, 2) if rated_cnt else 0.0,
        "overall_sla_rate": round((assigned_all - overdue_all) / assigned_all * 100.0, 1) if assigned_all else 100.0,
        "overall_avg_resolution_hours": _calc_avg_hours(all_measured),
    }
