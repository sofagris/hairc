"""Sensor for IRC Home Assistant Integration."""
from __future__ import annotations

import logging

import pydle
from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback


_LOGGER = logging.getLogger(__name__)


class IRCBot(pydle.Client):
    """IRC bot class."""

    def __init__(self, nickname, channel, hass):
        """Initialize the IRC bot."""
        super().__init__(nickname)
        self.channel = channel
        self.hass = hass
        self.connected = False
        self.last_message = None


    async def on_connect(self):
        """Handle connection to IRC server."""
        _LOGGER.info("Connected to IRC server")
        self.connected = True
        await self.join(self.channel)

    async def on_message(self, target, source, message):
        """Handle incoming messages."""
        _LOGGER.info(f"Message from {source}: {message}")
        self.last_message = message


class IRCSensor(SensorEntity):
    """Representation of an IRC sensor."""

    def __init__(self, config_entry: ConfigEntry):
        """Initialize the sensor."""
        self._config_entry = config_entry
        self._state = None
        self._bot = None
        self._name = f"IRC {config_entry.data['server']}"
        self._unique_id = f"irc_{config_entry.entry_id}"

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return self._name

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return self._unique_id

    @property
    def state(self) -> str | None:
        """Return the state of the sensor."""
        return self._state

    async def async_added_to_hass(self) -> None:
        """Run when entity about to be added to hass."""
        await self._start_bot()

    async def _start_bot(self) -> None:
        """Start the IRC bot."""
        config = self._config_entry.data
        self._bot = IRCBot(
            config["nickname"],
            config["channel"],
            self.hass
        )
        
        try:
            await self._bot.connect(
                config["server"],
                config["port"],
                password=config.get("password"),
                tls=config.get("ssl", False)
            )
        except Exception as e:
            _LOGGER.error(f"Failed to connect to IRC server: {e}")
            return

        # Start the bot in the background
        self.hass.async_create_task(self._bot.handle_forever())

    async def async_will_remove_from_hass(self) -> None:
        """Run when entity will be removed from hass."""
        if self._bot:
            await self._bot.disconnect()


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the IRC sensor from a config entry."""
    async_add_entities([IRCSensor(config_entry)]) 