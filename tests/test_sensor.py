"""Test the Essent sensors."""
from datetime import datetime
from unittest.mock import Mock, patch

from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass
from homeassistant.const import CURRENCY_EURO
from homeassistant.core import HomeAssistant

from custom_components.essent.const import ENERGY_TYPE_ELECTRICITY
from custom_components.essent.sensor import (
    EssentCurrentPriceSensor,
    EssentNextPriceSensor,
    EssentAveragePriceSensor,
    EssentLowestPriceSensor,
    EssentHighestPriceSensor,
)


async def test_current_price_sensor(hass: HomeAssistant, essent_api_response) -> None:
    """Test current price sensor."""
    coordinator = Mock()
    coordinator.data = {
        "electricity": {
            "tariffs": essent_api_response["prices"][0]["electricity"]["tariffs"],
            "unit": "kWh",
            "vat_percentage": 21,
        }
    }

    sensor = EssentCurrentPriceSensor(coordinator, ENERGY_TYPE_ELECTRICITY)

    # Mock current time to match a tariff in the response (10:00-11:00)
    with patch("custom_components.essent.sensor.dt_util.now") as mock_now:
        mock_now.return_value = datetime.fromisoformat("2025-11-16T10:30:00")

        assert sensor.native_value == 0.25296  # 10:00-11:00 price
        assert sensor.native_unit_of_measurement == f"{CURRENCY_EURO}/kWh"
        assert sensor.device_class == SensorDeviceClass.MONETARY
        assert sensor.state_class == SensorStateClass.MEASUREMENT


async def test_current_price_no_data(hass: HomeAssistant) -> None:
    """Test current price sensor with no matching tariff."""
    coordinator = Mock()
    coordinator.data = {
        "electricity": {
            "tariffs": [],
            "unit": "kWh",
            "vat_percentage": 21,
        }
    }

    sensor = EssentCurrentPriceSensor(coordinator, ENERGY_TYPE_ELECTRICITY)
    assert sensor.native_value is None


async def test_next_price_sensor(hass: HomeAssistant, essent_api_response) -> None:
    """Test next price sensor."""
    coordinator = Mock()
    coordinator.data = {
        "electricity": {
            "tariffs": essent_api_response["prices"][0]["electricity"]["tariffs"],
            "unit": "kWh",
            "vat_percentage": 21,
        }
    }

    sensor = EssentNextPriceSensor(coordinator, ENERGY_TYPE_ELECTRICITY)

    with patch("custom_components.essent.sensor.dt_util.now") as mock_now:
        mock_now.return_value = datetime.fromisoformat("2025-11-16T10:30:00")

        # Next hour is 11:00-12:00
        assert sensor.native_value == 0.25704


async def test_average_price_sensor(hass: HomeAssistant, essent_api_response) -> None:
    """Test average price sensor."""
    coordinator = Mock()
    coordinator.data = {
        "electricity": {
            "tariffs": essent_api_response["prices"][0]["electricity"]["tariffs"],
            "unit": "kWh",
            "vat_percentage": 21,
            "avg_price": 0.25884625,
            "min_price": 0.24009,
            "max_price": 0.29107,
        }
    }

    sensor = EssentAveragePriceSensor(coordinator, ENERGY_TYPE_ELECTRICITY)

    assert sensor.native_value == 0.25884625
    assert sensor.extra_state_attributes["min_price"] == 0.24009
    assert sensor.extra_state_attributes["max_price"] == 0.29107


async def test_lowest_price_sensor(hass: HomeAssistant, essent_api_response) -> None:
    """Test lowest price sensor."""
    coordinator = Mock()
    coordinator.data = {
        "electricity": {
            "tariffs": essent_api_response["prices"][0]["electricity"]["tariffs"],
            "unit": "kWh",
            "vat_percentage": 21,
            "min_price": 0.24009,
        }
    }

    sensor = EssentLowestPriceSensor(coordinator, ENERGY_TYPE_ELECTRICITY)

    assert sensor.native_value == 0.24009
    assert sensor.entity_registry_enabled_default is False
    # Lowest price is at 06:00-07:00 based on fixture
    assert "2025-11-16T06:00:00" in sensor.extra_state_attributes["start"]
    assert "2025-11-16T07:00:00" in sensor.extra_state_attributes["end"]


async def test_highest_price_sensor(hass: HomeAssistant, essent_api_response) -> None:
    """Test highest price sensor."""
    coordinator = Mock()
    coordinator.data = {
        "electricity": {
            "tariffs": essent_api_response["prices"][0]["electricity"]["tariffs"],
            "unit": "kWh",
            "vat_percentage": 21,
            "max_price": 0.29107,
        }
    }

    sensor = EssentHighestPriceSensor(coordinator, ENERGY_TYPE_ELECTRICITY)

    assert sensor.native_value == 0.29107
    assert sensor.entity_registry_enabled_default is False
    # Highest price is at 17:00-18:00 based on fixture
    assert "2025-11-16T17:00:00" in sensor.extra_state_attributes["start"]
    assert "2025-11-16T18:00:00" in sensor.extra_state_attributes["end"]


async def test_current_price_energy_dashboard_attributes(
    hass: HomeAssistant, essent_api_response
) -> None:
    """Test current price sensor has Energy Dashboard attributes."""
    coordinator = Mock()
    coordinator.data = {
        "electricity": {
            "tariffs": essent_api_response["prices"][0]["electricity"]["tariffs"],
            "unit": "kWh",
            "vat_percentage": 21,
        }
    }

    sensor = EssentCurrentPriceSensor(coordinator, ENERGY_TYPE_ELECTRICITY)

    with patch("custom_components.essent.sensor.dt_util.now") as mock_now:
        mock_now.return_value = datetime.fromisoformat("2025-11-16T10:30:00")

        attrs = sensor.extra_state_attributes

        # Should have today's prices for Energy Dashboard
        assert "prices_today" in attrs
        assert len(attrs["prices_today"]) == 24
        assert attrs["prices_today"][0]["value"] == 0.25353  # First hour price
