"""Support for IRC sensors."""
from __future__ import annotations

import logging
from typing import Any

import irc3
from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class IRCClient(irc3.IrcBot):
    """IRC client implementation using irc3."""

    def __init__(self, config: dict[str, Any], hass: HomeAssistant) -> None:
        """Initialize the IRC client."""
        super().__init__(**config)
        self.hass = hass
        self.messages = []
        self.connected = False

    def connection_made(self, transport):
        """Handle successful connection."""
        _LOGGER.info("Connected to IRC server")
        self.connected = True
        self.hass.bus.fire(f"{DOMAIN}_connected")

    def connection_lost(self, exc):
        """Handle lost connection."""
        _LOGGER.warning("Lost connection to IRC server: %s", exc)
        self.connected = False
        self.hass.bus.fire(f"{DOMAIN}_disconnected")

    def on_privmsg(self, mask, target, data):
        """Handle private messages."""
        msg = f"Private message from {mask.nick}: {data}"
        self.messages.append(msg)
        self.hass.bus.fire(
            f"{DOMAIN}_message",
            {"message": data, "sender": mask.nick}
        )

    def on_pubmsg(self, mask, target, data):
        """Handle public messages."""
        msg = f"Public message in {target} from {mask.nick}: {data}"
        self.messages.append(msg)
        self.hass.bus.fire(
            f"{DOMAIN}_message",
            {"message": data, "sender": mask.nick, "channel": target}
        )

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the IRC sensor from a config entry."""
    config = {
        "host": entry.data["server"],
        "port": entry.data["port"],
        "nick": entry.data["nickname"],
        "autojoins": [entry.data["channel"]],
        "ssl": entry.data.get("ssl", False),
        "password": entry.data.get("password"),
    }

    client = IRCClient(config, hass)
    sensor = IRCSensor(client, entry.title)
    async_add_entities([sensor])

    # Start the IRC client in the background
    hass.async_create_task(client.run())


class IRCSensor(SensorEntity):
    """Representation of an IRC sensor."""

    def __init__(self, client: IRCClient, name: str) -> None:
        """Initialize the sensor."""
        self._client = client
        self._name = name
        self._state = "disconnected"
        self._messages = []

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self) -> str:
        """Return the state of the sensor."""
        return "connected" if self._client.connected else "disconnected"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes."""
        return {
            "messages": self._client.messages[-10:],  # Last 10 messages
            "connected": self._client.connected,
        }

    async def async_update(self) -> None:
        """Update the sensor state."""
        self._state = "connected" if self._client.connected else "disconnected"
