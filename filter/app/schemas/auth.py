# -*- coding: utf-8 -*-
from typing import Optional
from pydantic import BaseModel, Field

class LoginRequest(BaseModel):
    login: str = Field(..., min_length=2, max_length=100)
    password: str = Field(..., min_length=1)
    db: Optional[str] = None

class UserProfile(BaseModel):
    uid: int
    name: str
    login: str
    is_officer: bool

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserProfile
