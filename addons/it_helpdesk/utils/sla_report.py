# -*- coding: utf-8 -*-
"""기간별 SLA 리포트 집계 유틸 (Odoo _read_group 기반, KST 버킷팅)."""
import re
from datetime import date, datetime, timedelta, timezone

from odoo import fields
from odoo.exceptions import UserError

from .related_tickets import CATEGORY_LABELS

KST = timezone(timedelta(hours=9))
_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

PRIORITY_LABELS = {"0": "낮음", "1": "보통", "2": "높음", "3": "긴급"}

VALID_UNITS = ("week", "month")
MAX_RANGE_DAYS = 366
DEFAULT_RANGE_DAYS = 83
CLOSED_STATUSES = ("resolved", "closed", "canceled")


def _parse_kst_date(raw) -> date:
    if not isinstance(raw, str) or not _DATE_RE.match(raw):
        raise UserError("날짜 형식이 올바르지 않습니다. (YYYY-MM-DD)")
    try:
        return date.fromisoformat(raw)
    except ValueError as exc:
        raise UserError("날짜 형식이 올바르지 않습니다. (YYYY-MM-DD)") from exc


def validate_report_params(date_from=None, date_to=None, unit=None, category=None):
    """리포트 조회 파라미터를 검증하고 KST 기준 (d_from, d_to, unit, category)를 반환한다."""
    today_kst = datetime.now(KST).date()
    d_to = today_kst if date_to is None else _parse_kst_date(date_to)
    d_from = (d_to - timedelta(days=DEFAULT_RANGE_DAYS)) if date_from is None else _parse_kst_date(date_from)

    if d_from > d_to:
        raise UserError("시작일이 종료일보다 늦을 수 없습니다.")
    if (d_to - d_from).days + 1 > MAX_RANGE_DAYS:
        raise UserError("조회 기간은 최대 366일입니다.")

    unit_val = "week" if unit is None else unit
    if unit_val not in VALID_UNITS:
        raise UserError("집계 단위는 week 또는 month여야 합니다.")

    cat_val = None if category in (None, "") else category
    if cat_val is not None and cat_val not in CATEGORY_LABELS:
        raise UserError("유효하지 않은 분야입니다.")

    return d_from, d_to, unit_val, cat_val


def _kst_range_to_utc_strings(d_from: date, d_to: date):
    start_kst = datetime(d_from.year, d_from.month, d_from.day, 0, 0, 0, tzinfo=KST)
    end_excl_kst = start_kst + timedelta(days=(d_to - d_from).days + 1)
    start_utc = start_kst.astimezone(timezone.utc).replace(tzinfo=None)
    end_excl_utc = end_excl_kst.astimezone(timezone.utc).replace(tzinfo=None)
    return fields.Datetime.to_string(start_utc), fields.Datetime.to_string(end_excl_utc)


def _generate_bucket_keys(d_from: date, d_to: date, unit: str):
    keys = []
    if unit == "week":
        cur = d_from - timedelta(days=d_from.weekday())
        end = d_to - timedelta(days=d_to.weekday())
        while cur <= end:
            keys.append(cur.isoformat())
            cur += timedelta(days=7)
        return keys

    y, m = d_from.year, d_from.month
    end_ym = (d_to.year, d_to.month)
    while (y, m) <= end_ym:
        keys.append(f"{y:04d}-{m:02d}-01")
        if m == 12:
            y += 1
            m = 1
        else:
            m += 1
    return keys


def _normalize_bucket_key(raw_val, unit: str):
    if raw_val in (None, False, ""):
        return None
    if isinstance(raw_val, str):
        cleaned = raw_val.strip()
        if len(cleaned) == 10:
            raw_val = date.fromisoformat(cleaned)
        else:
            raw_val = datetime.fromisoformat(cleaned.replace("Z", "+00:00"))

    if isinstance(raw_val, datetime):
        if raw_val.tzinfo is not None:
            d = raw_val.astimezone(KST).date()
        elif raw_val.hour == 0 and raw_val.minute == 0 and raw_val.second == 0:
            d = raw_val.date()
        else:
            d = (raw_val + timedelta(hours=9)).date()
    elif isinstance(raw_val, date):
        d = raw_val
    else:
        return None

    if unit == "month":
        return f"{d.year:04d}-{d.month:02d}-01"
    monday = d - timedelta(days=d.weekday())
    return monday.isoformat()


def _calc_rate(on_time: int, breached: int):
    denom = on_time + breached
    return round(on_time / denom * 100.0, 1) if denom > 0 else None


def _calc_avg_hours(hours_sum: float, count: int):
    return round(hours_sum / count, 1) if count > 0 else None


def _empty_bucket():
    return {"created": 0, "on_time": 0, "breached": 0, "res_hours_sum": 0.0}


def _add_resolved_row(bucket: dict, on_time_flag, count: int, res_sum):
    if on_time_flag:
        bucket["on_time"] += count
    else:
        bucket["breached"] += count
    bucket["res_hours_sum"] += float(res_sum or 0.0)


def _aggregate_dimension(ticket_env, created_domain, resolved_domain, field_name: str, label_map: dict, key_name: str):
    buckets = {code: _empty_bucket() for code in label_map}
    for code, count in ticket_env._read_group(created_domain, groupby=[field_name], aggregates=["__count"]):
        if code in buckets:
            buckets[code]["created"] += count
    for code, on_time_flag, count, res_sum in ticket_env._read_group(
        resolved_domain, groupby=[field_name, "first_resolved_on_time"], aggregates=["__count", "resolution_hours:sum"]
    ):
        if code in buckets:
            _add_resolved_row(buckets[code], on_time_flag, count, res_sum)

    rows = []
    for code, label in label_map.items():
        b = buckets[code]
        resolved = b["on_time"] + b["breached"]
        rows.append({
            key_name: code, "label": label, "created": b["created"], "resolved": resolved,
            "on_time_rate": _calc_rate(b["on_time"], b["breached"]),
            "avg_resolution_hours": _calc_avg_hours(b["res_hours_sum"], resolved),
        })
    return rows


def build_sla_report(req_env, user, date_from=None, date_to=None, unit=None, category=None) -> dict:
    """DB 집계(_read_group/search_count)로 기간별 SLA 리포트 페이로드를 생성한다."""
    d_from, d_to, unit_val, cat_val = validate_report_params(date_from, date_to, unit, category)
    start_utc, end_excl_utc = _kst_range_to_utc_strings(d_from, d_to)

    ticket_env = req_env["it.helpdesk.ticket"].with_user(user).with_context(tz="Asia/Seoul")
    cat_domain = [("category", "=", cat_val)] if cat_val else []
    created_domain = cat_domain + [("create_date", ">=", start_utc), ("create_date", "<", end_excl_utc)]
    resolved_domain = cat_domain + [("first_resolved_date", ">=", start_utc), ("first_resolved_date", "<", end_excl_utc)]

    bucket_keys = _generate_bucket_keys(d_from, d_to, unit_val)
    series_map = {key: _empty_bucket() for key in bucket_keys}

    # 주 시작은 로케일(일요일/월요일)에 좌우되므로 일 단위로 묶은 뒤 월요일/월 기준으로 직접 합산한다.
    for bucket_val, count in ticket_env._read_group(created_domain, groupby=["create_date:day"], aggregates=["__count"]):
        key = _normalize_bucket_key(bucket_val, unit_val)
        if key in series_map:
            series_map[key]["created"] += count

    for bucket_val, on_time_flag, count, res_sum in ticket_env._read_group(
        resolved_domain, groupby=["first_resolved_date:day", "first_resolved_on_time"],
        aggregates=["__count", "resolution_hours:sum"],
    ):
        key = _normalize_bucket_key(bucket_val, unit_val)
        if key in series_map:
            _add_resolved_row(series_map[key], on_time_flag, count, res_sum)

    series = []
    tot_created = tot_on_time = tot_breached = 0
    tot_res_hours = 0.0
    for key in bucket_keys:
        b = series_map[key]
        resolved = b["on_time"] + b["breached"]
        tot_created += b["created"]
        tot_on_time += b["on_time"]
        tot_breached += b["breached"]
        tot_res_hours += b["res_hours_sum"]
        series.append({
            "period": key,
            "created": b["created"],
            "resolved": resolved,
            "on_time": b["on_time"],
            "breached": b["breached"],
            "on_time_rate": _calc_rate(b["on_time"], b["breached"]),
            "avg_resolution_hours": _calc_avg_hours(b["res_hours_sum"], resolved),
        })

    tot_resolved = tot_on_time + tot_breached
    paused_rows = ticket_env._read_group(
        created_domain + [("sla_paused_seconds", ">", 0)],
        groupby=[],
        aggregates=["sla_paused_seconds:avg", "__count"],
    )
    avg_paused_hours = None
    if paused_rows and paused_rows[0][1] and paused_rows[0][0] is not None:
        avg_paused_hours = round(float(paused_rows[0][0]) / 3600.0, 1)

    return {
        "range": {
            "date_from": d_from.isoformat(),
            "date_to": d_to.isoformat(),
            "unit": unit_val,
            "category": cat_val,
        },
        "summary": {
            "created": tot_created,
            "resolved": tot_resolved,
            "on_time": tot_on_time,
            "breached": tot_breached,
            "on_time_rate": _calc_rate(tot_on_time, tot_breached),
            "avg_resolution_hours": _calc_avg_hours(tot_res_hours, tot_resolved),
            "open_now": ticket_env.search_count(cat_domain + [("status", "not in", CLOSED_STATUSES)]),
            "overdue_now": ticket_env.search_count(cat_domain + [("is_overdue", "=", True)]),
            "paused_now": ticket_env.search_count(cat_domain + [("status", "=", "pending")]),
            "avg_paused_hours": avg_paused_hours,
        },
        "series": series,
        "by_category": _aggregate_dimension(
            ticket_env, created_domain, resolved_domain, "category", CATEGORY_LABELS, "category"
        ),
        "by_priority": _aggregate_dimension(
            ticket_env, created_domain, resolved_domain, "priority", PRIORITY_LABELS, "priority"
        ),
    }
