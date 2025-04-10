"""Config flow for IRC Home Assistant Integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required("server"): str,
        vol.Required("port", default=6667): int,
        vol.Required("nickname"): str,
        vol.Required("channel"): str,
        vol.Optional("password"): str,
        vol.Optional("ssl", default=False): bool,
    }
)


async def validate_input(hass: HomeAssistant, data: dict) -> dict[str, str]:
    """Validate the user input."""
    # Here we can add validation of the IRC connection
    return {"title": f"IRC: {data['server']}"}


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for IRC."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                # Validate the channel name
                channel = user_input["channel"]
                if not channel.startswith("#"):
                    channel = f"#{channel}"
                user_input["channel"] = channel

                # Check if this config entry already exists
                server = user_input["server"]
                port = user_input["port"]
                nick = user_input["nickname"]
                unique_id = f"{server}:{port}:{nick}"
                await self.async_set_unique_id(unique_id)
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=f"IRC: {server}",
                    data=user_input,
                )
            except Exception as e:
                _LOGGER.error("Error in config flow: %s", e)
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle a reconfiguration flow initiated by the user."""
        entry = self.hass.config_entries.async_get_entry(self.context["entry_id"])
        if entry is None:
            return self.async_abort(reason="not_found")

        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                # Validate the channel name
                channel = user_input["channel"]
                if not channel.startswith("#"):
                    channel = f"#{channel}"
                user_input["channel"] = channel

                # Update the existing entry
                self.hass.config_entries.async_update_entry(
                    entry,
                    data=user_input,
                )

                # Reload the integration to apply changes
                await self.hass.config_entries.async_reload(entry.entry_id)

                return self.async_abort(reason="reconfigure_successful")
            except Exception as e:
                _LOGGER.error("Error in reconfiguration: %s", e)
                errors["base"] = "unknown"

        # Pre-fill the form with current values
        current_data = entry.data
        schema = vol.Schema(
            {
                vol.Required("server", default=current_data["server"]): str,
                vol.Required("port", default=current_data["port"]): int,
                vol.Required("nickname", default=current_data["nickname"]): str,
                vol.Required("channel", default=current_data["channel"]): str,
                vol.Optional("password", default=current_data.get("password", "")): str,
                vol.Optional("ssl", default=current_data.get("ssl", False)): bool,
            }
        )

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=schema,
            errors=errors,
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""
