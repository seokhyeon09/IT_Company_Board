# -*- coding: utf-8 -*-
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    PROJECT_NAME: str = "IT Company Board - Gateway Filter"
    VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api/v1"

    # Odoo Configuration
    ODOO_RPC_URL: str = "http://localhost:8069"
    ODOO_DB: str = "helpdesk_db"
    GATEWAY_SHARED_SECRET: str = "secure_inter_tier_hmac_secret_key_32_chars"

    # JWT Security Configuration
    JWT_SECRET_KEY: str = "it_company_board_super_secret_jwt_key_2026_xyz"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 120

    # CORS Configuration
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]

settings = Settings()
