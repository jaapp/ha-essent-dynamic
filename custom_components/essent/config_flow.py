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
