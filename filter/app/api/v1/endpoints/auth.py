# -*- coding: utf-8 -*-
from fastapi import APIRouter, HTTPException, Depends, status
from app.core.config import settings
from app.core.security import create_access_token, get_current_user_claims
from app.client.odoo_client import odoo_client
from app.schemas.auth import LoginRequest, TokenResponse, UserProfile

router = APIRouter()

@router.post("/login", response_model=TokenResponse)
async def login(req: LoginRequest):
    """Authenticate with Odoo backend and issue JWT Bearer Token."""
    target_db = req.db or settings.ODOO_DB

    # 사용자 편의를 위한 숏컷 별칭 매핑 (이메일 도메인 생략 허용)
    raw_login = req.login.strip().lower()
    alias_map = {
        "admin": "admin@helpdesk.com",
        "officer": "officer@test.com",
        "user1": "user1@test.com",
        "user": "user1@test.com",
    }
    resolved_login = alias_map.get(raw_login, req.login.strip())

    result = await odoo_client.call_json(
        "/api/v1/auth/login",
        params={"db": target_db, "login": resolved_login, "password": req.password}
    )

    if result.get("status") != "success":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=result.get("message", "Invalid username or password")
        )

    user_info = result["data"]
    claims = {
        "sub": str(user_info["uid"]),
        "name": user_info["name"],
        "login": user_info["login"],
        "is_officer": user_info["is_officer"],
    }
    token = create_access_token(claims)

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user=UserProfile(
            uid=user_info["uid"],
            name=user_info["name"],
            login=user_info["login"],
            is_officer=user_info["is_officer"],
        )
    )

@router.get("/me", response_model=UserProfile)
async def get_me(claims: dict = Depends(get_current_user_claims)):
    """Retrieve current authenticated user's profile."""
    return UserProfile(
        uid=int(claims["sub"]),
        name=claims.get("name", ""),
        login=claims.get("login", ""),
        is_officer=bool(claims.get("is_officer", False)),
    )
