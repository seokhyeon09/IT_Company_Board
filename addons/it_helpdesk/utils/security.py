# -*- coding: utf-8 -*-
import os
import hmac
import hashlib
import time
import logging
from typing import Optional
from datetime import datetime, timezone
from odoo.http import request
from odoo.exceptions import AccessError, UserError
from odoo.addons.it_helpdesk.utils.request_context import get_current_request

_logger = logging.getLogger(__name__)

GATEWAY_SHARED_SECRET = os.environ.get("GATEWAY_SHARED_SECRET", "")

_MIN_SECRET_LENGTH = 32
_KNOWN_INSECURE_SECRETS = frozenset({
    "secure_inter_tier_hmac_secret_key_32_chars",
    "it_company_board_super_secret_jwt_key_2026_xyz",
    "production_change_in_env_super_secret_key",
    "gateway_odoo_tunnel_shared_secret_key",
})


def _gateway_secret_is_safe(secret: Optional[str]) -> bool:
    """게이트웨이 공유 비밀키가 최소 길이와 안전 기준을 충족하는지 확인한다."""
    if not isinstance(secret, str):
        return False
    cleaned = secret.strip()
    return len(cleaned) >= _MIN_SECRET_LENGTH and cleaned.lower() not in _KNOWN_INSECURE_SECRETS


class ConcurrencyError(UserError):
    """Raised when an optimistic concurrency check detects a collision (HTTP 409)."""
    def __init__(self, message=None, current_write_date=None):
        msg = message or "다른 사용자가 먼저 수정했습니다. 새로고침 후 다시 시도해 주세요."
        super().__init__(msg)
        self.current_write_date = current_write_date

def verify_gateway_request():
    """Verify HMAC signature from trusted FastAPI Gateway and switch user context.
    
    Hardened HMAC binds: HTTP Method, Path, User ID, Timestamp, and SHA-256 Body Hash.
    Falls back to current session user if authenticated directly.
    """
    req_proxy = get_current_request()
    req = req_proxy.httprequest
    headers = req.headers
    user_id_str = headers.get("X-Gateway-User-Id")
    timestamp_str = headers.get("X-Gateway-Timestamp")
    signature = headers.get("X-Gateway-Signature")

    # If Gateway HMAC headers are present, verify HMAC
    if user_id_str and timestamp_str and signature:
        if not _gateway_secret_is_safe(GATEWAY_SHARED_SECRET):
            _logger.error("GATEWAY_SHARED_SECRET 환경변수가 설정되지 않았거나 안전하지 않습니다.")
            raise AccessError("게이트웨이 인증 설정이 올바르지 않아 요청을 처리할 수 없습니다.")

        try:
            ts = int(timestamp_str)
            uid = int(user_id_str)
        except (ValueError, TypeError):
            raise AccessError("인증 정보 형식이 올바르지 않습니다.")

        # Replay protection: 60-second window
        if abs(time.time() - ts) > 60:
            raise AccessError("인증 요청이 만료되었습니다. 다시 시도해 주세요.")

        method = req.method.upper()
        path = req.path
        raw_body = req.get_data() or b""
        body_hash = hashlib.sha256(raw_body).hexdigest()

        payload = f"{method}:{path}:{user_id_str}:{timestamp_str}:{body_hash}".encode('utf-8')
        expected_sig = hmac.new(GATEWAY_SHARED_SECRET.encode('utf-8'), payload, hashlib.sha256).hexdigest()

        # Strict HMAC verification: Reject all legacy payloads lacking body hash
        if not hmac.compare_digest(signature, expected_sig):
            raise AccessError("게이트웨이 서명이 올바르지 않습니다.")

        user = req_proxy.env['res.users'].sudo().browse(uid)
        if not user.exists() or not user.active:
            raise AccessError("비활성화되었거나 존재하지 않는 사용자입니다.")
        return user

    # Fallback to direct session user if logged in
    if req_proxy.session.uid:
        user = req_proxy.env['res.users'].sudo().browse(req_proxy.session.uid)
        if user.exists() and user.active:
            return user

    raise AccessError("인증 정보가 없거나 세션이 만료되었습니다.")
