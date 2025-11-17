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
    hass: HomeAssistant, electricity_api_response, gas_api_response
) -> None:
    """Test successful data fetch."""
    coordinator = EssentDataUpdateCoordinator(hass)

    with patch("aiohttp.ClientSession.get") as mock_get:
        mock_response_electricity = AsyncMock()
        mock_response_electricity.status = 200
        mock_response_electricity.json = AsyncMock(return_value=electricity_api_response)

        mock_response_gas = AsyncMock()
        mock_response_gas.status = 200
        mock_response_gas.json = AsyncMock(return_value=gas_api_response)

        ctx_electricity = AsyncMock()
        ctx_electricity.__aenter__.return_value = mock_response_electricity
        ctx_gas = AsyncMock()
        ctx_gas.__aenter__.return_value = mock_response_gas

        mock_get.side_effect = [ctx_electricity, ctx_gas]

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
