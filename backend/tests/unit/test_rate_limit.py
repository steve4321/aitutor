"""Unit tests for the rate limiter module."""

from slowapi import Limiter
from slowapi.util import get_remote_address
from starlette.requests import Request

from app.core.rate_limit import limiter


class TestRateLimiter:
    def test_limiter_is_instance(self):
        assert isinstance(limiter, Limiter)

    def test_key_func_returns_string(self):
        req = Request({"type": "http", "client": ("127.0.0.1", 8000)})
        result = get_remote_address(req)
        assert isinstance(result, str)

    def test_key_func_uses_ip(self):
        req = Request({"type": "http", "client": ("192.168.1.1", 8000)})
        result = get_remote_address(req)
        assert result == "192.168.1.1"
