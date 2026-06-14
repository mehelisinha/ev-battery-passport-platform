"""Smoke tests for the shared config loader.

Keeps CI green from day one and verifies the import path (databricks/src is on
pythonpath via pyproject) works before any pipeline code exists.
"""

import pytest

from common.config import Settings, get_optional, get_required


def test_get_optional_returns_default_when_unset():
    assert get_optional("EV_BATTERY_DOES_NOT_EXIST_123", "fallback") == "fallback"


def test_get_optional_returns_none_by_default():
    assert get_optional("EV_BATTERY_DOES_NOT_EXIST_123") is None


def test_get_required_raises_when_missing():
    with pytest.raises(RuntimeError):
        get_required("EV_BATTERY_DOES_NOT_EXIST_123")


def test_settings_load_is_typed_and_safe_without_env():
    settings = Settings.load()
    assert settings.openlineage_namespace == "ev-battery-grid"
    assert settings.entsoe_api_token is None or isinstance(settings.entsoe_api_token, str)
