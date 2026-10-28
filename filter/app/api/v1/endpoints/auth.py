# -*- coding: utf-8 -*-
from fastapi import APIRouter, Depends
from app.core.security import get_current_user_claims
from app.schemas.auth import LoginRequest, TokenResponse, UserProfile
from app.services import auth_service

router = APIRouter()

@router.post("/login", response_model=TokenResponse)
async def login(req: LoginRequest):
    """Authenticate with Odoo backend and issue JWT Bearer Token."""
    return await auth_service.authenticate_and_create_token(req)

@router.get("/me", response_model=UserProfile)
async def get_me(claims: dict = Depends(get_current_user_claims)):
    """Retrieve current authenticated user's profile."""
    return auth_service.get_profile_from_claims(claims)
