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
    ENERGY_TYPE_ELECTRICITY,
    ENERGY_TYPE_GAS,
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

    async def _fetch_energy_type(
        self, session: aiohttp.ClientSession, energy_type: str
    ) -> dict[str, Any]:
        """Fetch data for a specific energy type."""
        url = f"{API_ENDPOINT}{energy_type}"
        async with session.get(
            url, timeout=aiohttp.ClientTimeout(total=10), headers={"Accept": "application/json"}
        ) as response:
            raw_body = await response.text()
            if response.status != 200:
                _LOGGER.debug(
                    "Essent API %s returned %s with body: %s",
                    url,
                    response.status,
                    raw_body,
                )
                raise UpdateFailed(
                    f"Error fetching {energy_type} data: {response.status}"
                )

            try:
                data = await response.json()
            except Exception as err:
                _LOGGER.debug(
                    "Failed to decode JSON for %s, body: %s", energy_type, raw_body
                )
                raise UpdateFailed(
                    f"Invalid JSON received for {energy_type}: {err}"
                ) from err

        prices = data.get("prices") or []
        if not prices:
            _LOGGER.debug("No price data available in response for %s: %s", energy_type, data)
            raise UpdateFailed(f"No price data available for {energy_type}")

        today_data = prices[0]
        tariffs_today = sorted(today_data.get("tariffs", []), key=_tariff_sort_key)
        tariffs_tomorrow = []
        if len(prices) > 1:
            tariffs_tomorrow = sorted(
                prices[1].get("tariffs", []), key=_tariff_sort_key
            )

        if not tariffs_today:
            _LOGGER.debug("No tariffs found for %s in payload: %s", energy_type, today_data)
            raise UpdateFailed(f"No tariffs found for {energy_type}")

        amounts = [tariff["totalAmount"] for tariff in tariffs_today if "totalAmount" in tariff]
        if not amounts:
            _LOGGER.debug("No usable tariff values for %s in tariffs: %s", energy_type, tariffs_today)
            raise UpdateFailed(f"No usable tariff values for {energy_type}")

        unit = today_data.get("unit") or today_data.get("unitOfMeasurement")
        if not unit:
            _LOGGER.debug("No unit provided for %s in payload: %s", energy_type, today_data)
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
                electricity = await self._fetch_energy_type(
                    session, ENERGY_TYPE_ELECTRICITY
                )
                gas = await self._fetch_energy_type(session, ENERGY_TYPE_GAS)

                return {
                    ENERGY_TYPE_ELECTRICITY: electricity,
                    ENERGY_TYPE_GAS: gas,
                }
        except aiohttp.ClientError as err:
            raise UpdateFailed(f"Error communicating with API: {err}") from err
        except KeyError as err:
            raise UpdateFailed(f"Invalid data received from API: {err}") from err
