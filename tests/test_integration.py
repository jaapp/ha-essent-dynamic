"""Full integration test."""
from unittest.mock import AsyncMock, patch

from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant
from homeassistant.setup import async_setup_component
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.essent.const import DOMAIN


async def test_full_integration_setup(
    hass: HomeAssistant,
    electricity_api_response,
    gas_api_response,
    enable_custom_integrations: None,
) -> None:
    """Test complete integration setup."""
    # Mock API response
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

        # Setup integration
        assert await async_setup_component(hass, DOMAIN, {})
        await hass.async_block_till_done()

        entry = MockConfigEntry(
            domain=DOMAIN,
            title="Essent",
            data={},
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
        assert elec_current.attributes.get("unit_of_measurement") == "€/kWh"

        # Verify unload
        assert await hass.config_entries.async_unload(entry.entry_id)
        await hass.async_block_till_done()
        assert entry.state == ConfigEntryState.NOT_LOADED
