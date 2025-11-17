"""Test the Essent coordinator."""
from datetime import timedelta
from unittest.mock import AsyncMock, patch

import pytest
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import UpdateFailed
from homeassistant.util import dt as dt_util

from custom_components.essent.coordinator import EssentDataUpdateCoordinator
from custom_components.essent.const import UPDATE_INTERVAL


async def test_coordinator_fetch_success(hass: HomeAssistant, essent_api_response) -> None:
    """Test successful data fetch."""
    coordinator = EssentDataUpdateCoordinator(hass)

    with patch("aiohttp.ClientSession.get") as mock_get:
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value=essent_api_response)
        mock_get.return_value.__aenter__.return_value = mock_response

        await coordinator.async_config_entry_first_refresh()

    assert coordinator.data is not None
    assert "electricity" in coordinator.data
    assert "gas" in coordinator.data
    assert len(coordinator.data["electricity"]["tariffs"]) == 24
    assert len(coordinator.data["gas"]["tariffs"]) == 24


async def test_coordinator_fetch_failure(hass: HomeAssistant) -> None:
    """Test failed data fetch."""
    coordinator = EssentDataUpdateCoordinator(hass)

    with patch("aiohttp.ClientSession.get") as mock_get:
        mock_response = AsyncMock()
        mock_response.status = 500
        mock_get.return_value.__aenter__.return_value = mock_response

        with pytest.raises(UpdateFailed):
            await coordinator.async_config_entry_first_refresh()
