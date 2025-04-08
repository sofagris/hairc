"""Support for IRC sensors."""
from __future__ import annotations

import logging
import asyncio
from typing import Any
import threading

from twisted.words.protocols import irc
from twisted.internet import protocol, reactor, defer
from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)
MAX_MESSAGES = 100  # Maximum number of messages to store


class IRCClient(irc.IRCClient):
    """IRC client implementation using Twisted."""

    def __init__(self, config: dict[str, Any], hass: HomeAssistant) -> None:
        """Initialize the IRC client."""
        self.hass = hass
        self.messages = []
        self.connected = False
        self._reconnect_task = None
        self._stop_event = asyncio.Event()
        self._config = config
        self.nickname = config["nick"]
        self.factory = None
        self.transport = None
        self._connection_deferred = None
        _LOGGER.debug("IRC client initialized with config: %s", config)

    def connectionMade(self):
        """Called when a connection is made."""
        _LOGGER.debug("Connection made to IRC server")
        self.transport = self.factory.transport
        if self.transport is None:
            _LOGGER.error("Transport is None in connectionMade")
            return
        super().connectionMade()
        if self._connection_deferred:
            self._connection_deferred.callback(self)

    def signedOn(self):
        """Handle successful connection."""
        try:
            _LOGGER.info("Successfully signed on to IRC server")
            self.connected = True
            self.hass.bus.fire(f"{DOMAIN}_connected")
            if self._reconnect_task:
                self._reconnect_task.cancel()
                self._reconnect_task = None
            channel = self._config["autojoins"][0]
            _LOGGER.debug("Joining channel: %s", channel)
            self.join(channel)
        except Exception as e:
            _LOGGER.error("Error in signedOn: %s", e)

    def connectionLost(self, reason):
        """Handle lost connection."""
        try:
            _LOGGER.warning("Lost connection to IRC server: %s", reason)
            self.connected = False
            self.transport = None
            self.hass.bus.fire(f"{DOMAIN}_disconnected")
            if self._connection_deferred:
                self._connection_deferred.errback(reason)
                self._connection_deferred = None
            if not self._stop_event.is_set():
                # Schedule reconnect in the event loop
                self.hass.loop.call_soon_threadsafe(
                    self.hass.async_create_task,
                    self._reconnect()
                )
        except Exception as e:
            _LOGGER.error("Error in connectionLost: %s", e)

    async def _reconnect(self):
        """Attempt to reconnect to the IRC server."""
        retry_delay = 5  # Start with 5 seconds
        max_delay = 300  # Maximum 5 minutes between retries
        
        while not self._stop_event.is_set():
            try:
                _LOGGER.info(
                    "Attempting to reconnect to IRC server at %s:%s",
                    self._config["host"], self._config["port"]
                )
                self.factory = IRCClientFactory(self._config, self.hass)
                # Create a new deferred for this connection attempt
                self._connection_deferred = defer.Deferred()
                # Schedule the connection in the reactor thread
                reactor.callFromThread(
                    reactor.connectTCP,
                    self._config["host"],
                    self._config["port"],
                    self.factory
                )
                # Wait for the connection to complete or fail
                try:
                    await asyncio.get_event_loop().run_in_executor(
                        None,
                        lambda: self._connection_deferred.result
                    )
                    break
                except Exception as e:
                    _LOGGER.error("Connection attempt failed: %s", e)
                    await asyncio.sleep(retry_delay)
                    retry_delay = min(retry_delay * 2, max_delay)
            except Exception as e:
                _LOGGER.error("Reconnection attempt failed: %s", e)
                await asyncio.sleep(retry_delay)
                retry_delay = min(retry_delay * 2, max_delay)

    def privmsg(self, user, channel, message):
        """Handle incoming messages."""
        try:
            if channel == self.nickname:
                msg = f"Private message from {user}: {message}"
                self._add_message(msg)
                self.hass.bus.fire(
                    f"{DOMAIN}_message",
                    {"message": message, "sender": user}
                )
            else:
                msg = f"Public message in {channel} from {user}: {message}"
                self._add_message(msg)
                self.hass.bus.fire(
                    f"{DOMAIN}_message",
                    {"message": message, "sender": user, "channel": channel}
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
            if self.transport is not None:
                _LOGGER.debug("Sending quit message to IRC server")
                self.quit("Home Assistant shutting down")
        except Exception as e:
            _LOGGER.error("Error during shutdown: %s", e)


class IRCClientFactory(protocol.ClientFactory):
    """Factory for IRC clients."""

    def __init__(self, config: dict[str, Any], hass: HomeAssistant) -> None:
        """Initialize the factory."""
        self.config = config
        self.hass = hass
        self.protocol = IRCClient
        self.transport = None
        _LOGGER.debug("IRC client factory initialized with config: %s", config)

    def buildProtocol(self, addr):
        """Create an instance of the protocol."""
        _LOGGER.debug("Building protocol for address: %s", addr)
        p = self.protocol(self.config, self.hass)
        p.factory = self
        return p

    def clientConnectionLost(self, connector, reason):
        """Handle lost connection."""
        _LOGGER.warning("Connection lost: %s", reason)
        # Schedule reconnect in the event loop
        self.hass.loop.call_soon_threadsafe(
            self.hass.async_create_task,
            self.protocol(self.config, self.hass)._reconnect()
        )

    def clientConnectionFailed(self, connector, reason):
        """Handle failed connection."""
        _LOGGER.error("Connection failed: %s", reason)
        # Schedule reconnect in the event loop
        self.hass.loop.call_soon_threadsafe(
            self.hass.async_create_task,
            self.protocol(self.config, self.hass)._reconnect()
        )


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
        _LOGGER.debug("Setting up IRC integration with config: %s", config)

        factory = IRCClientFactory(config, hass)
        client = factory.buildProtocol(None)
        sensor = IRCSensor(client, entry.title)
        async_add_entities([sensor])

        # Start the IRC client in the background
        _LOGGER.info(
            "Connecting to IRC server at %s:%s",
            config["host"], config["port"]
        )

        # Start the Twisted reactor in a separate thread
        def start_reactor():
            try:
                reactor.run(installSignalHandlers=False)
            except Exception as e:
                _LOGGER.error("Error in Twisted reactor: %s", e)

        # Start the reactor in a separate thread
        reactor_thread = threading.Thread(target=start_reactor, daemon=True)
        reactor_thread.start()

        # Wait a moment for the reactor to start
        await asyncio.sleep(1)

        # Connect to the IRC server
        reactor.callFromThread(
            reactor.connectTCP,
            config["host"],
            config["port"],
            factory
        )

        # Register cleanup
        async def async_cleanup():
            await client.stop()
            reactor.callFromThread(reactor.stop)

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
        _LOGGER.debug("IRC sensor initialized with name: %s", name)

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
