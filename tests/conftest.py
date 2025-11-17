"""Test fixtures for Essent integration."""
import json
from pathlib import Path

import pytest

pytest_plugins = ("pytest_homeassistant_custom_component", "pytest_asyncio")
pytestmark = pytest.mark.asyncio


def _load_fixture(name: str) -> dict:
    fixture_path = Path(__file__).parent / "fixtures" / name
    with open(fixture_path, encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture
def electricity_api_response() -> dict:
    """Load sample electricity API response."""
    return _load_fixture("electricity_api_response.json")


@pytest.fixture
def gas_api_response() -> dict:
    """Load sample gas API response."""
    return _load_fixture("gas_api_response.json")


@pytest.fixture
def essent_api_response(electricity_api_response, gas_api_response) -> dict:
    """Combined response helper for full integration tests."""
    return _load_fixture("essent_api_response.json")
