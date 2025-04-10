"""Config flow for IRC Home Assistant Integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import config_validation as cv

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required("server"): cv.string,
        vol.Required("port", default=6667): cv.port,
        vol.Required("nickname"): cv.string,
        vol.Required("channel"): cv.string,
        vol.Optional("password"): cv.string,
        vol.Optional("ssl", default=False): cv.boolean,
    }
)


@config_entries.HANDLERS.register(DOMAIN)
class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for IRC."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_PUSH

    async def validate_input(
        self, hass: HomeAssistant, data: dict[str, Any]
    ) -> dict[str, Any]:
        """Validate the user input allows us to connect."""
        # Here we can add validation of the IRC connection
        return {"title": f"IRC: {data['server']}"}

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        if user_input is None:
            return self.async_show_form(
                step_id="user", data_schema=STEP_USER_DATA_SCHEMA
            )

        errors = {}

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

            info = await self.validate_input(self.hass, user_input)
        except Exception:  # pylint: disable=broad-except
            _LOGGER.exception("Unexpected exception")
            errors["base"] = "unknown"

        if errors:
            return self.async_show_form(
                step_id="user",
                data_schema=STEP_USER_DATA_SCHEMA,
                errors=errors,
            )

        return self.async_create_entry(title=info["title"], data=user_input)

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> OptionsFlowHandler:
        """Get the options flow for this handler."""
        return OptionsFlowHandler(config_entry)


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow for IRC integration."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            # Update the existing entry with new title
            server = user_input["server"]
            self.hass.config_entries.async_update_entry(
                self.config_entry,
                title=f"IRC: {server}",
                data=user_input,
            )
            # Reload the integration to apply changes
            await self.hass.config_entries.async_reload(self.config_entry.entry_id)
            return self.async_create_entry(title="", data=user_input)

        schema = {
            vol.Required(
                "server",
                default=self.config_entry.data.get("server"),
            ): cv.string,
            vol.Required(
                "port",
                default=self.config_entry.data.get("port", 6667),
            ): cv.port,
            vol.Required(
                "nickname",
                default=self.config_entry.data.get("nickname"),
            ): cv.string,
            vol.Required(
                "channel",
                default=self.config_entry.data.get("channel"),
            ): cv.string,
            vol.Optional(
                "password",
                default=self.config_entry.data.get("password", ""),
            ): cv.string,
            vol.Optional(
                "ssl",
                default=self.config_entry.data.get("ssl", False),
            ): cv.boolean,
        }

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(schema),
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""
