# -*- coding: utf-8 -*-
"""도메인 공통 예외 클래스 정의."""
from odoo.exceptions import UserError


class NotFoundError(UserError):
    """요청한 대상 리소스를 찾을 수 없을 때 발생시키는 예외 (HTTP 404 매핑)."""
