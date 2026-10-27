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
    result = await odoo_client.call_json(
        "/api/v1/auth/login",
        params={"db": target_db, "login": req.login.strip(), "password": req.password}
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
