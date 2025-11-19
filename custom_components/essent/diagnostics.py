"""Diagnostics support for Essent integration."""

from __future__ import annotations

from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .coordinator import EssentDataUpdateCoordinator


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    coordinator: EssentDataUpdateCoordinator = entry.runtime_data

    # Get diagnostic data
    diagnostics_data = {
        "coordinator_data": coordinator.data if coordinator.data else None,
        "last_update_success": coordinator.last_update_success,
        "api_fetch_minute_offset": coordinator._api_fetch_minute_offset,
    }

    # Add scheduling information if available
    if coordinator._unsub_data:
        diagnostics_data["api_refresh_scheduled"] = True
    else:
        diagnostics_data["api_refresh_scheduled"] = False

    if coordinator._unsub_listener:
        diagnostics_data["listener_tick_scheduled"] = True
    else:
        diagnostics_data["listener_tick_scheduled"] = False

    return diagnostics_data
