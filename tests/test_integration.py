"""Full integration test."""
from unittest.mock import AsyncMock, patch

from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant
from homeassistant.setup import async_setup_component

from custom_components.essent.const import DOMAIN


async def test_full_integration_setup(hass: HomeAssistant, essent_api_response) -> None:
    """Test complete integration setup."""
    # Mock API response
    with patch("aiohttp.ClientSession.get") as mock_get:
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value=essent_api_response)
        mock_get.return_value.__aenter__.return_value = mock_response

        # Setup integration
        assert await async_setup_component(hass, DOMAIN, {})
        await hass.async_block_till_done()

        # Create config entry
        from homeassistant.config_entries import ConfigEntry

        entry = ConfigEntry(
            version=1,
            domain=DOMAIN,
            title="Essent",
            data={},
            source="user",
            unique_id="essent_dynamic_prices",
        )

        entry.add_to_hass(hass)
        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

        # Verify config entry loaded
        assert entry.state == ConfigEntryState.LOADED

        # Verify all sensors created
        assert hass.states.get("sensor.essent_electricity_current_price") is not None
        assert hass.states.get("sensor.essent_electricity_next_price") is not None
        assert hass.states.get("sensor.essent_electricity_average_today") is not None
        assert hass.states.get("sensor.essent_gas_current_price") is not None
        assert hass.states.get("sensor.essent_gas_next_price") is not None
        assert hass.states.get("sensor.essent_gas_average_today") is not None

        # Verify sensor states
        elec_current = hass.states.get("sensor.essent_electricity_current_price")
        assert elec_current.state != "unavailable"
        assert elec_current.attributes.get("unit_of_measurement") == "EUR/kWh"

        # Verify unload
        assert await hass.config_entries.async_unload(entry.entry_id)
        await hass.async_block_till_done()
        assert entry.state == ConfigEntryState.NOT_LOADED
