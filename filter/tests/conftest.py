# -*- coding: utf-8 -*-
import pytest

from app.core.config import settings


@pytest.fixture(autouse=True)
def _trust_proxy_headers_in_tests():
    """기존 테스트가 X-Forwarded-For로 버킷을 분리하므로 각 테스트 동안만 True로 설정한다."""
    prev = settings.TRUST_PROXY_HEADERS
    settings.TRUST_PROXY_HEADERS = True
    try:
        yield
    finally:
        settings.TRUST_PROXY_HEADERS = prev
