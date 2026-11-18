# -*- coding: utf-8 -*-
from typing import List
from pydantic import ValidationInfo, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_MIN_SECRET_LENGTH = 32
_KNOWN_INSECURE_SECRETS = frozenset({
    "secure_inter_tier_hmac_secret_key_32_chars",
    "it_company_board_super_secret_jwt_key_2026_xyz",
    "production_change_in_env_super_secret_key",
    "gateway_odoo_tunnel_shared_secret_key",
})
_FORBIDDEN_SECRET_SUBSTRINGS = ("changeme", "change_me", "secret")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    PROJECT_NAME: str = "IT Company Board - Gateway Filter"
    VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api/v1"

    # Odoo Configuration
    ODOO_RPC_URL: str = "http://localhost:8069"
    ODOO_DB: str = "helpdesk_db"
    GATEWAY_SHARED_SECRET: str

    # JWT Security Configuration
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 120

    # CORS Configuration
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]

    # 신뢰할 리버스 프록시 뒤에서만 True
    TRUST_PROXY_HEADERS: bool = False

    @field_validator("GATEWAY_SHARED_SECRET", "JWT_SECRET_KEY")
    @classmethod
    def _validate_secret(cls, value: str, info: ValidationInfo) -> str:
        cleaned = value.strip()
        lowered = cleaned.lower()
        if (
            len(cleaned) < _MIN_SECRET_LENGTH
            or lowered in _KNOWN_INSECURE_SECRETS
            or any(token in lowered for token in _FORBIDDEN_SECRET_SUBSTRINGS)
        ):
            raise ValueError(
                f"{info.field_name}은(는) {_MIN_SECRET_LENGTH}자 이상의 무작위 값이어야 하며 "
                "예시/기본값은 사용할 수 없습니다. "
                '생성 예: python -c "import secrets; print(secrets.token_hex(32))"'
            )
        return cleaned


settings = Settings()
