"""Test the Essent diagnostics."""

from unittest.mock import AsyncMock, patch

from homeassistant.core import HomeAssistant
from homeassistant.util import dt as dt_util
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.essent.const import DOMAIN
from custom_components.essent.diagnostics import async_get_config_entry_diagnostics


async def test_diagnostics(
    hass: HomeAssistant,
    essent_api_response: dict,
    enable_custom_integrations: None,
) -> None:
    """Test diagnostics for config entry."""
    # Mock API response
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

        # Setup config entry
        entry = MockConfigEntry(
            domain=DOMAIN,
            title="Essent",
            data={},
            unique_id="essent_dynamic_prices",
        )
        entry.add_to_hass(hass)
        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

    diagnostics = await async_get_config_entry_diagnostics(hass, entry)

    # Verify structure
    assert "coordinator_data" in diagnostics
    assert "last_update_success" in diagnostics
    assert "api_fetch_minute_offset" in diagnostics
    assert "api_refresh_scheduled" in diagnostics
    assert "listener_tick_scheduled" in diagnostics

    # Verify data content
    assert diagnostics["last_update_success"] is True
    assert diagnostics["coordinator_data"] is not None
    assert "electricity" in diagnostics["coordinator_data"]
    assert "gas" in diagnostics["coordinator_data"]

    # Verify scheduling status
    assert diagnostics["api_refresh_scheduled"] is True
    assert diagnostics["listener_tick_scheduled"] is True

    # Verify minute offset is in valid range
    assert 0 <= diagnostics["api_fetch_minute_offset"] <= 59

    # Verify electricity data structure
    elec_data = diagnostics["coordinator_data"]["electricity"]
    assert "tariffs" in elec_data
    assert "unit" in elec_data
    assert "min_price" in elec_data
    assert "avg_price" in elec_data
    assert "max_price" in elec_data

    # Verify gas data structure
    gas_data = diagnostics["coordinator_data"]["gas"]
    assert "tariffs" in gas_data
    assert "unit" in gas_data
