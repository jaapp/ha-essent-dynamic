"""Test the Essent coordinator."""
from datetime import timedelta
from unittest.mock import AsyncMock, patch

import pytest
from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import UpdateFailed
from homeassistant.util import dt as dt_util
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.essent.coordinator import EssentDataUpdateCoordinator
from custom_components.essent.const import DOMAIN, UPDATE_INTERVAL


async def test_coordinator_fetch_success(
    hass: HomeAssistant, essent_api_response
) -> None:
    """Test successful data fetch."""
    coordinator = EssentDataUpdateCoordinator(hass)

    with patch("aiohttp.ClientSession.get") as mock_get, patch(
        "homeassistant.util.dt.now"
    ) as mock_now:
        mock_now.return_value = dt_util.as_local(
            dt_util.parse_datetime("2025-11-16T12:00:00")
        )
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value=essent_api_response)
        mock_get.return_value.__aenter__.return_value = mock_response

        coordinator.data = await coordinator._async_update_data()

    assert coordinator.data is not None
    assert "electricity" in coordinator.data
    assert "gas" in coordinator.data
    assert len(coordinator.data["electricity"]["tariffs"]) == 3
    assert len(coordinator.data["gas"]["tariffs"]) == 3
    assert coordinator.data["electricity"]["min_price"] == 0.2
    assert round(coordinator.data["electricity"]["avg_price"], 4) == 0.2233
    assert coordinator.data["electricity"]["max_price"] == 0.25


async def test_coordinator_fetch_failure(hass: HomeAssistant) -> None:
    """Test failed data fetch."""
    coordinator = EssentDataUpdateCoordinator(hass)

    with patch("aiohttp.ClientSession.get") as mock_get:
        mock_response = AsyncMock()
        mock_response.status = 500
        mock_get.return_value.__aenter__.return_value = mock_response

        with pytest.raises(UpdateFailed):
            await coordinator._async_update_data()
