"""Test the Essent sensors."""
from datetime import datetime
from unittest.mock import Mock, patch

from homeassistant.components.sensor import SensorDeviceClass
from homeassistant.const import CURRENCY_EURO
from homeassistant.core import HomeAssistant
from homeassistant.util import dt as dt_util

from custom_components.essent.const import ENERGY_TYPE_ELECTRICITY
from custom_components.essent.sensor import (
    EssentAveragePriceSensor,
    EssentCurrentPriceSensor,
    EssentHighestPriceSensor,
    EssentLowestPriceSensor,
    EssentNextPriceSensor,
)


def _coordinator_from_fixture(fixture: dict) -> Mock:
    """Create a mock coordinator from a fixture payload."""
    return Mock(
        data={
            ENERGY_TYPE_ELECTRICITY: {
                "tariffs": fixture["prices"][0]["tariffs"],
                "tariffs_tomorrow": fixture["prices"][1]["tariffs"],
                "unit": fixture["prices"][0]["unit"],
                "avg_price": 0.22333333333333333,
                "min_price": 0.2,
                "max_price": 0.25,
            }
        }
    )


async def test_current_price_sensor(
    hass: HomeAssistant, electricity_api_response: dict
) -> None:
    """Test current price sensor."""
    coordinator = _coordinator_from_fixture(electricity_api_response)

    sensor = EssentCurrentPriceSensor(coordinator, ENERGY_TYPE_ELECTRICITY)

    with patch("custom_components.essent.sensor.dt_util.now") as mock_now:
        mock_now.return_value = dt_util.as_local(
            datetime.fromisoformat("2025-11-16T10:30:00")
        )

        assert sensor.native_value == 0.25  # 10:00-11:00 price
        assert sensor.native_unit_of_measurement == f"{CURRENCY_EURO}/kWh"
        assert sensor.device_class == SensorDeviceClass.MONETARY
        assert sensor.state_class is None


async def test_current_price_no_data(hass: HomeAssistant) -> None:
    """Test current price sensor with no matching tariff."""
    coordinator = Mock()
    coordinator.data = {
        "electricity": {
            "tariffs": [],
            "tariffs_tomorrow": [],
            "unit": "kWh",
        }
    }

    sensor = EssentCurrentPriceSensor(coordinator, ENERGY_TYPE_ELECTRICITY)
    assert sensor.native_value is None


async def test_next_price_sensor(
    hass: HomeAssistant, electricity_api_response: dict
) -> None:
    """Test next price sensor."""
    coordinator = _coordinator_from_fixture(electricity_api_response)

    sensor = EssentNextPriceSensor(coordinator, ENERGY_TYPE_ELECTRICITY)

    with patch("custom_components.essent.sensor.dt_util.now") as mock_now:
        mock_now.return_value = dt_util.as_local(
            datetime.fromisoformat("2025-11-16T10:30:00")
        )

        # Next hour is 11:00-12:00
        assert sensor.native_value == 0.22


async def test_next_price_sensor_uses_tomorrow(
    hass: HomeAssistant, electricity_api_response: dict
) -> None:
    """Test next price sensor falls back to tomorrow when needed."""
    coordinator = _coordinator_from_fixture(electricity_api_response)
    sensor = EssentNextPriceSensor(coordinator, ENERGY_TYPE_ELECTRICITY)

    with patch("custom_components.essent.sensor.dt_util.now") as mock_now:
        mock_now.return_value = dt_util.as_local(
            datetime.fromisoformat("2025-11-16T23:30:00")
        )

        assert sensor.native_value == 0.21  # First tariff tomorrow


async def test_average_price_sensor(
    hass: HomeAssistant, electricity_api_response: dict
) -> None:
    """Test average price sensor."""
    coordinator = _coordinator_from_fixture(electricity_api_response)

    sensor = EssentAveragePriceSensor(coordinator, ENERGY_TYPE_ELECTRICITY)

    assert round(sensor.native_value, 4) == 0.2233
    assert sensor.extra_state_attributes["min_price"] == 0.2
    assert sensor.extra_state_attributes["max_price"] == 0.25


async def test_lowest_price_sensor(
    hass: HomeAssistant, electricity_api_response: dict
) -> None:
    """Test lowest price sensor."""
    coordinator = _coordinator_from_fixture(electricity_api_response)

    sensor = EssentLowestPriceSensor(coordinator, ENERGY_TYPE_ELECTRICITY)

    assert sensor.native_value == 0.2
    assert sensor.entity_registry_enabled_default is False
    assert "2025-11-16T09:00:00" in sensor.extra_state_attributes["start"]
    assert "2025-11-16T10:00:00" in sensor.extra_state_attributes["end"]


async def test_highest_price_sensor(
    hass: HomeAssistant, electricity_api_response: dict
) -> None:
    """Test highest price sensor."""
    coordinator = _coordinator_from_fixture(electricity_api_response)

    sensor = EssentHighestPriceSensor(coordinator, ENERGY_TYPE_ELECTRICITY)

    assert sensor.native_value == 0.25
    assert sensor.entity_registry_enabled_default is False
    assert "2025-11-16T10:00:00" in sensor.extra_state_attributes["start"]
    assert "2025-11-16T11:00:00" in sensor.extra_state_attributes["end"]


async def test_current_price_energy_dashboard_attributes(
    hass: HomeAssistant, electricity_api_response: dict
) -> None:
    """Test current price sensor has Energy Dashboard attributes."""
    coordinator = _coordinator_from_fixture(electricity_api_response)

    sensor = EssentCurrentPriceSensor(coordinator, ENERGY_TYPE_ELECTRICITY)

    with patch("custom_components.essent.sensor.dt_util.now") as mock_now:
        mock_now.return_value = dt_util.as_local(
            datetime.fromisoformat("2025-11-16T10:30:00")
        )

        attrs = sensor.extra_state_attributes

        assert "prices_today" in attrs
        assert len(attrs["prices_today"]) == 3
        assert attrs["prices_today"][1]["value"] == 0.25  # Current hour price
        assert len(attrs["prices_tomorrow"]) == 2
