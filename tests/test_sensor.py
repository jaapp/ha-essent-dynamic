"""Test the Essent sensors."""
from datetime import datetime
from unittest.mock import Mock, patch

from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass
from homeassistant.const import CURRENCY_EURO
from homeassistant.core import HomeAssistant

from custom_components.essent.const import ENERGY_TYPE_ELECTRICITY
from custom_components.essent.sensor import EssentCurrentPriceSensor, EssentNextPriceSensor


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
