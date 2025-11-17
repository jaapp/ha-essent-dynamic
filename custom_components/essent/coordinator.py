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

                    # Extract today's data from the prices array
                    if not data.get("prices") or len(data["prices"]) == 0:
                        raise UpdateFailed("No price data available")

                    today_data = data["prices"][0]

                    return {
                        "electricity": {
                            "tariffs": today_data["electricity"]["tariffs"],
                            "unit": today_data["electricity"]["unitOfMeasurement"],
                            "vat_percentage": today_data["electricity"]["vatPercentage"],
                            "min_price": today_data["electricity"]["minAmount"],
                            "avg_price": today_data["electricity"]["averageAmount"],
                            "max_price": today_data["electricity"]["maxAmount"],
                        },
                        "gas": {
                            "tariffs": today_data["gas"]["tariffs"],
                            "unit": today_data["gas"]["unitOfMeasurement"],
                            "vat_percentage": today_data["gas"]["vatPercentage"],
                            "min_price": today_data["gas"]["minAmount"],
                            "avg_price": today_data["gas"]["averageAmount"],
                            "max_price": today_data["gas"]["maxAmount"],
                        },
                    }
        except aiohttp.ClientError as err:
            raise UpdateFailed(f"Error communicating with API: {err}") from err
        except KeyError as err:
            raise UpdateFailed(f"Invalid data received from API: {err}") from err
