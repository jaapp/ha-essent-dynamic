# Essent Home Assistant Integration Implementation Plan

> **For Claude:** Use `${SUPERPOWERS_SKILLS_ROOT}/skills/collaboration/executing-plans/SKILL.md` to implement this plan task-by-task.

**Goal:** Build a Home Assistant integration that fetches dynamic electricity and gas prices from Essent's public API and exposes them as sensors for the Energy Dashboard.

**Architecture:** DataUpdateCoordinator pattern with hourly polling of Essent API endpoint. Single coordinator manages both electricity and gas data. Ten sensor entities (5 per energy type) calculate current/next/average/min/max prices from coordinator data. Follows Home Assistant core quality standards (Nordpool platinum reference).

**Tech Stack:** Python 3.12+, Home Assistant Core patterns (DataUpdateCoordinator, ConfigFlow), aiohttp for async HTTP, pytest for testing.

---

## Task 1: Project Structure & Constants

**Files:**
- Create: `custom_components/essent/__init__.py`
- Create: `custom_components/essent/manifest.json`
- Create: `custom_components/essent/const.py`
- Create: `tests/conftest.py`
- Create: `tests/fixtures/essent_api_response.json`

**Step 1: Create basic directory structure**

```bash
mkdir -p custom_components/essent
mkdir -p tests/fixtures
```

**Step 2: Write manifest.json**

Create `custom_components/essent/manifest.json`:

```json
{
  "domain": "essent",
  "name": "Essent",
  "codeowners": ["@jwpieroen"],
  "config_flow": true,
  "documentation": "https://github.com/jwpieroen/essent-ha-integration",
  "iot_class": "cloud_polling",
  "requirements": [],
  "version": "1.0.0"
}
```

**Step 3: Write constants file**

Create `custom_components/essent/const.py`:

```python
"""Constants for the Essent integration."""

DOMAIN = "essent"
API_ENDPOINT = "https://www.essent.nl/api/public/tariffmanagement/dynamic-prices/v1/"
UPDATE_INTERVAL = 3600  # 1 hour in seconds
ATTRIBUTION = "Data provided by Essent"

# Energy types
ENERGY_TYPE_ELECTRICITY = "electricity"
ENERGY_TYPE_GAS = "gas"

# Price group types
PRICE_GROUP_MARKET = "MARKET_PRICE"
PRICE_GROUP_PURCHASING_FEE = "PURCHASING_FEE"
PRICE_GROUP_TAX = "TAX"
```

**Step 4: Create API response fixture**

Create `tests/fixtures/essent_api_response.json` with the sample data from your HAR file (electricity and gas data for 2025-11-15).

**Step 5: Create pytest conftest**

Create `tests/conftest.py`:

```python
"""Test fixtures for Essent integration."""
import json
from pathlib import Path
import pytest


@pytest.fixture
def essent_api_response():
    """Load sample API response."""
    fixture_path = Path(__file__).parent / "fixtures" / "essent_api_response.json"
    with open(fixture_path) as f:
        return json.load(f)
```

**Step 6: Create minimal __init__.py**

Create `custom_components/essent/__init__.py`:

```python
"""The Essent integration."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

PLATFORMS = ["sensor"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Essent from a config entry."""
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
```

**Step 7: Commit**

```bash
git add custom_components/ tests/ docs/
git commit -m "feat: add project structure and constants

Initialize Essent integration with manifest, constants, and test fixtures.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 2: Configuration Flow

**Files:**
- Create: `custom_components/essent/config_flow.py`
- Create: `custom_components/essent/strings.json`
- Create: `tests/test_config_flow.py`

**Step 1: Write failing test for config flow**

Create `tests/test_config_flow.py`:

```python
"""Test the Essent config flow."""
from unittest.mock import patch

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

from custom_components.essent.const import DOMAIN


async def test_form(hass: HomeAssistant) -> None:
    """Test we get the form."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] == FlowResultType.FORM
    assert result["errors"] == {}

    with patch(
        "custom_components.essent.async_setup_entry",
        return_value=True,
    ):
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {},
        )
        await hass.async_block_till_done()

    assert result2["type"] == FlowResultType.CREATE_ENTRY
    assert result2["title"] == "Essent"
    assert result2["data"] == {}
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_config_flow.py -v`
Expected: FAIL with "No module named 'custom_components.essent.config_flow'"

**Step 3: Write minimal config flow implementation**

Create `custom_components/essent/config_flow.py`:

```python
"""Config flow for Essent integration."""
from __future__ import annotations

from typing import Any

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult

from .const import DOMAIN


class EssentConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Essent."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        if user_input is not None:
            await self.async_set_unique_id("essent_dynamic_prices")
            self._abort_if_unique_id_configured()
            return self.async_create_entry(title="Essent", data={})

        return self.async_show_form(step_id="user")
```

**Step 4: Create strings.json**

Create `custom_components/essent/strings.json`:

```json
{
  "config": {
    "step": {
      "user": {
        "title": "Essent Dynamic Energy Prices",
        "description": "Set up Essent energy price monitoring for the Netherlands."
      }
    },
    "abort": {
      "already_configured": "Essent integration is already configured"
    }
  }
}
```

**Step 5: Run test to verify it passes**

Run: `pytest tests/test_config_flow.py -v`
Expected: PASS

**Step 6: Commit**

```bash
git add custom_components/essent/config_flow.py custom_components/essent/strings.json tests/test_config_flow.py
git commit -m "feat: add config flow

Add simple config flow with no required configuration (API is public).

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 3: Data Coordinator

**Files:**
- Create: `custom_components/essent/coordinator.py`
- Create: `tests/test_coordinator.py`

**Step 1: Write failing test for coordinator data fetch**

Create `tests/test_coordinator.py`:

```python
"""Test the Essent coordinator."""
from datetime import timedelta
from unittest.mock import AsyncMock, patch

import pytest
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import UpdateFailed
from homeassistant.util import dt as dt_util

from custom_components.essent.coordinator import EssentDataUpdateCoordinator
from custom_components.essent.const import UPDATE_INTERVAL


async def test_coordinator_fetch_success(hass: HomeAssistant, essent_api_response) -> None:
    """Test successful data fetch."""
    coordinator = EssentDataUpdateCoordinator(hass)

    with patch("aiohttp.ClientSession.get") as mock_get:
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value=essent_api_response)
        mock_get.return_value.__aenter__.return_value = mock_response

        await coordinator.async_config_entry_first_refresh()

    assert coordinator.data is not None
    assert "electricity" in coordinator.data
    assert "gas" in coordinator.data
    assert len(coordinator.data["electricity"]["tariffs"]) == 24
    assert len(coordinator.data["gas"]["tariffs"]) == 24


async def test_coordinator_fetch_failure(hass: HomeAssistant) -> None:
    """Test failed data fetch."""
    coordinator = EssentDataUpdateCoordinator(hass)

    with patch("aiohttp.ClientSession.get") as mock_get:
        mock_response = AsyncMock()
        mock_response.status = 500
        mock_get.return_value.__aenter__.return_value = mock_response

        with pytest.raises(UpdateFailed):
            await coordinator.async_config_entry_first_refresh()
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_coordinator.py -v`
Expected: FAIL with "No module named 'custom_components.essent.coordinator'"

**Step 3: Write minimal coordinator implementation**

Create `custom_components/essent/coordinator.py`:

```python
"""DataUpdateCoordinator for Essent integration."""
from datetime import timedelta
import logging

import aiohttp

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import API_ENDPOINT, DOMAIN, UPDATE_INTERVAL

_LOGGER = logging.getLogger(__name__)


class EssentDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Essent data."""

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=UPDATE_INTERVAL),
        )

    async def _async_update_data(self) -> dict:
        """Fetch data from API."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(API_ENDPOINT, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status != 200:
                        raise UpdateFailed(f"Error fetching data: {response.status}")

                    data = await response.json()

                    return {
                        "electricity": {
                            "tariffs": data["electricity"]["tariffs"],
                            "unit": data["electricity"]["unitOfMeasurement"],
                            "vat_percentage": data["electricity"]["vatPercentage"],
                            "min_price": data["electricity"]["minAmount"],
                            "avg_price": data["electricity"]["averageAmount"],
                            "max_price": data["electricity"]["maxAmount"],
                        },
                        "gas": {
                            "tariffs": data["gas"]["tariffs"],
                            "unit": data["gas"]["unitOfMeasurement"],
                            "vat_percentage": data["gas"]["vatPercentage"],
                            "min_price": data["gas"]["minAmount"],
                            "avg_price": data["gas"]["averageAmount"],
                            "max_price": data["gas"]["maxAmount"],
                        },
                    }
        except aiohttp.ClientError as err:
            raise UpdateFailed(f"Error communicating with API: {err}") from err
        except KeyError as err:
            raise UpdateFailed(f"Invalid data received from API: {err}") from err
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_coordinator.py -v`
Expected: PASS

**Step 5: Update __init__.py to create coordinator**

Modify `custom_components/essent/__init__.py`:

```python
"""The Essent integration."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .coordinator import EssentDataUpdateCoordinator

PLATFORMS = ["sensor"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Essent from a config entry."""
    coordinator = EssentDataUpdateCoordinator(hass)
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
```

**Step 6: Commit**

```bash
git add custom_components/essent/coordinator.py custom_components/essent/__init__.py tests/test_coordinator.py
git commit -m "feat: add data coordinator

Implement DataUpdateCoordinator with hourly API polling and error handling.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 4: Base Sensor Entity

**Files:**
- Create: `custom_components/essent/entity.py`
- Create: `tests/test_entity.py`

**Step 1: Write failing test for base entity**

Create `tests/test_entity.py`:

```python
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
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_entity.py -v`
Expected: FAIL with "No module named 'custom_components.essent.entity'"

**Step 3: Write base entity implementation**

Create `custom_components/essent/entity.py`:

```python
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
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_entity.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add custom_components/essent/entity.py tests/test_entity.py
git commit -m "feat: add base entity class

Add CoordinatorEntity base class with device info.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 5: Current Price Sensor

**Files:**
- Create: `custom_components/essent/sensor.py`
- Create: `tests/test_sensor.py`

**Step 1: Write failing test for current price sensor**

Create `tests/test_sensor.py`:

```python
"""Test the Essent sensors."""
from datetime import datetime
from unittest.mock import Mock, patch

from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass
from homeassistant.const import CURRENCY_EURO
from homeassistant.core import HomeAssistant

from custom_components.essent.const import ENERGY_TYPE_ELECTRICITY
from custom_components.essent.sensor import EssentCurrentPriceSensor


async def test_current_price_sensor(hass: HomeAssistant, essent_api_response) -> None:
    """Test current price sensor."""
    coordinator = Mock()
    coordinator.data = {
        "electricity": {
            "tariffs": essent_api_response["electricity"]["tariffs"],
            "unit": "kWh",
            "vat_percentage": 21,
        }
    }

    sensor = EssentCurrentPriceSensor(coordinator, ENERGY_TYPE_ELECTRICITY)

    # Mock current time to match a tariff in the response
    with patch("custom_components.essent.sensor.dt_util.now") as mock_now:
        mock_now.return_value = datetime.fromisoformat("2025-11-15T10:30:00")

        assert sensor.native_value == 0.25329  # 10:00-11:00 price
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
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_sensor.py::test_current_price_sensor -v`
Expected: FAIL with "No module named 'custom_components.essent.sensor'"

**Step 3: Write current price sensor implementation**

Create `custom_components/essent/sensor.py`:

```python
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
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_sensor.py -v`
Expected: PASS

**Step 5: Update strings.json with sensor names**

Modify `custom_components/essent/strings.json`:

```json
{
  "config": {
    "step": {
      "user": {
        "title": "Essent Dynamic Energy Prices",
        "description": "Set up Essent energy price monitoring for the Netherlands."
      }
    },
    "abort": {
      "already_configured": "Essent integration is already configured"
    }
  },
  "entity": {
    "sensor": {
      "electricity_current_price": {
        "name": "Electricity current price"
      },
      "gas_current_price": {
        "name": "Gas current price"
      }
    }
  }
}
```

**Step 6: Commit**

```bash
git add custom_components/essent/sensor.py custom_components/essent/strings.json tests/test_sensor.py
git commit -m "feat: add current price sensors

Add current price sensors for electricity and gas with price breakdown attributes.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 6: Next Price Sensor

**Files:**
- Modify: `custom_components/essent/sensor.py`
- Modify: `tests/test_sensor.py`
- Modify: `custom_components/essent/strings.json`

**Step 1: Write failing test for next price sensor**

Add to `tests/test_sensor.py`:

```python
from custom_components.essent.sensor import EssentNextPriceSensor


async def test_next_price_sensor(hass: HomeAssistant, essent_api_response) -> None:
    """Test next price sensor."""
    coordinator = Mock()
    coordinator.data = {
        "electricity": {
            "tariffs": essent_api_response["electricity"]["tariffs"],
            "unit": "kWh",
            "vat_percentage": 21,
        }
    }

    sensor = EssentNextPriceSensor(coordinator, ENERGY_TYPE_ELECTRICITY)

    with patch("custom_components.essent.sensor.dt_util.now") as mock_now:
        mock_now.return_value = datetime.fromisoformat("2025-11-15T10:30:00")

        # Next hour is 11:00-12:00
        assert sensor.native_value == 0.25439
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_sensor.py::test_next_price_sensor -v`
Expected: FAIL

**Step 3: Add next price sensor to sensor.py**

Add to `custom_components/essent/sensor.py`:

```python
# In async_setup_entry, add:
        entities.append(EssentNextPriceSensor(coordinator, energy_type))


class EssentNextPriceSensor(EssentEntity, SensorEntity):
    """Next price sensor."""

    _attr_device_class = SensorDeviceClass.MONETARY
    _attr_state_class = SensorStateClass.MEASUREMENT

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
            if start and start > now:
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
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_sensor.py::test_next_price_sensor -v`
Expected: PASS

**Step 5: Update strings.json**

Add to `custom_components/essent/strings.json` entity.sensor section:

```json
      "electricity_next_price": {
        "name": "Electricity next price"
      },
      "gas_next_price": {
        "name": "Gas next price"
      }
```

**Step 6: Commit**

```bash
git add custom_components/essent/sensor.py custom_components/essent/strings.json tests/test_sensor.py
git commit -m "feat: add next price sensors

Add next price sensors for electricity and gas.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 7: Average Price Sensor

**Files:**
- Modify: `custom_components/essent/sensor.py`
- Modify: `tests/test_sensor.py`
- Modify: `custom_components/essent/strings.json`

**Step 1: Write failing test for average price sensor**

Add to `tests/test_sensor.py`:

```python
from custom_components.essent.sensor import EssentAveragePriceSensor


async def test_average_price_sensor(hass: HomeAssistant, essent_api_response) -> None:
    """Test average price sensor."""
    coordinator = Mock()
    coordinator.data = {
        "electricity": {
            "tariffs": essent_api_response["electricity"]["tariffs"],
            "unit": "kWh",
            "vat_percentage": 21,
            "avg_price": 0.24857083333333332,
            "min_price": 0.21903,
            "max_price": 0.28458,
        }
    }

    sensor = EssentAveragePriceSensor(coordinator, ENERGY_TYPE_ELECTRICITY)

    assert sensor.native_value == 0.24857083333333332
    assert sensor.extra_state_attributes["min_price"] == 0.21903
    assert sensor.extra_state_attributes["max_price"] == 0.28458
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_sensor.py::test_average_price_sensor -v`
Expected: FAIL

**Step 3: Add average price sensor to sensor.py**

Add to `custom_components/essent/sensor.py`:

```python
# In async_setup_entry, add:
        entities.append(EssentAveragePriceSensor(coordinator, energy_type))


class EssentAveragePriceSensor(EssentEntity, SensorEntity):
    """Average price today sensor."""

    _attr_device_class = SensorDeviceClass.MONETARY
    _attr_state_class = SensorStateClass.MEASUREMENT

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
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_sensor.py::test_average_price_sensor -v`
Expected: PASS

**Step 5: Update strings.json**

Add to entity.sensor section:

```json
      "electricity_average_today": {
        "name": "Electricity average today"
      },
      "gas_average_today": {
        "name": "Gas average today"
      }
```

**Step 6: Commit**

```bash
git add custom_components/essent/sensor.py custom_components/essent/strings.json tests/test_sensor.py
git commit -m "feat: add average price sensors

Add average price sensors with min/max attributes.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 8: Min/Max Price Sensors (Disabled by Default)

**Files:**
- Modify: `custom_components/essent/sensor.py`
- Modify: `tests/test_sensor.py`
- Modify: `custom_components/essent/strings.json`

**Step 1: Write failing test for min/max price sensors**

Add to `tests/test_sensor.py`:

```python
from homeassistant.helpers.entity import EntityCategory

from custom_components.essent.sensor import (
    EssentLowestPriceSensor,
    EssentHighestPriceSensor,
)


async def test_lowest_price_sensor(hass: HomeAssistant, essent_api_response) -> None:
    """Test lowest price sensor."""
    coordinator = Mock()
    coordinator.data = {
        "electricity": {
            "tariffs": essent_api_response["electricity"]["tariffs"],
            "unit": "kWh",
            "vat_percentage": 21,
            "min_price": 0.21903,
        }
    }

    sensor = EssentLowestPriceSensor(coordinator, ENERGY_TYPE_ELECTRICITY)

    assert sensor.native_value == 0.21903
    assert sensor.entity_registry_enabled_default is False
    # Lowest price is at 06:00-07:00 based on fixture
    assert "2025-11-15T06:00:00" in sensor.extra_state_attributes["start"]
    assert "2025-11-15T07:00:00" in sensor.extra_state_attributes["end"]


async def test_highest_price_sensor(hass: HomeAssistant, essent_api_response) -> None:
    """Test highest price sensor."""
    coordinator = Mock()
    coordinator.data = {
        "electricity": {
            "tariffs": essent_api_response["electricity"]["tariffs"],
            "unit": "kWh",
            "vat_percentage": 21,
            "max_price": 0.28458,
        }
    }

    sensor = EssentHighestPriceSensor(coordinator, ENERGY_TYPE_ELECTRICITY)

    assert sensor.native_value == 0.28458
    assert sensor.entity_registry_enabled_default is False
    # Highest price is at 18:00-19:00 based on fixture
    assert "2025-11-15T18:00:00" in sensor.extra_state_attributes["start"]
    assert "2025-11-15T19:00:00" in sensor.extra_state_attributes["end"]
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_sensor.py::test_lowest_price_sensor -v`
Expected: FAIL

**Step 3: Add min/max sensors to sensor.py**

Add to `custom_components/essent/sensor.py`:

```python
# In async_setup_entry, add:
        entities.append(EssentLowestPriceSensor(coordinator, energy_type))
        entities.append(EssentHighestPriceSensor(coordinator, energy_type))


class EssentLowestPriceSensor(EssentEntity, SensorEntity):
    """Lowest price today sensor."""

    _attr_device_class = SensorDeviceClass.MONETARY
    _attr_state_class = SensorStateClass.MEASUREMENT
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
    _attr_state_class = SensorStateClass.MEASUREMENT
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
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_sensor.py -v`
Expected: PASS (all tests)

**Step 5: Update strings.json**

Add to entity.sensor section:

```json
      "electricity_lowest_price_today": {
        "name": "Electricity lowest price today"
      },
      "gas_lowest_price_today": {
        "name": "Gas lowest price today"
      },
      "electricity_highest_price_today": {
        "name": "Electricity highest price today"
      },
      "gas_highest_price_today": {
        "name": "Gas highest price today"
      }
```

**Step 6: Commit**

```bash
git add custom_components/essent/sensor.py custom_components/essent/strings.json tests/test_sensor.py
git commit -m "feat: add min/max price sensors

Add lowest and highest price sensors (disabled by default) with time window attributes.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 9: Energy Dashboard Integration Attributes

**Files:**
- Modify: `custom_components/essent/sensor.py`
- Modify: `tests/test_sensor.py`

**Step 1: Write test for Energy Dashboard attributes**

Add to `tests/test_sensor.py`:

```python
async def test_current_price_energy_dashboard_attributes(
    hass: HomeAssistant, essent_api_response
) -> None:
    """Test current price sensor has Energy Dashboard attributes."""
    coordinator = Mock()
    coordinator.data = {
        "electricity": {
            "tariffs": essent_api_response["electricity"]["tariffs"],
            "unit": "kWh",
            "vat_percentage": 21,
        }
    }

    sensor = EssentCurrentPriceSensor(coordinator, ENERGY_TYPE_ELECTRICITY)

    with patch("custom_components.essent.sensor.dt_util.now") as mock_now:
        mock_now.return_value = datetime.fromisoformat("2025-11-15T10:30:00")

        attrs = sensor.extra_state_attributes

        # Should have today's prices for Energy Dashboard
        assert "prices_today" in attrs
        assert len(attrs["prices_today"]) == 24
        assert attrs["prices_today"][0]["value"] == 0.23103  # First hour price
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_sensor.py::test_current_price_energy_dashboard_attributes -v`
Expected: FAIL

**Step 3: Add Energy Dashboard attributes to current price sensor**

Modify `EssentCurrentPriceSensor.extra_state_attributes` in `sensor.py`:

```python
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
```

**Step 4: Add missing import**

Add to top of `sensor.py`:

```python
from datetime import timedelta
```

**Step 5: Run test to verify it passes**

Run: `pytest tests/test_sensor.py::test_current_price_energy_dashboard_attributes -v`
Expected: PASS

**Step 6: Commit**

```bash
git add custom_components/essent/sensor.py tests/test_sensor.py
git commit -m "feat: add Energy Dashboard attributes

Add prices_today and prices_tomorrow attributes for Energy Dashboard integration.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 10: Documentation

**Files:**
- Create: `README.md`
- Create: `docs/INSTALLATION.md`
- Create: `docs/ENERGY_DASHBOARD.md`

**Step 1: Create README**

Create `README.md`:

```markdown
# Essent Home Assistant Integration

Home Assistant integration for Essent dynamic energy prices in the Netherlands.

## Features

- Real-time electricity and gas prices
- Hourly price updates
- Current, next, and average price sensors
- Min/max daily price tracking
- Full Energy Dashboard integration
- No authentication required (public API)

## Installation

See [Installation Guide](docs/INSTALLATION.md)

## Energy Dashboard Setup

See [Energy Dashboard Guide](docs/ENERGY_DASHBOARD.md)

## Sensors

### Enabled by Default

- **Current Price** (electricity/gas): Current hour's energy price
- **Next Price** (electricity/gas): Next hour's energy price
- **Average Today** (electricity/gas): Average price for current day

### Disabled by Default

- **Lowest Price Today** (electricity/gas): Minimum price with time window
- **Highest Price Today** (electricity/gas): Maximum price with time window

## Price Components

Each price sensor includes detailed attributes:
- `price_ex_vat`: Price excluding VAT
- `vat`: VAT amount
- `market_price`: Spot market price component
- `purchasing_fee`: Supplier purchasing fee
- `tax`: Energy tax component

## Energy Dashboard Integration

Current price sensors include `prices_today` and `prices_tomorrow` attributes with hourly price data formatted for Home Assistant Energy Dashboard.

## Data Source

Prices are fetched from Essent's public API:
`https://www.essent.nl/api/public/tariffmanagement/dynamic-prices/v1/`

Data updates hourly. Tomorrow's prices typically available after 13:00 CET.

## License

MIT License
```

**Step 2: Create installation guide**

Create `docs/INSTALLATION.md`:

```markdown
# Installation Guide

## HACS Installation (Recommended)

1. Open HACS in Home Assistant
2. Click on "Integrations"
3. Click the three dots in the top right corner
4. Select "Custom repositories"
5. Add repository URL: `https://github.com/jwpieroen/essent-ha-integration`
6. Select category: "Integration"
7. Click "Add"
8. Click "Install" on the Essent integration
9. Restart Home Assistant

## Manual Installation

1. Copy the `custom_components/essent` directory to your `config/custom_components` folder
2. Restart Home Assistant
3. Go to Settings → Devices & Services
4. Click "+ Add Integration"
5. Search for "Essent"
6. Click to add

## Configuration

No configuration required! The integration uses Essent's public API.

## Verification

After installation, you should see 6 enabled sensors:
- `sensor.essent_electricity_current_price`
- `sensor.essent_electricity_next_price`
- `sensor.essent_electricity_average_today`
- `sensor.essent_gas_current_price`
- `sensor.essent_gas_next_price`
- `sensor.essent_gas_average_today`

And 4 disabled sensors (can be enabled in entity settings):
- `sensor.essent_electricity_lowest_price_today`
- `sensor.essent_electricity_highest_price_today`
- `sensor.essent_gas_lowest_price_today`
- `sensor.essent_gas_highest_price_today`
```

**Step 3: Create Energy Dashboard guide**

Create `docs/ENERGY_DASHBOARD.md`:

```markdown
# Energy Dashboard Integration

The Essent integration provides full support for Home Assistant's Energy Dashboard.

## Setup

### 1. Add Energy Source

1. Go to Settings → Dashboards → Energy
2. Click "Add Consumption" under Electricity or Gas grid consumption
3. Select your energy meter entity
4. Under "Use an entity with current price":
   - For electricity: Select `sensor.essent_electricity_current_price`
   - For gas: Select `sensor.essent_gas_current_price`
5. Save

### 2. Price Data

The current price sensors automatically provide:
- **Current hour price**: Used for real-time cost calculation
- **Today's hourly prices**: Available via `prices_today` attribute
- **Tomorrow's prices**: Available via `prices_tomorrow` attribute (after ~13:00 CET)

### 3. Historical Cost Tracking

The Energy Dashboard will automatically:
- Track hourly energy costs
- Display daily/monthly/yearly cost breakdowns
- Show cost trends over time
- Compare current vs historical prices

## Advanced Usage

### Creating Automations

Use price sensors to optimize energy consumption:

```yaml
automation:
  - alias: "Charge battery when cheap"
    trigger:
      - platform: numeric_state
        entity_id: sensor.essent_electricity_current_price
        below: 0.20
    action:
      - service: switch.turn_on
        target:
          entity_id: switch.battery_charger
```

### Template Sensors

Calculate custom metrics:

```yaml
template:
  - sensor:
      - name: "Price vs Average"
        unit_of_measurement: "%"
        state: >
          {% set current = states('sensor.essent_electricity_current_price') | float %}
          {% set avg = states('sensor.essent_electricity_average_today') | float %}
          {{ ((current - avg) / avg * 100) | round(1) }}
```

## Troubleshooting

### Prices not showing in Energy Dashboard

1. Verify sensors are available and have values
2. Check sensor state class is `measurement`
3. Ensure unit of measurement is `EUR/kWh` or `EUR/m³`
4. Restart Home Assistant

### Tomorrow's prices missing

Tomorrow's prices are published around 13:00 CET each day. Before this time, the `prices_tomorrow` attribute will be empty or missing. This is normal behavior.
```

**Step 4: Commit documentation**

```bash
git add README.md docs/
git commit -m "docs: add comprehensive documentation

Add README, installation guide, and Energy Dashboard integration guide.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 11: Add HACS Support

**Files:**
- Create: `hacs.json`
- Create: `.github/workflows/validate.yml`

**Step 1: Create HACS manifest**

Create `hacs.json`:

```json
{
  "name": "Essent",
  "content_in_root": false,
  "filename": "essent",
  "render_readme": true,
  "homeassistant": "2024.1.0"
}
```

**Step 2: Create GitHub Actions workflow for validation**

Create `.github/workflows/validate.yml`:

```yaml
name: Validate

on:
  push:
  pull_request:

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: HACS validation
        uses: hacs/action@main
        with:
          category: integration
```

**Step 3: Commit HACS support**

```bash
git add hacs.json .github/
git commit -m "feat: add HACS support

Add HACS manifest and GitHub Actions validation workflow.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 12: Final Integration Testing

**Files:**
- Create: `tests/test_integration.py`

**Step 1: Write integration test**

Create `tests/test_integration.py`:

```python
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
```

**Step 2: Run full test suite**

Run: `pytest tests/ -v --cov=custom_components.essent --cov-report=term-missing`

**Step 3: Fix any failing tests**

Address any test failures before proceeding.

**Step 4: Commit integration test**

```bash
git add tests/test_integration.py
git commit -m "test: add full integration test

Add end-to-end integration test covering setup, sensors, and teardown.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Post-Implementation Checklist

After completing all tasks:

1. ✅ Run full test suite: `pytest tests/ -v`
2. ✅ Verify all 10 sensors are created
3. ✅ Test in development Home Assistant instance
4. ✅ Verify Energy Dashboard integration
5. ✅ Check tomorrow's prices appear after 13:00 CET
6. ✅ Review code for YAGNI violations
7. ✅ Verify all commits follow conventional commits
8. ✅ Push to GitHub
9. ✅ Test HACS installation
10. ✅ Update README with any findings

## Notes

- All times are handled in local timezone using `dt_util`
- API endpoint requires no authentication
- Price data updates hourly
- Tomorrow's data available after ~13:00 CET
- Integration follows Home Assistant core quality standards
- Uses Nordpool integration as reference (platinum standard)
