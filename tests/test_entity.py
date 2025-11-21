"""Test the Essent entity."""
from unittest.mock import Mock

from homeassistant.core import HomeAssistant

from custom_components.essent.entity import EssentEntity
from custom_components.essent.const import ENERGY_TYPE_ELECTRICITY


async def test_entity_device_info(hass: HomeAssistant) -> None:
    """Test entity device info."""
    coordinator = Mock()
    coordinator.config_entry = Mock(entry_id="test_entry")
    entity = EssentEntity(coordinator, ENERGY_TYPE_ELECTRICITY)

    device_info = entity.device_info
    assert device_info["identifiers"] == {("essent", "test_entry")}
    assert device_info["name"] == "Essent"
    assert device_info["manufacturer"] == "Essent"
