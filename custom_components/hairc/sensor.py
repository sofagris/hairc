"""Support for IRC sensors."""
from __future__ import annotations

import logging
import asyncio
from typing import Any
import threading

from twisted.words.protocols import irc
from twisted.internet import protocol, reactor, ssl
from twisted.python import log
from OpenSSL import SSL
from twisted.internet.ssl import CertificateOptions
from twisted.internet._sslverify import ClientTLSOptions

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)
MAX_MESSAGES = 100  # Maximum number of messages to store


class CustomClientTLSOptions(ClientTLSOptions):
    """Custom TLS options for IRC client."""

    def _identityVerifyingInfoCallback(self, connection, where, ret):
        """Override certificate verification."""
        return None


class IRCClient(irc.IRCClient):
    """IRC client implementation using Twisted."""

    def __init__(self, config: dict[str, Any], hass: HomeAssistant) -> None:
        """Initialize the IRC client."""
        self.hass = hass
        self.messages = []
        self.connected = False
        self._config = config
        self.nickname = config["nick"]
        self.factory = None
        _LOGGER.debug("IRC client initialized with config: %s", config)

    def connectionMade(self):
        """Called when a connection is made."""
        _LOGGER.debug("Connection made to IRC server")
        super().connectionMade()

    def signedOn(self):
        """Handle successful connection."""
        try:
            _LOGGER.info("Successfully signed on to IRC server")
            self.connected = True
            self.hass.bus.fire(f"{DOMAIN}_connected")
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
            self.hass.bus.fire(f"{DOMAIN}_disconnected")
        except Exception as e:
            _LOGGER.error("Error in connectionLost: %s", e)

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


class IRCClientFactory(protocol.ReconnectingClientFactory):
    """Factory for IRC clients."""

    def __init__(self, config: dict[str, Any], hass: HomeAssistant) -> None:
        """Initialize the factory."""
        self.config = config
        self.hass = hass
        self.protocol = IRCClient
        self.maxDelay = 300  # Maximum delay between reconnection attempts
        _LOGGER.debug("IRC client factory initialized with config: %s", config)

    def buildProtocol(self, addr):
        """Create an instance of the protocol."""
        _LOGGER.debug("Building protocol for address: %s", addr)
        self.resetDelay()  # Reset the delay when we successfully connect
        p = self.protocol(self.config, self.hass)
        p.factory = self
        return p

    def clientConnectionLost(self, connector, reason):
        """Handle lost connection."""
        _LOGGER.warning("Connection lost: %s", reason)
        protocol.ReconnectingClientFactory.clientConnectionLost(
            self, connector, reason
        )

    def clientConnectionFailed(self, connector, reason):
        """Handle failed connection."""
        _LOGGER.error("Connection failed: %s", reason)
        protocol.ReconnectingClientFactory.clientConnectionFailed(
            self, connector, reason
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

        # Start the Twisted reactor in a separate thread if it's not running
        if not reactor.running:
            def start_reactor():
                try:
                    reactor.run(installSignalHandlers=False)
                except Exception as e:
                    _LOGGER.error("Error in Twisted reactor: %s", e)

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
            try:
                if reactor.running:
                    reactor.callFromThread(reactor.stop)
            except Exception as e:
                _LOGGER.error("Error during cleanup: %s", e)

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
        self._factory = None
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

    async def async_added_to_hass(self) -> None:
        """Set up the sensor."""
        self._factory = IRCClientFactory(self._client._config, self._client.hass)

        if self._client._config["ssl"]:
            # Opprett SSL-kontekst med tilpasset sertifikatvalidering
            options = CertificateOptions(verify=False)
            reactor.connectSSL(
                self._client._config["host"],
                self._client._config["port"],
                self._factory,
                options
            )
        else:
            reactor.connectTCP(
                self._client._config["host"],
                self._client._config["port"],
                self._factory
            )

    async def async_will_remove_from_hass(self) -> None:
        """Clean up resources."""
        if self._factory and self._factory.protocol:
            try:
                self._factory.protocol.quit("Shutting down")
            except Exception as e:
                _LOGGER.error("Error during shutdown: %s", e)

    async def async_update(self) -> None:
        """Update the sensor state."""
        self._state = "connected" if self._client.connected else "disconnected"
