"""Sensor platform for Essent integration."""
from __future__ import annotations

from datetime import datetime, timedelta
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
        entities.append(EssentNextPriceSensor(coordinator, energy_type))
        entities.append(EssentAveragePriceSensor(coordinator, energy_type))
        entities.append(EssentLowestPriceSensor(coordinator, energy_type))
        entities.append(EssentHighestPriceSensor(coordinator, energy_type))

    async_add_entities(entities)


class EssentCurrentPriceSensor(EssentEntity, SensorEntity):
    """Current price sensor."""

    _attr_device_class = SensorDeviceClass.MONETARY
    _attr_state_class = None  # Monetary sensors don't use state_class

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
            if start and end:
                # Ensure timezone-aware comparison
                if not start.tzinfo:
                    start = dt_util.as_local(start)
                if not end.tzinfo:
                    end = dt_util.as_local(end)
                if start <= now < end:
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

        attributes: dict[str, Any] = {}

        # Current price breakdown
        if current_tariff:
            groups = {g["type"]: g["amount"] for g in current_tariff["groups"]}
            attributes.update({
                "price_ex_vat": current_tariff["totalAmountEx"],
                "vat": current_tariff["totalAmountVat"],
                "market_price": groups.get("MARKET_PRICE"),
                "purchasing_fee": groups.get("PURCHASING_FEE"),
                "tax": groups.get("TAX"),
                "start_time": current_tariff["startDateTime"],
                "end_time": current_tariff["endDateTime"],
            })

        # Energy Dashboard integration - today's hourly prices
        today = dt_util.start_of_local_day()
        tomorrow = today + timedelta(days=1)

        today_prices = []
        tomorrow_prices = []

        for tariff in tariffs:
            start = dt_util.parse_datetime(tariff["startDateTime"])
            if not start:
                continue

            price_entry = {
                "start": tariff["startDateTime"],
                "end": tariff["endDateTime"],
                "value": tariff["totalAmount"],
            }

            if today <= start < tomorrow:
                today_prices.append(price_entry)
            elif start >= tomorrow:
                tomorrow_prices.append(price_entry)

        attributes["prices_today"] = today_prices
        if tomorrow_prices:
            attributes["prices_tomorrow"] = tomorrow_prices

        return attributes


class EssentNextPriceSensor(EssentEntity, SensorEntity):
    """Next price sensor."""

    _attr_device_class = SensorDeviceClass.MONETARY
    _attr_state_class = None  # Monetary sensors don't use state_class

    def __init__(
        self,
        coordinator: EssentDataUpdateCoordinator,
        energy_type: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, energy_type)
        self._attr_unique_id = f"{energy_type}_next_price"
        self._attr_translation_key = f"{energy_type}_next_price"

    @property
    def native_value(self) -> float | None:
        """Return the next price."""
        now = dt_util.now()
        tariffs = self.coordinator.data[self.energy_type]["tariffs"]

        for tariff in tariffs:
            start = dt_util.parse_datetime(tariff["startDateTime"])
            if start:
                # Ensure timezone-aware comparison
                if not start.tzinfo:
                    start = dt_util.as_local(start)
                if start > now:
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

        next_tariff = None
        for tariff in tariffs:
            start = dt_util.parse_datetime(tariff["startDateTime"])
            if start and start > now:
                next_tariff = tariff
                break

        if not next_tariff:
            return {}

        groups = {g["type"]: g["amount"] for g in next_tariff["groups"]}

        return {
            "price_ex_vat": next_tariff["totalAmountEx"],
            "vat": next_tariff["totalAmountVat"],
            "market_price": groups.get("MARKET_PRICE"),
            "purchasing_fee": groups.get("PURCHASING_FEE"),
            "tax": groups.get("TAX"),
            "start_time": next_tariff["startDateTime"],
            "end_time": next_tariff["endDateTime"],
        }


class EssentAveragePriceSensor(EssentEntity, SensorEntity):
    """Average price today sensor."""

    _attr_device_class = SensorDeviceClass.MONETARY
    _attr_state_class = None  # Monetary sensors don't use state_class

    def __init__(
        self,
        coordinator: EssentDataUpdateCoordinator,
        energy_type: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, energy_type)
        self._attr_unique_id = f"{energy_type}_average_today"
        self._attr_translation_key = f"{energy_type}_average_today"

    @property
    def native_value(self) -> float | None:
        """Return the average price."""
        return self.coordinator.data[self.energy_type]["avg_price"]

    @property
    def native_unit_of_measurement(self) -> str:
        """Return the unit of measurement."""
        unit = self.coordinator.data[self.energy_type]["unit"]
        return f"{CURRENCY_EURO}/{unit}"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra attributes."""
        return {
            "min_price": self.coordinator.data[self.energy_type]["min_price"],
            "max_price": self.coordinator.data[self.energy_type]["max_price"],
        }


class EssentLowestPriceSensor(EssentEntity, SensorEntity):
    """Lowest price today sensor."""

    _attr_device_class = SensorDeviceClass.MONETARY
    _attr_state_class = None  # Monetary sensors don't use state_class
    _attr_entity_registry_enabled_default = False

    def __init__(
        self,
        coordinator: EssentDataUpdateCoordinator,
        energy_type: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, energy_type)
        self._attr_unique_id = f"{energy_type}_lowest_price_today"
        self._attr_translation_key = f"{energy_type}_lowest_price_today"

    @property
    def native_value(self) -> float | None:
        """Return the lowest price."""
        return self.coordinator.data[self.energy_type]["min_price"]

    @property
    def native_unit_of_measurement(self) -> str:
        """Return the unit of measurement."""
        unit = self.coordinator.data[self.energy_type]["unit"]
        return f"{CURRENCY_EURO}/{unit}"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra attributes."""
        tariffs = self.coordinator.data[self.energy_type]["tariffs"]
        min_price = self.coordinator.data[self.energy_type]["min_price"]

        # Find tariff with minimum price
        for tariff in tariffs:
            if tariff["totalAmount"] == min_price:
                return {
                    "start": tariff["startDateTime"],
                    "end": tariff["endDateTime"],
                }

        return {}


class EssentHighestPriceSensor(EssentEntity, SensorEntity):
    """Highest price today sensor."""

    _attr_device_class = SensorDeviceClass.MONETARY
    _attr_state_class = None  # Monetary sensors don't use state_class
    _attr_entity_registry_enabled_default = False

    def __init__(
        self,
        coordinator: EssentDataUpdateCoordinator,
        energy_type: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, energy_type)
        self._attr_unique_id = f"{energy_type}_highest_price_today"
        self._attr_translation_key = f"{energy_type}_highest_price_today"

    @property
    def native_value(self) -> float | None:
        """Return the highest price."""
        return self.coordinator.data[self.energy_type]["max_price"]

    @property
    def native_unit_of_measurement(self) -> str:
        """Return the unit of measurement."""
        unit = self.coordinator.data[self.energy_type]["unit"]
        return f"{CURRENCY_EURO}/{unit}"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra attributes."""
        tariffs = self.coordinator.data[self.energy_type]["tariffs"]
        max_price = self.coordinator.data[self.energy_type]["max_price"]

        # Find tariff with maximum price
        for tariff in tariffs:
            if tariff["totalAmount"] == max_price:
                return {
                    "start": tariff["startDateTime"],
                    "end": tariff["endDateTime"],
                }

        return {}
