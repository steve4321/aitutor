"""Unit tests for configuration SECRET_KEY validation."""
import uuid

import pytest

from app.config import Settings, _DEFAULT_SECRET


class TestSecretKeyValidation:
    def test_development_accepts_default_key(self):
        s = Settings(ENVIRONMENT="development", SECRET_KEY=_DEFAULT_SECRET)
        assert s.SECRET_KEY == _DEFAULT_SECRET

    def test_development_accepts_short_key(self):
        s = Settings(ENVIRONMENT="development", SECRET_KEY="short")
        assert s.SECRET_KEY == "short"

    def test_production_rejects_default_key(self):
        with pytest.raises(ValueError, match="SECRET_KEY"):
            Settings(ENVIRONMENT="production", SECRET_KEY=_DEFAULT_SECRET)

    def test_production_rejects_short_key(self):
        with pytest.raises(ValueError, match="SECRET_KEY"):
            Settings(ENVIRONMENT="production", SECRET_KEY="a" * 31)

    def test_production_accepts_long_custom_key(self):
        key = "a" * 32
        s = Settings(ENVIRONMENT="production", SECRET_KEY=key)
        assert s.SECRET_KEY == key

    def test_production_accepts_uuid_key(self):
        key = str(uuid.uuid4())
        s = Settings(ENVIRONMENT="production", SECRET_KEY=key)
        assert len(s.SECRET_KEY) >= 32
