# -*- coding: utf-8 -*-
import time
import hmac
import hashlib
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from jose import jwt, JWTError
from fastapi import HTTPException, Security, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.config import settings

security_scheme = HTTPBearer()

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a signed JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> Dict[str, Any]:
    """Decode and validate a JWT access token."""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e

async def get_current_user_claims(credentials: HTTPAuthorizationCredentials = Security(security_scheme)) -> Dict[str, Any]:
    """FastAPI Dependency for extracting current user claims from Bearer token."""
    token = credentials.credentials
    claims = decode_access_token(token)
    if "sub" not in claims:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload: missing sub",
        )
    return claims

def generate_hmac_headers(user_id: int, method: str, path: str, body: bytes = b'') -> Dict[str, str]:
    """Generate tamper-proof HMAC-SHA256 headers for Odoo inter-tier identity propagation."""
    ts = str(int(time.time()))
    uid_str = str(user_id)
    body_hash = hashlib.sha256(body).hexdigest()
    
    payload = f"{method.upper()}:{path}:{uid_str}:{ts}:{body_hash}".encode('utf-8')
    sig = hmac.new(settings.GATEWAY_SHARED_SECRET.encode('utf-8'), payload, hashlib.sha256).hexdigest()
    
    return {
        "X-Gateway-User-Id": uid_str,
        "X-Gateway-Timestamp": ts,
        "X-Gateway-Signature": sig,
    }
