"""DataUpdateCoordinator for Essent integration."""
from datetime import datetime, timedelta
import logging
from typing import Any, Callable

import aiohttp

from homeassistant.core import HomeAssistant
from homeassistant.helpers.event import async_track_point_in_utc_time
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import dt as dt_util

from .const import API_ENDPOINT, API_FETCH_OFFSET_SECONDS, DOMAIN, UPDATE_INTERVAL

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
            update_interval=None,  # explicit scheduling
        )
        self._unsub_data: Callable[[], None] | None = None
        self._unsub_listener: Callable[[], None] | None = None

    async def async_shutdown(self) -> None:
        """Cancel any scheduled call, and ignore new runs."""
        await super().async_shutdown()
        if self._unsub_data:
            self._unsub_data()
            self._unsub_data = None
        if self._unsub_listener:
            self._unsub_listener()
            self._unsub_listener = None

    def _schedule_data_refresh(self) -> None:
        """Schedule next data fetch aligned near the top of the hour with a slight offset."""
        if self._unsub_data:
            self._unsub_data()

        now = dt_util.utcnow()
        current_hour = now.replace(minute=0, second=0, microsecond=0)
        candidate = current_hour + timedelta(
            hours=1, seconds=API_FETCH_OFFSET_SECONDS
        )
        if candidate <= now:
            candidate = candidate + timedelta(hours=1)

        def _handle(_: datetime) -> None:
            self._unsub_data = None
            self.hass.async_create_task(self.async_request_refresh())

        self._unsub_data = async_track_point_in_utc_time(self.hass, _handle, candidate)

    def _schedule_listener_tick(self) -> None:
        """Schedule listener updates on the hour to advance cached tariffs."""
        if self._unsub_listener:
            self._unsub_listener()

        now = dt_util.utcnow()
        next_hour = now + timedelta(hours=1)
        next_run = datetime(
            next_hour.year,
            next_hour.month,
            next_hour.day,
            next_hour.hour,
            tzinfo=dt_util.UTC,
        )

        def _handle(_: datetime) -> None:
            self._unsub_listener = None
            self.async_update_listeners()
            self._schedule_listener_tick()

        self._unsub_listener = async_track_point_in_utc_time(
            self.hass,
            _handle,
            next_run,
        )

    def _normalize_energy_block(
        self,
        data: dict[str, Any],
        energy_type: str,
        tomorrow: dict[str, Any] | None,
    ) -> dict[str, Any]:
        """Normalize the energy block into the coordinator format."""
        tariffs_today = sorted(
            data.get("tariffs", []),
            key=_tariff_sort_key,
        )
        if not tariffs_today:
            _LOGGER.debug("No tariffs found for %s in payload: %s", energy_type, data)
            raise UpdateFailed(f"No tariffs found for {energy_type}")

        tariffs_tomorrow: list[dict[str, Any]] = []
        if tomorrow:
            tariffs_tomorrow = sorted(
                tomorrow.get("tariffs", []),
                key=_tariff_sort_key,
            )
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
                        _LOGGER.debug("Failed to decode JSON body: %s", raw_body)
                        raise UpdateFailed(f"Invalid JSON received: {err}") from err

            prices = data.get("prices") or []
            if not prices:
                _LOGGER.debug("No price data available in response: %s", data)
                raise UpdateFailed("No price data available")

            current_date = dt_util.now().date().isoformat()
            today = None
            tomorrow = None

            for idx, price in enumerate(prices):
                if price.get("date") == current_date:
                    today = price
                    if idx + 1 < len(prices):
                        tomorrow = prices[idx + 1]
                    break

            if today is None:
                today = prices[0]
                tomorrow = prices[1] if len(prices) > 1 else None
                _LOGGER.debug(
                    "No price entry found for %s, falling back to first date %s",
                    current_date,
                    today.get("date"),
                )

            electricity_block = today.get("electricity")
            gas_block = today.get("gas")

            if not electricity_block or not gas_block:
                _LOGGER.debug(
                    "Missing electricity or gas block in payload: %s", today
                )
                raise UpdateFailed("Response missing electricity or gas data")

            result = {
                "electricity": self._normalize_energy_block(
                    electricity_block,
                    "electricity",
                    tomorrow.get("electricity") if tomorrow else None,
                ),
                "gas": self._normalize_energy_block(
                    gas_block,
                    "gas",
                    tomorrow.get("gas") if tomorrow else None,
                ),
            }

            # Schedule hourly API fetch and hourly listener tick on cached data.
            self._schedule_data_refresh()
            self._schedule_listener_tick()

            return result
        except aiohttp.ClientError as err:
            raise UpdateFailed(f"Error communicating with API: {err}") from err
        except KeyError as err:
            raise UpdateFailed(f"Invalid data received from API: {err}") from err
