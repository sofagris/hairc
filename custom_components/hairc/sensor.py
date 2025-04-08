"""Support for IRC sensors."""
from __future__ import annotations

import logging
import asyncio
from typing import Any

import pydle
from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)
MAX_MESSAGES = 100  # Maximum number of messages to store


class IRCClient(pydle.Client):
    """IRC client implementation using pydle."""

    def __init__(self, config: dict[str, Any], hass: HomeAssistant) -> None:
        """Initialize the IRC client."""
        super().__init__(config["nick"])
        self.hass = hass
        self.messages = []
        self.connected = False
        self._reconnect_task = None
        self._stop_event = asyncio.Event()
        self._config = config

    async def on_connect(self):
        """Handle successful connection."""
        try:
            _LOGGER.info("Connected to IRC server")
            self.connected = True
            self.hass.bus.fire(f"{DOMAIN}_connected")
            if self._reconnect_task:
                self._reconnect_task.cancel()
                self._reconnect_task = None
            await self.join(self._config["autojoins"][0])
        except Exception as e:
            _LOGGER.error("Error in on_connect: %s", e)

    async def on_disconnect(self, expected):
        """Handle lost connection."""
        try:
            _LOGGER.warning("Lost connection to IRC server")
            self.connected = False
            self.hass.bus.fire(f"{DOMAIN}_disconnected")
            if not self._stop_event.is_set():
                self._reconnect_task = self.hass.async_create_task(
                    self._reconnect()
                )
        except Exception as e:
            _LOGGER.error("Error in on_disconnect: %s", e)

    async def _reconnect(self):
        """Attempt to reconnect to the IRC server."""
        retry_delay = 5  # Start with 5 seconds
        max_delay = 300  # Maximum 5 minutes between retries
        
        while not self._stop_event.is_set():
            try:
                _LOGGER.info("Attempting to reconnect to IRC server")
                await self.connect(
                    self._config["host"],
                    self._config["port"],
                    password=self._config.get("password"),
                    tls=self._config.get("ssl", False)
                )
                break
            except Exception as e:
                _LOGGER.error("Reconnection attempt failed: %s", e)
                await asyncio.sleep(retry_delay)
                retry_delay = min(retry_delay * 2, max_delay)

    async def on_message(self, target, source, message):
        """Handle incoming messages."""
        try:
            if target == self.nickname:
                msg = f"Private message from {source}: {message}"
                self._add_message(msg)
                self.hass.bus.fire(
                    f"{DOMAIN}_message",
                    {"message": message, "sender": source}
                )
            else:
                msg = f"Public message in {target} from {source}: {message}"
                self._add_message(msg)
                self.hass.bus.fire(
                    f"{DOMAIN}_message",
                    {"message": message, "sender": source, "channel": target}
                )
        except Exception as e:
            _LOGGER.error("Error handling message: %s", e)

    def _add_message(self, message: str) -> None:
        """Add a message to the list, maintaining the maximum size."""
        self.messages.append(message)
        if len(self.messages) > MAX_MESSAGES:
            self.messages = self.messages[-MAX_MESSAGES:]

    async def stop(self) -> None:
        """Stop the IRC client."""
        self._stop_event.set()
        if self._reconnect_task:
            self._reconnect_task.cancel()
        try:
            await self.disconnect()
        except Exception as e:
            _LOGGER.error("Error during shutdown: %s", e)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the IRC sensor from a config entry."""
    try:
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
        hass.async_create_task(client.connect(
            config["host"],
            config["port"],
            password=config.get("password"),
            tls=config.get("ssl", False)
        ))

        # Register cleanup
        async def async_cleanup():
            await client.stop()

        entry.async_on_unload(async_cleanup)

    except Exception as e:
        _LOGGER.error("Error setting up IRC integration: %s", e)
        raise


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
