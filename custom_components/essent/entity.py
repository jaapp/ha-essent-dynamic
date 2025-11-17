"""Base entity for Essent integration."""
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import EssentDataUpdateCoordinator


class EssentEntity(CoordinatorEntity[EssentDataUpdateCoordinator]):
    """Base class for Essent entities."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: EssentDataUpdateCoordinator,
        energy_type: str,
    ) -> None:
        """Initialize the entity."""
        super().__init__(coordinator)
        self.energy_type = energy_type
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, "essent_dynamic_prices")},
            name="Essent Dynamic Prices",
            manufacturer="Essent",
        )
