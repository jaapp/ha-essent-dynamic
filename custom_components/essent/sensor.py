"""Sensor platform for Essent integration."""
from __future__ import annotations

from datetime import datetime
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CURRENCY_EURO
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util import dt as dt_util

from .const import DOMAIN, ENERGY_TYPE_ELECTRICITY, ENERGY_TYPE_GAS
from .coordinator import EssentDataUpdateCoordinator
from .entity import EssentEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Essent sensors."""
    coordinator: EssentDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities: list[SensorEntity] = []

    for energy_type in [ENERGY_TYPE_ELECTRICITY, ENERGY_TYPE_GAS]:
        entities.append(EssentCurrentPriceSensor(coordinator, energy_type))

    async_add_entities(entities)


class EssentCurrentPriceSensor(EssentEntity, SensorEntity):
    """Current price sensor."""

    _attr_device_class = SensorDeviceClass.MONETARY
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(
        self,
        coordinator: EssentDataUpdateCoordinator,
        energy_type: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, energy_type)
        self._attr_unique_id = f"{energy_type}_current_price"
        self._attr_translation_key = f"{energy_type}_current_price"

    @property
    def native_value(self) -> float | None:
        """Return the current price."""
        now = dt_util.now()
        tariffs = self.coordinator.data[self.energy_type]["tariffs"]

        for tariff in tariffs:
            start = dt_util.parse_datetime(tariff["startDateTime"])
            end = dt_util.parse_datetime(tariff["endDateTime"])
            if start and end and start <= now < end:
                return tariff["totalAmount"]

        return None

    @property
    def native_unit_of_measurement(self) -> str:
        """Return the unit of measurement."""
        unit = self.coordinator.data[self.energy_type]["unit"]
        return f"{CURRENCY_EURO}/{unit}"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra attributes."""
        now = dt_util.now()
        tariffs = self.coordinator.data[self.energy_type]["tariffs"]

        # Find current tariff
        current_tariff = None
        for tariff in tariffs:
            start = dt_util.parse_datetime(tariff["startDateTime"])
            end = dt_util.parse_datetime(tariff["endDateTime"])
            if start and end and start <= now < end:
                current_tariff = tariff
                break

        if not current_tariff:
            return {}

        # Extract price components
        groups = {g["type"]: g["amount"] for g in current_tariff["groups"]}

        return {
            "price_ex_vat": current_tariff["totalAmountEx"],
            "vat": current_tariff["totalAmountVat"],
            "market_price": groups.get("MARKET_PRICE"),
            "purchasing_fee": groups.get("PURCHASING_FEE"),
            "tax": groups.get("TAX"),
            "start_time": current_tariff["startDateTime"],
            "end_time": current_tariff["endDateTime"],
        }
