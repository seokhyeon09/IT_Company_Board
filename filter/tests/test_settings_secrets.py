# -*- coding: utf-8 -*-
import secrets
import pytest
from pydantic import ValidationError

from app.core.config import Settings


def _valid_pair() -> tuple[str, str]:
    return secrets.token_hex(32), secrets.token_hex(32)


def test_settings_accepts_valid_64_hex_secrets():
    """두 비밀키 모두 64자 무작위 hex 값이면 Settings 생성에 성공한다."""
    hmac_secret, jwt_secret = _valid_pair()
    cfg = Settings(
        _env_file=None,
        GATEWAY_SHARED_SECRET=hmac_secret,
        JWT_SECRET_KEY=jwt_secret,
    )
    assert cfg.GATEWAY_SHARED_SECRET == hmac_secret
    assert cfg.JWT_SECRET_KEY == jwt_secret


def test_settings_fails_without_secret_env_vars(monkeypatch):
    """환경변수가 없으면 기본값 없이 ValidationError로 실패한다."""
    monkeypatch.delenv("GATEWAY_SHARED_SECRET", raising=False)
    monkeypatch.delenv("JWT_SECRET_KEY", raising=False)
    with pytest.raises(ValidationError):
        Settings(_env_file=None)


@pytest.mark.parametrize("field_name", ["GATEWAY_SHARED_SECRET", "JWT_SECRET_KEY"])
def test_secret_length_boundary_31_rejected_32_accepted(field_name):
    """앞뒤 공백 제거 후 31자는 거부하고 32자는 허용한다."""
    valid_hmac, valid_jwt = _valid_pair()
    base = {"GATEWAY_SHARED_SECRET": valid_hmac, "JWT_SECRET_KEY": valid_jwt}

    too_short = secrets.token_hex(16)[:31]
    with pytest.raises(ValidationError):
        Settings(_env_file=None, **{**base, field_name: too_short})

    padded_short = f"  {too_short}  "
    with pytest.raises(ValidationError):
        Settings(_env_file=None, **{**base, field_name: padded_short})

    exact_min = secrets.token_hex(16)
    assert len(exact_min) == 32
    cfg = Settings(_env_file=None, **{**base, field_name: exact_min})
    assert getattr(cfg, field_name) == exact_min


@pytest.mark.parametrize("field_name", ["GATEWAY_SHARED_SECRET", "JWT_SECRET_KEY"])
@pytest.mark.parametrize(
    "bad_value",
    [
        "secure_inter_tier_hmac_secret_key_32_chars",
        "it_company_board_super_secret_jwt_key_2026_xyz",
        "production_change_in_env_super_secret_key",
        "gateway_odoo_tunnel_shared_secret_key",
        "MyChangeMeKey_0123456789abcdef012345",
        "dev_CHANGE_ME_0123456789abcdef012345",
        "custom_Secret_token_0123456789abcdef",
    ],
)
def test_known_insecure_and_placeholder_secrets_rejected(field_name, bad_value):
    """알려진 예시값과 changeme/change_me/secret 포함 값은 32자 이상이어도 거부한다."""
    valid_hmac, valid_jwt = _valid_pair()
    kwargs = {"GATEWAY_SHARED_SECRET": valid_hmac, "JWT_SECRET_KEY": valid_jwt}
    kwargs[field_name] = bad_value
    with pytest.raises(ValidationError):
        Settings(_env_file=None, **kwargs)


@pytest.mark.parametrize("field_name", ["GATEWAY_SHARED_SECRET", "JWT_SECRET_KEY"])
@pytest.mark.parametrize(
    "probe_secret",
    [
        "TooShortProbe_987654321",
        "MyChangeMeKey_LeakProbe_0123456789ab",
    ],
)
def test_validation_error_msg_does_not_leak_secret_value(field_name, probe_secret):
    """ValidationError의 msg에는 필드명이 포함되지만 입력한 비밀값은 포함되지 않는다."""
    valid_hmac, valid_jwt = _valid_pair()
    kwargs = {"GATEWAY_SHARED_SECRET": valid_hmac, "JWT_SECRET_KEY": valid_jwt}
    kwargs[field_name] = probe_secret

    with pytest.raises(ValidationError) as exc_info:
        Settings(_env_file=None, **kwargs)

    errors = exc_info.value.errors()
    assert errors
    for err in errors:
        assert probe_secret not in err["msg"]
        assert field_name in err["msg"]
