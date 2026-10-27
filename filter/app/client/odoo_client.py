# -*- coding: utf-8 -*-
import json
import logging
import httpx
from typing import Any, Dict, Optional
from fastapi import HTTPException, status
from app.core.config import settings
from app.core.security import generate_hmac_headers

_logger = logging.getLogger(__name__)

class OdooClient:
    def __init__(self):
        self.base_url = settings.ODOO_RPC_URL

    async def call_json(
        self,
        endpoint: str,
        params: dict,
        user_id: Optional[int] = None,
        timeout: float = 10.0
    ) -> Dict[str, Any]:
        """Make an asynchronous JSON-RPC call to Odoo with HMAC identity propagation."""
        url = f"{self.base_url.rstrip('/')}{endpoint}"
        raw_body = json.dumps({"jsonrpc": "2.0", "method": "call", "params": params, "id": 1}).encode('utf-8')

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        if user_id is not None:
            hmac_headers = generate_hmac_headers(user_id=user_id, method="POST", path=endpoint, body=raw_body)
            headers.update(hmac_headers)

        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                resp = await client.post(url, content=raw_body, headers=headers)
                
            if resp.status_code == 409:
                data = resp.json()
                msg = data.get("error", {}).get("data", {}).get("message", "Optimistic concurrency conflict")
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=msg)

            if resp.status_code >= 500:
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail=f"Odoo backend server error (HTTP {resp.status_code})"
                )

            data = resp.json()

            # Handle JSON-RPC errors
            if "error" in data:
                err_data = data["error"].get("data", {})
                message = err_data.get("message") or data["error"].get("message") or "Odoo RPC execution error"
                name = err_data.get("name", "")

                if "AccessError" in name:
                    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=message)
                if "ConcurrencyError" in name:
                    raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=message)
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)

            result = data.get("result", {})
            return result

        except httpx.ConnectError as e:
            _logger.error("Failed to connect to Odoo backend: %s", e)
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Odoo backend is temporarily unavailable"
            ) from e
        except httpx.TimeoutException as e:
            _logger.error("Timeout waiting for Odoo backend: %s", e)
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail="Odoo backend request timed out"
            ) from e

odoo_client = OdooClient()
