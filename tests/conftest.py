"""Test fixtures for Essent integration."""
import json
from pathlib import Path
import pytest


@pytest.fixture
def essent_api_response():
    """Load sample API response."""
    fixture_path = Path(__file__).parent / "fixtures" / "essent_api_response.json"
    with open(fixture_path) as f:
        return json.load(f)
