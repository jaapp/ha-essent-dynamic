"""Test the Essent entity."""
from unittest.mock import Mock

from homeassistant.core import HomeAssistant

from custom_components.essent.entity import EssentEntity
from custom_components.essent.const import ENERGY_TYPE_ELECTRICITY


async def test_entity_device_info(hass: HomeAssistant) -> None:
    """Test entity device info."""
    coordinator = Mock()
    entity = EssentEntity(coordinator, ENERGY_TYPE_ELECTRICITY)

    device_info = entity.device_info
    assert device_info["identifiers"] == {("essent", "essent_dynamic_prices")}
    assert device_info["name"] == "Essent Dynamic Prices"
    assert device_info["manufacturer"] == "Essent"
