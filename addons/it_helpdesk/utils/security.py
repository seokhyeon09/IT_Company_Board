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

_logger = logging.getLogger(__name__)

GATEWAY_SHARED_SECRET = os.environ.get("GATEWAY_SHARED_SECRET", "secure_inter_tier_hmac_secret_key_32_chars")

class ConcurrencyError(UserError):
    """Raised when an optimistic concurrency check detects a collision (HTTP 409)."""
    def __init__(self, message=None, current_write_date=None):
        msg = message or "Concurrent modification detected. The record has been modified by another transaction."
        super().__init__(msg)
        self.current_write_date = current_write_date

def get_current_request():
    """Retrieve active Odoo request, checking main_api mock patch first."""
    try:
        from odoo.addons.it_helpdesk.controllers import main_api
        return getattr(main_api, 'request', request)
    except Exception:
        return request

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
        try:
            ts = int(timestamp_str)
            uid = int(user_id_str)
        except (ValueError, TypeError):
            raise AccessError("Unauthorized: Invalid gateway identity credentials format.")

        # Replay protection: 60-second window
        if abs(time.time() - ts) > 60:
            raise AccessError("Unauthorized: Gateway signature expired.")

        method = req.method.upper()
        path = req.path
        raw_body = req.get_data() or b""
        body_hash = hashlib.sha256(raw_body).hexdigest()

        payload = f"{method}:{path}:{user_id_str}:{timestamp_str}:{body_hash}".encode('utf-8')
        expected_sig = hmac.new(GATEWAY_SHARED_SECRET.encode('utf-8'), payload, hashlib.sha256).hexdigest()

        # Strict HMAC verification: Reject all legacy payloads lacking body hash
        if not hmac.compare_digest(signature, expected_sig):
            raise AccessError("Unauthorized: Invalid gateway signature.")

        user = req_proxy.env['res.users'].sudo().browse(uid)
        if not user.exists() or not user.active:
            raise AccessError("Unauthorized: Inactive or non-existent user identity.")
        return user

    # Fallback to direct session user if logged in
    if req_proxy.session.uid:
        user = req_proxy.env['res.users'].sudo().browse(req_proxy.session.uid)
        if user.exists() and user.active:
            return user

    raise AccessError("Unauthorized: Missing gateway identity credentials or active session.")
