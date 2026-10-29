# -*- coding: utf-8 -*-
"""담당자별 처리 실적, SLA 준수율 및 MTTR(평균 해결 시간) 계산기 (Layer 2 유틸)."""
from .related_tickets import CATEGORY_LABELS


def _measured_tickets(tickets):
    """MTTR 측정 대상 티켓: 취소되지 않고 first_resolved_date가 기록된 티켓."""
    return [
        t for t in tickets
        if t.status != "canceled" and bool(t.first_resolved_date) and t.create_date
    ]


def _avg_hours(measured_list) -> float:
    if not measured_list:
        return 0.0
    vals = []
    for t in measured_list:
        hrs = max(0.0, (t.first_resolved_date - t.create_date).total_seconds() / 3600.0)
        vals.append(hrs)
    return round(sum(vals) / len(vals), 1)


def compute_officer_stats_payload(req_env, user) -> dict:
    """/api/v1/tickets/officer-stats 응답의 data 딕셔너리를 계산한다."""
    all_tickets = req_env["it.helpdesk.ticket"].sudo().search([("status", "!=", "canceled")])
    officer_ids = set()
    for xmlid in ("it_helpdesk.group_helpdesk_officer", "base.group_system"):
        grp = user.env.ref(xmlid, raise_if_not_found=False)
        if grp:
            officer_ids.update(grp.users.filtered(lambda u: u.active).ids)
    officer_ids.update(t.assignee_id.id for t in all_tickets if t.assignee_id)

    officers = []
    rated_sum, rated_cnt, assigned_all, overdue_all = 0, 0, 0, 0

    for u in req_env["res.users"].sudo().browse(sorted(officer_ids)):
        if not u.exists() or u.id == 1:
            continue
        mine = all_tickets.filtered(lambda t: t.assignee_id.id == u.id)
        n = len(mine)
        overdue = len(mine.filtered(lambda t: t.is_overdue and t.status not in ("resolved", "closed")))
        scores = [int(t.rating) for t in mine if t.rating in ("1", "2", "3", "4", "5")]
        rated_sum += sum(scores)
        rated_cnt += len(scores)
        assigned_all += n
        overdue_all += overdue

        mine_measured = _measured_tickets(mine)
        officers.append({
            "officer_id": u.id,
            "officer_name": u.name,
            "officer_email": u.login,
            "total_assigned": n,
            "in_progress_count": len(mine.filtered(lambda t: t.status in ("assigned", "in_progress", "pending"))),
            "resolved_count": len(mine.filtered(lambda t: t.status in ("resolved", "closed"))),
            "overdue_count": overdue,
            "sla_compliance_rate": round((n - overdue) / n * 100.0, 1) if n else 100.0,
            "avg_rating": round(sum(scores) / len(scores), 2) if scores else 0.0,
            "rating_count": len(scores),
            "avg_resolution_hours": _avg_hours(mine_measured),
            "resolved_measured_count": len(mine_measured),
        })

    officers.sort(key=lambda x: (x["resolved_count"], x["total_assigned"]), reverse=True)

    total = len(all_tickets)
    categories = []
    for code, label in CATEGORY_LABELS.items():
        cat_tickets = all_tickets.filtered(lambda t: t.category == code)
        cnt = len(cat_tickets)
        cat_measured = _measured_tickets(cat_tickets)
        categories.append({
            "category": code,
            "label": label,
            "count": cnt,
            "percentage": round(cnt / total * 100.0, 1) if total else 0.0,
            "avg_resolution_hours": _avg_hours(cat_measured),
        })

    all_measured = _measured_tickets(all_tickets)
    return {
        "officers": officers,
        "category_breakdown": categories,
        "unassigned_count": len(all_tickets.filtered(lambda t: not t.assignee_id and t.status == "submitted")),
        "total_active_tickets": total,
        "overall_avg_rating": round(rated_sum / rated_cnt, 2) if rated_cnt else 0.0,
        "overall_sla_rate": round((assigned_all - overdue_all) / assigned_all * 100.0, 1) if assigned_all else 100.0,
        "overall_avg_resolution_hours": _avg_hours(all_measured),
    }
