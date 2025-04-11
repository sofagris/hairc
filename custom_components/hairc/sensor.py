"""Support for IRC sensors."""
from __future__ import annotations

import logging
import asyncio
from typing import Any
import threading

from twisted.words.protocols import irc
from twisted.internet import protocol, reactor
from twisted.internet.ssl import CertificateOptions
from twisted.internet._sslverify import ClientTLSOptions

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers import config_validation as cv
import voluptuous as vol

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)
MAX_MESSAGES = 100  # Maximum number of messages to store

# Global reactor thread
_reactor_thread = None

# Service schema
SERVICE_SEND_MESSAGE = "send_message"
SERVICE_SCHEMA = vol.Schema({
    vol.Required("message"): cv.string,
    vol.Optional("channel"): cv.string,
})


def start_reactor():
    """Start the Twisted reactor in a separate thread."""
    global _reactor_thread
    if _reactor_thread is None or not _reactor_thread.is_alive():
        def run_reactor():
            try:
                if not reactor.running:
                    reactor.run(installSignalHandlers=False)
            except Exception as e:
                _LOGGER.error("Error in Twisted reactor: %s", e)

        _reactor_thread = threading.Thread(target=run_reactor, daemon=True)
        _reactor_thread.start()
        _LOGGER.debug("Started Twisted reactor thread")


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
        self._nick_attempts = 0
        self._reconnecting = False
        # Add supported attribute with default values
        self.supported = type('Supported', (), {
            'getFeature': lambda self, feature: {
                'NICKLEN': 30,
                'CHANNELLEN': 200,
                'TOPICLEN': 390,
                'LINELEN': 512
            }.get(feature, None)
        })()
        _LOGGER.debug("IRC client initialized with config: %s", config)

    def connectionMade(self):
        """Called when a connection is made."""
        _LOGGER.debug("Connection made to IRC server")
        super().connectionMade()
        self.connected = True
        self._nick_attempts = 0
        if hasattr(self.hass, 'bus'):
            self.hass.bus.fire(f"{DOMAIN}_connected")
        channel = self._config["autojoins"][0]
        self.join(channel)

    def signedOn(self):
        """Handle successful connection."""
        try:
            _LOGGER.info("Successfully signed on to IRC server")
            self.connected = True
            self._nick_attempts = 0
            self._reconnecting = False
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
            self._nick_attempts = 0
            self._reconnecting = True
            self.hass.bus.fire(f"{DOMAIN}_disconnected")
            # Try to reconnect
            factory = self.factory
            if factory and hasattr(factory, 'clientConnectionLost'):
                factory.clientConnectionLost(None, reason)
        except Exception as e:
            _LOGGER.error("Error in connectionLost: %s", e)

    def privmsg(self, user, channel, message):
        """Handle incoming messages."""
        try:
            # Handle ping/pong for test purposes
            if message.lower() == "ping":
                if channel == self.nickname:
                    self.msg(user, "pong")
                else:
                    self.msg(channel, "pong")
                return

            # Fire event for automations
            event_data = {
                "message": message,
                "sender": user,
                "channel": channel,
                "type": "private" if channel == self.nickname else "public"
            }
            self.hass.bus.fire(f"{DOMAIN}_message", event_data)

            if channel == self.nickname:
                msg = f"Private message from {user}: {message}"
            else:
                msg = f"Public message in {channel} from {user}: {message}"
            self._add_message(msg)
        except Exception as e:
            _LOGGER.error("Error handling message: %s", e)

    def _add_message(self, message: str) -> None:
        """Add a message to the list, maintaining the maximum size."""
        self.messages.append(message)
        if len(self.messages) > MAX_MESSAGES:
            self.messages = self.messages[-MAX_MESSAGES:]

    def send_message(self, message: str, channel: str = None) -> None:
        """Send a message to IRC."""
        try:
            target = channel or self._config["autojoins"][0]
            reactor.callFromThread(self.msg, target, message)
            _LOGGER.debug("Sent message to %s: %s", target, message)
        except Exception as e:
            _LOGGER.error("Error sending message: %s", e)


class IRCClientFactory(protocol.ReconnectingClientFactory):
    """Factory for IRC clients."""

    def __init__(self, config: dict[str, Any], hass: HomeAssistant) -> None:
        """Initialize the factory."""
        self.config = config
        self.hass = hass
        self.protocol = IRCClient
        self.maxDelay = 300  # Maximum delay between reconnection attempts
        self._current_protocol = None
        _LOGGER.debug("IRC client factory initialized with config: %s", config)

    def buildProtocol(self, addr):
        """Create an instance of the protocol."""
        _LOGGER.debug("Building protocol for address: %s", addr)
        self.resetDelay()  # Reset the delay when we successfully connect
        p = self.protocol(self.config, self.hass)
        p.factory = self
        self._current_protocol = p
        return p

    def clientConnectionLost(self, connector, reason):
        """Handle lost connection."""
        _LOGGER.warning("Connection lost: %s", reason)
        if self._current_protocol and not self._current_protocol._reconnecting:
            protocol.ReconnectingClientFactory.clientConnectionLost(
                self, connector, reason
            )

    def clientConnectionFailed(self, connector, reason):
        """Handle failed connection."""
        _LOGGER.error("Connection failed: %s", reason)
        protocol.ReconnectingClientFactory.clientConnectionFailed(
            self, connector, reason
        )


class IRCSensor(SensorEntity):
    """Representation of an IRC sensor."""

    def __init__(self, factory: IRCClientFactory, name: str) -> None:
        """Initialize the sensor."""
        self._factory = factory
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
        if not self._factory._current_protocol:
            return "disconnected"
        return "connected" if self._factory._current_protocol.connected else "disconnected"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes."""
        if not self._factory._current_protocol:
            return {"messages": [], "connected": False}
        return {
            "messages": self._factory._current_protocol.messages[-10:],
            "connected": self._factory._current_protocol.connected,
        }

    async def async_added_to_hass(self) -> None:
        """Set up the sensor."""
        # Connection is already handled in async_setup_entry
        pass

    async def async_will_remove_from_hass(self) -> None:
        """Clean up resources."""
        if (self._factory and hasattr(self._factory, 'protocol') and
                self._factory.protocol):
            try:
                if hasattr(self._factory.protocol, 'quit'):
                    self._factory.protocol.quit("Shutting down")
                else:
                    _LOGGER.debug("Protocol does not have quit method")
            except Exception as e:
                _LOGGER.error("Error during shutdown: %s", e)

    async def async_update(self) -> None:
        """Update the sensor state."""
        self._state = "connected" if self._factory._current_protocol.connected else "disconnected"

    async def async_send_message(self, message: str, channel: str = None) -> None:
        """Send a message to IRC."""
        if not self._factory._current_protocol:
            _LOGGER.error("Cannot send message: No protocol available")
            return
            
        if not self._factory._current_protocol.connected:
            _LOGGER.error("Cannot send message: Not connected to IRC server")
            return
            
        try:
            target = channel or self._factory._current_protocol._config["autojoins"][0]
            self._factory._current_protocol.send_message(message, target)
            _LOGGER.debug("Sent message to %s: %s", target, message)
        except Exception as e:
            _LOGGER.error("Error sending message: %s", e)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the IRC sensor from a config entry."""
    try:
        # Get configuration
        config = {
            "host": entry.data["server"],
            "port": entry.data["port"],
            "nick": entry.data["nickname"],
            "autojoins": [entry.data["channel"]],
            "ssl": entry.data.get("ssl", False),
            "password": entry.data.get("password"),
        }
        _LOGGER.debug("Setting up IRC integration with config: %s", config)

        # Start the Twisted reactor
        start_reactor()
        await asyncio.sleep(1)  # Wait for reactor to start

        # Create factory and sensor
        factory = IRCClientFactory(config, hass)
        sensor = IRCSensor(factory, entry.title)
        async_add_entities([sensor])

        # Connect to IRC server
        def connect():
            try:
                if config["ssl"]:
                    options = CertificateOptions(verify=False)
                    reactor.connectSSL(
                        config["host"],
                        config["port"],
                        factory,
                        options
                    )
                else:
                    reactor.connectTCP(
                        config["host"],
                        config["port"],
                        factory
                    )
            except Exception as e:
                _LOGGER.error("Error connecting to IRC server: %s", e)

        reactor.callFromThread(connect)

        # Register service
        async def handle_send_message(call: ServiceCall) -> None:
            """Handle the send_message service call."""
            try:
                message = call.data.get("message")
                if not message:
                    _LOGGER.error("No message provided in service call")
                    return
                await sensor.async_send_message(message)
            except Exception as e:
                _LOGGER.error("Error handling send_message service: %s", e)

        hass.services.async_register(
            DOMAIN,
            SERVICE_SEND_MESSAGE,
            handle_send_message,
            schema=SERVICE_SCHEMA
        )

        # Register cleanup
        async def cleanup():
            try:
                if reactor.running:
                    reactor.callFromThread(reactor.stop)
            except Exception as e:
                _LOGGER.error("Error during cleanup: %s", e)

        entry.async_on_unload(cleanup)

        return True

    except Exception as e:
        _LOGGER.error("Error setting up IRC integration: %s", e)
        return False
