# -*- coding: utf-8 -*-
from fastapi import HTTPException, status
from app.core.config import settings
from app.core.security import create_access_token
from app.client.odoo_client import odoo_client
from app.schemas.auth import LoginRequest, TokenResponse, UserProfile

class AuthService:
    """Authentication and Identity Service"""

    async def authenticate_and_create_token(self, req: LoginRequest) -> TokenResponse:
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
            "is_admin": user_info.get("is_admin", False),
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
                is_admin=user_info.get("is_admin", False),
            )
        )

    def get_profile_from_claims(self, claims: dict) -> UserProfile:
        return UserProfile(
            uid=int(claims["sub"]),
            name=claims.get("name", ""),
            login=claims.get("login", ""),
            is_officer=bool(claims.get("is_officer", False)),
            is_admin=bool(claims.get("is_admin", False)),
        )

auth_service = AuthService()
