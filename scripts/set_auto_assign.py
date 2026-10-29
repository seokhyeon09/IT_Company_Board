# -*- coding: utf-8 -*-
"""자동 배정 스위치를 켜거나 끈다.

Usage:
  python scripts/set_auto_assign.py on
  python scripts/set_auto_assign.py off
기존 E2E 스크립트(접수 직후 접수대기를 가정)는 실행 전 off, 실행 후 on 으로 되돌린다.
"""
import subprocess
import sys
import time
import urllib.request

mode = sys.argv[1] if len(sys.argv) > 1 else ""
if mode not in ("on", "off"):
    print("Usage: python scripts/set_auto_assign.py on|off")
    sys.exit(2)

value = "True" if mode == "on" else "False"
code = (
    'env["ir.config_parameter"].sudo().set_param("it_helpdesk.auto_assign_enabled", "%s")\n'
    'env.cr.commit()\n'
    'print("RESULT auto_assign=" + env["ir.config_parameter"].sudo().get_param("it_helpdesk.auto_assign_enabled"))\n'
) % value

res = subprocess.run(
    ["docker", "exec", "-i", "it_helpdesk_odoo", "odoo", "shell", "-d", "helpdesk_db",
     "--db_host=db", "-r", "odooU", "-w", "odooPW", "--no-http"],
    input=code.encode("utf-8"), capture_output=True,
)
output = (res.stdout + res.stderr).decode("utf-8", errors="replace")
expected = "RESULT auto_assign=" + value
if expected in output:
    subprocess.run(["docker", "restart", "it_helpdesk_odoo"], capture_output=True)
    for _ in range(30):
        time.sleep(1)
        try:
            with urllib.request.urlopen("http://localhost:8069/web/login", timeout=2) as r:
                if r.status == 200:
                    break
        except Exception:
            pass
    print(expected)
    sys.exit(0)
print(output)
print("FAILED to set auto_assign switch")
sys.exit(1)
