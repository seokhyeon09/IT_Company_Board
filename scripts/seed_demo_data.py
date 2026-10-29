# -*- coding: utf-8 -*-
"""
IT Helpdesk 3-Tier System - Idempotent Demo Data Seed Runner
Usage:
  python scripts/seed_demo_data.py          # Idempotent seed
  python scripts/seed_demo_data.py --reset  # Reset [SEED] data and re-seed
"""
import os
import sys
import subprocess
from datetime import datetime, timedelta

try:
    import odoo
except ImportError:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    specs_f = os.path.join(script_dir, "seed_specs.py")
    with open(specs_f, "rb") as f1, open(os.path.abspath(__file__), "rb") as f2:
        code_payload = f1.read() + b"\n# --- RUNNER ---\n" + f2.read()
    res = subprocess.run(
        ["docker", "exec", "-i", "it_helpdesk_odoo", "python3", "-"] + sys.argv[1:],
        input=code_payload,
    )
    sys.exit(res.returncode)

if "USERS_SPEC" not in globals():
    from seed_specs import USERS_SPEC, TICKETS_SPEC, ASSIGN_RULES_SPEC

DB_NAME = os.environ.get("ODOO_DB", "helpdesk_db")
DB_HOST = os.environ.get("HOST", "db")
DB_USER = os.environ.get("USER", "odooU")
DB_PASSWORD = os.environ.get("PASSWORD", "odooPW")


def ensure_users(env):
    Users = env["res.users"].sudo()
    grp_user = env.ref("base.group_user")
    grp_officer = env.ref("it_helpdesk.group_helpdesk_officer")
    grp_manager = env.ref("it_helpdesk.group_helpdesk_manager")
    grp_system = env.ref("base.group_system")
    user_map = {}

    for spec in USERS_SPEC:
        user = Users.search([("login", "=", spec["login"])], limit=1)
        groups = [(4, grp_user.id)]
        if spec.get("is_officer"):
            groups.append((4, grp_officer.id))
        if spec.get("is_manager"):
            groups.append((4, grp_manager.id))
        if spec.get("is_admin"):
            groups.append((4, grp_system.id))

        vals = {"name": spec["name"], "email": spec["login"], "password": spec["password"], "groups_id": groups}
        if not user:
            vals["login"] = spec["login"]
            user = Users.create(vals)
            print(f"[SEED] Created user: {spec['name']} ({spec['login']})")
        else:
            user.write(vals)
            print(f"[SEED] Updated user: {spec['name']} ({spec['login']})")
        user_map[spec["login"]] = user
    return user_map


def ensure_assign_rules(env, user_map):
    """분야별 전담 담당자 규칙을 멱등하게 반영하고 자동 배정 스위치를 켠다."""
    Rule = env["it.helpdesk.assign.rule"].sudo().with_context(active_test=False)
    for category, logins in ASSIGN_RULES_SPEC.items():
        officer_ids = [user_map[login].id for login in logins]
        vals = {"category": category, "officer_ids": [(6, 0, officer_ids)], "active": True}
        rules = Rule.search([("category", "=", category)])
        if len(rules) > 1:
            rules[1:].unlink()
        rule = Rule.search([("category", "=", category)], limit=1)
        if rule:
            rule.write(vals)
            print(f"[SEED] Updated assign rule: {category} -> {logins}")
        else:
            Rule.create(vals)
            print(f"[SEED] Created assign rule: {category} -> {logins}")
    env["ir.config_parameter"].sudo().set_param("it_helpdesk.auto_assign_enabled", "True")
    print("[SEED] Auto-assign switch: ON")


def reset_seed_data(env, wipe_all=False):
    Ticket = env["it.helpdesk.ticket"].sudo()
    Att = env["ir.attachment"].sudo()
    Msg = env["mail.message"].sudo()
    tickets = Ticket.search([]) if wipe_all else Ticket.search([("title", "=like", "[SEED]%")])
    if tickets:
        lbl = "ALL" if wipe_all else "[SEED]"
        print(f"[RESET] Purging {len(tickets)} existing {lbl} tickets...")
        Att.search([("res_model", "=", "it.helpdesk.ticket"), ("res_id", "in", tickets.ids)]).unlink()
        Msg.search([("model", "=", "it.helpdesk.ticket"), ("res_id", "in", tickets.ids)]).unlink()
        tickets.rating_ids.unlink()
        tickets.unlink()
    env["it.helpdesk.notification.read"].sudo().search([]).unlink()
    if wipe_all:
        seq = env["ir.sequence"].sudo().search([("code", "=", "it.helpdesk.ticket")], limit=1)
        if seq:
            seq.write({"number_next": 1})
            print("[RESET] Reset ticket sequence to 1.")
    print("[RESET] Clean reset finished.")


def _handle_ticket_lifecycle(ticket, spec, author, user_map, now):
    if spec.get("initial_assignee") and spec.get("reassign_reason"):
        old_u = user_map[spec["initial_assignee"]]
        new_u = user_map[spec["assignee"]]
        ticket.action_assign_to_user(old_u)
        ticket.action_assign_to_user(new_u)
        r_msg = f'<div data-msg-type="reassign" data-old-user-id="{old_u.id}"><b>[담당자 변경]</b> {old_u.name} -&gt; {new_u.name}<br/>인계 사유: {spec["reassign_reason"]}</div>'
        ticket.message_post(body=r_msg)
    elif spec.get("assignee"):
        ticket.action_assign_to_user(user_map[spec["assignee"]])

    tgt = spec["status"]
    if tgt in ("in_progress", "pending", "resolved", "closed"):
        if ticket.status == "assigned":
            ticket.action_start_progress()

    if spec.get("pending_reason") and spec.get("pending_response"):
        ticket.pending_reason = spec["pending_reason"]
        ticket.action_pending()
        ticket.message_post(body=f'<div data-msg-type="pending_request"><b>[답변 대기 요청]</b><br/>{spec["pending_reason"]}</div>')
        ticket.with_user(author).action_restart_ticket()
        ticket.message_post(body=f'<div data-msg-type="pending_response"><b>[답변 대기 회신]</b><br/>{spec["pending_response"]}</div>')
    elif tgt == "pending":
        ticket.pending_reason = spec.get("pending_reason", "추가 정보 회신 요청")
        ticket.action_pending()
        ticket.message_post(body=f'<div data-msg-type="pending_request"><b>[답변 대기 요청]</b><br/>{ticket.pending_reason}</div>')

    if spec.get("round1_resolution") and spec.get("restart_inquiry"):
        ticket.resolution_note = spec["round1_resolution"]
        ticket.action_resolve()
        ticket.message_post(body=f'<div data-msg-type="resolution"><b>[조치 답변]</b><br/>{spec["round1_resolution"]}</div>')
        ticket.with_user(author).action_restart_ticket()
        ticket.message_post(body=f'<div data-msg-type="inquiry"><b>[추가 재문의]</b><br/>{spec["restart_inquiry"]}</div>')

    if spec.get("resolution_before_edit"):
        ticket.message_post(body=f'<b>[답변 내용 수정 이력]</b><br/>[수정 전] {spec["resolution_before_edit"]}<br/>[수정 후] {spec.get("resolution_note", "")}')

    if tgt in ("resolved", "closed"):
        ticket.resolution_note = spec.get("resolution_note", "조치 완료되었습니다.")
        if ticket.status != "resolved":
            ticket.action_resolve()
        ticket.message_post(body=f'<div data-msg-type="resolution"><b>[조치 답변]</b><br/>{ticket.resolution_note}</div>')

    if tgt == "closed":
        if spec.get("rating"):
            ticket.rating = spec["rating"]
            ticket.rating_comment = spec.get("rating_comment", "")
            ticket.with_user(author).action_submit_rating()
        else:
            ticket.action_close()
    elif tgt == "canceled":
        ticket.with_user(author).action_cancel()
        if spec.get("cancel_reason"):
            ticket.message_post(body=f'<b>[문의 취소]</b><br/>취소 사유: {spec["cancel_reason"]}')

    if spec.get("overdue_hours"):
        ticket.write({"deadline": now - timedelta(hours=int(spec["overdue_hours"])), "is_overdue": True})
    if spec.get("is_faq"):
        ticket.write({"is_faq": True})
    if spec.get("resolution_hours_sim") and ticket.create_date:
        sim_dt = ticket.create_date + timedelta(hours=float(spec["resolution_hours_sim"]))
        ticket.write({"first_resolved_date": sim_dt})


def ensure_tickets(env, user_map):
    Ticket = env["it.helpdesk.ticket"].sudo()
    Att = env["ir.attachment"].sudo()
    now = datetime.utcnow()

    for spec in TICKETS_SPEC:
        existing = Ticket.search([("title", "=", spec["title"])], limit=1)
        if existing:
            print(f"[SEED] Exists: {existing.ticket_number} - {spec['title']}")
            continue

        author = user_map[spec["author"]]
        ticket = Ticket.with_user(author).create({
            "title": spec["title"],
            "category": spec["category"],
            "priority": spec["priority"],
            "status": "submitted",
            "author_id": author.id,
            "content": spec["content"],
        }).sudo()

        if spec.get("attachment"):
            att_info = spec["attachment"]
            Att.create({
                "name": att_info["name"], "datas": att_info["datas"],
                "mimetype": att_info.get("mimetype", "text/plain"),
                "res_model": "it.helpdesk.ticket", "res_id": ticket.id,
            })

        _handle_ticket_lifecycle(ticket, spec, author, user_map, now)
        print(f"[SEED] Created: {ticket.ticket_number} ({ticket.status}) - {spec['title']}")


def seed_sample_read_notifications(env, user_map):
    ReadModel = env["it.helpdesk.notification.read"].sudo()
    Ticket = env["it.helpdesk.ticket"].sudo()
    u_officer = user_map.get("officer@test.com")
    t_reassign = Ticket.search([("title", "=like", "%[SEED]%ERP 재무회계%")], limit=1)
    if u_officer and t_reassign:
        nid = f"{t_reassign.id}-new"
        if not ReadModel.search([("user_id", "=", u_officer.id), ("notification_id", "=", nid)], limit=1):
            ReadModel.create({"user_id": u_officer.id, "notification_id": nid})
            print(f"[SEED] Sample notification read record created for {u_officer.login}")


def main():
    odoo.tools.config.parse_config(["-d", DB_NAME, f"--db_host={DB_HOST}", "-r", DB_USER, "-w", DB_PASSWORD])
    registry = odoo.modules.registry.Registry(DB_NAME)
    with registry.cursor() as cr:
        env = odoo.api.Environment(cr, odoo.SUPERUSER_ID, {})
        print("=" * 68)
        print("[SEED] Starting Idempotent Demo Data Seeding for IT Helpdesk...")
        print("=" * 68)
        if "--wipe-all" in sys.argv:
            reset_seed_data(env, wipe_all=True)
        elif "--reset" in sys.argv:
            reset_seed_data(env, wipe_all=False)
        user_map = ensure_users(env)
        ensure_assign_rules(env, user_map)
        ensure_tickets(env, user_map)
        seed_sample_read_notifications(env, user_map)
        cr.commit()
        print("=" * 68)
        print("[SEED] Demo Data Seeding Completed Successfully.")
        print("=" * 68)


if __name__ == "__main__":
    main()
