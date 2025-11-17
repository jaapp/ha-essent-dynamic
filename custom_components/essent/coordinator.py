"""DataUpdateCoordinator for Essent integration."""
from datetime import timedelta
import logging
from typing import Any

import aiohttp

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    API_ENDPOINT,
    DOMAIN,
    UPDATE_INTERVAL,
)

_LOGGER = logging.getLogger(__name__)


def _tariff_sort_key(tariff: dict[str, Any]) -> str:
    """Sort key for tariffs based on start time."""
    return tariff.get("startDateTime", "")


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

    def _normalize_energy_block(self, data: dict[str, Any], energy_type: str) -> dict[str, Any]:
        """Normalize the energy block into the coordinator format."""
        tariffs_today = sorted(
            data.get("tariffs", []),
            key=_tariff_sort_key,
        )
        if not tariffs_today:
            _LOGGER.debug("No tariffs found for %s in payload: %s", energy_type, data)
            raise UpdateFailed(f"No tariffs found for {energy_type}")

        tariffs_tomorrow: list[dict[str, Any]] = []
        unit = data.get("unitOfMeasurement") or data.get("unit")

        amounts = [
            tariff["totalAmount"]
            for tariff in tariffs_today
            if "totalAmount" in tariff
        ]
        if not amounts:
            _LOGGER.debug(
                "No usable totalAmount values for %s in tariffs: %s",
                energy_type,
                tariffs_today,
            )
            raise UpdateFailed(f"No usable tariff values for {energy_type}")

        if not unit:
            _LOGGER.debug("No unit provided for %s in payload: %s", energy_type, data)
            raise UpdateFailed(f"No unit provided for {energy_type}")

        return {
            "tariffs": tariffs_today,
            "tariffs_tomorrow": tariffs_tomorrow,
            "unit": unit,
            "min_price": min(amounts),
            "avg_price": sum(amounts) / len(amounts),
            "max_price": max(amounts),
        }

    async def _async_update_data(self) -> dict:
        """Fetch data from API."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    API_ENDPOINT,
                    timeout=aiohttp.ClientTimeout(total=10),
                    headers={"Accept": "application/json"},
                ) as response:
                    raw_body = await response.text()
                    if response.status != 200:
                        _LOGGER.debug(
                            "Essent API %s returned %s with body: %s",
                            API_ENDPOINT,
                            response.status,
                            raw_body,
                        )
                        raise UpdateFailed(f"Error fetching data: {response.status}")

                    try:
                        data = await response.json()
                    except Exception as err:
                        _LOGGER.debug(
                            "Failed to decode JSON body: %s", raw_body
                        )
                        raise UpdateFailed(f"Invalid JSON received: {err}") from err

            prices = data.get("prices") or []
            if not prices:
                _LOGGER.debug("No price data available in response: %s", data)
                raise UpdateFailed("No price data available")

            today = prices[0]
            electricity_block = today.get("electricity")
            gas_block = today.get("gas")

            if not electricity_block or not gas_block:
                _LOGGER.debug(
                    "Missing electricity or gas block in payload: %s", today
                )
                raise UpdateFailed("Response missing electricity or gas data")

            return {
                "electricity": self._normalize_energy_block(
                    electricity_block, "electricity"
                ),
                "gas": self._normalize_energy_block(
                    gas_block, "gas"
                ),
            }
        except aiohttp.ClientError as err:
            raise UpdateFailed(f"Error communicating with API: {err}") from err
        except KeyError as err:
            raise UpdateFailed(f"Invalid data received from API: {err}") from err
