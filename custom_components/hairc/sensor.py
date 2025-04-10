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
        super().__init__()
        self.messages = []
        self.connected = False
        self._config = config
        self.nickname = config["nick"]
        self.factory = None
        self._nick_attempts = 0
        self._reconnecting = False
        self._hass = hass
        self._channels = set()  # Track joined channels
        _LOGGER.debug("IRC client initialized with config: %s", config)

    def connectionMade(self) -> None:
        """Called when a connection is made."""
        _LOGGER.debug("Connection made to IRC server")
        self.connected = True
        self._nick_attempts = 0
        self._reconnecting = False
        if hasattr(self._hass, 'bus'):
            self._hass.bus.fire(f"{DOMAIN}_connected")
        channel = self._config["autojoins"][0]
        _LOGGER.debug("Joining channel: %s", channel)
        self.join(channel)

    def alterCollidedNick(self, nickname):
        """Generate an alternative nickname when there's a collision."""
        self._nick_attempts += 1
        if self._nick_attempts > 5:  # Maksimalt antall forsøk
            _LOGGER.error("Too many nick collisions, giving up")
            return None
        new_nick = f"{nickname}_{self._nick_attempts}"
        _LOGGER.debug("Nick collision, trying: %s", new_nick)
        return new_nick

    def signedOn(self) -> None:
        """Handle successful connection."""
        try:
            _LOGGER.info("Successfully signed on to IRC server")
            self.connected = True
            self._nick_attempts = 0
            self._reconnecting = False
            if hasattr(self._hass, 'bus'):
                self._hass.bus.fire(f"{DOMAIN}_connected")
            channel = self._config["autojoins"][0]
            _LOGGER.debug("Joining channel: %s", channel)
            self.join(channel)
        except Exception as e:
            _LOGGER.error("Error in signedOn: %s", e)

    def joined(self, channel: str) -> None:
        """Called when the bot joins a channel."""
        try:
            _LOGGER.debug("Successfully joined channel: %s", channel)
            self._channels.add(channel)
            if hasattr(self._hass, 'bus'):
                self._hass.bus.fire(
                    f"{DOMAIN}_channel_joined",
                    {"channel": channel}
                )
        except Exception as e:
            _LOGGER.error("Error in joined: %s", e)

    def left(self, channel: str) -> None:
        """Called when the bot leaves a channel."""
        try:
            _LOGGER.debug("Left channel: %s", channel)
            self._channels.discard(channel)
            if hasattr(self._hass, 'bus'):
                self._hass.bus.fire(
                    f"{DOMAIN}_channel_left",
                    {"channel": channel}
                )
        except Exception as e:
            _LOGGER.error("Error in left: %s", e)

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
            self._hass.bus.fire(f"{DOMAIN}_message", event_data)

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
            
            # Check if we're in the channel
            if target not in self._channels:
                _LOGGER.warning("Not in channel %s, attempting to join", target)
                self.join(target)
                # Wait a moment for the join to complete
                reactor.callLater(2, self._send_message_after_join, target, message)
                return
                
            reactor.callFromThread(self.msg, target, message)
            _LOGGER.debug("Sent message to %s: %s", target, message)
        except Exception as e:
            _LOGGER.error("Error sending message: %s", e)

    def _send_message_after_join(self, channel: str, message: str) -> None:
        """Send a message after joining a channel."""
        try:
            if channel in self._channels:
                reactor.callFromThread(self.msg, channel, message)
                _LOGGER.debug("Sent message to %s: %s", channel, message)
            else:
                _LOGGER.error("Failed to join channel %s, message not sent", channel)
        except Exception as e:
            _LOGGER.error("Error in _send_message_after_join: %s", e)

    def connectionLost(self, reason) -> None:
        """Handle lost connection."""
        try:
            _LOGGER.warning("Lost connection to IRC server: %s", reason)
            self.connected = False
            self._nick_attempts = 0
            self._channels.clear()

            if not self._reconnecting:
                self._reconnecting = True
                if hasattr(self._hass, 'bus'):
                    self._hass.bus.fire(f"{DOMAIN}_disconnected")
                # Try to reconnect
                factory = self.factory
                if factory and hasattr(factory, 'clientConnectionLost'):
                    factory.clientConnectionLost(None, reason)
        except Exception as e:
            _LOGGER.error("Error in connectionLost: %s", e)


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


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the IRC sensor from a config entry."""
    try:
        # Map the entry data to the expected config format
        config = {
            "host": entry.data.get("server", ""),  # Use get() to avoid KeyError
            "port": entry.data.get("port", 6667),
            "nick": entry.data.get("nickname", ""),
            "autojoins": [entry.data.get("channel", "")],
            "ssl": entry.data.get("ssl", False),
            "password": entry.data.get("password", ""),
        }
        _LOGGER.debug("Setting up IRC integration with config: %s", config)

        # Start the Twisted reactor if it's not running
        start_reactor()

        # Wait a moment for the reactor to start
        await asyncio.sleep(1)

        factory = IRCClientFactory(config, hass)
        sensor = IRCSensor(config)
        async_add_entities([sensor])

        # Connect to the IRC server
        if config["ssl"]:
            options = CertificateOptions(verify=False)
            reactor.callFromThread(
                reactor.connectSSL,
                config["host"],
                config["port"],
                factory,
                options
            )
        else:
            reactor.callFromThread(
                reactor.connectTCP,
                config["host"],
                config["port"],
                factory
            )

        # Register service
        async def async_handle_send_message(call: ServiceCall) -> None:
            """Handle the send_message service call."""
            try:
                message = call.data.get("message")
                if not message:
                    _LOGGER.error("No message provided in service call")
                    return
                sensor.async_send_message(message)
            except Exception as e:
                _LOGGER.error("Error handling send_message service: %s", e)

        # Register the service
        hass.services.async_register(
            DOMAIN,
            SERVICE_SEND_MESSAGE,
            async_handle_send_message,
            schema=SERVICE_SCHEMA
        )

        # Register cleanup
        async def async_cleanup():
            try:
                if reactor.running:
                    reactor.callFromThread(reactor.stop)
            except Exception as e:
                _LOGGER.error("Error during cleanup: %s", e)

        entry.async_on_unload(async_cleanup)

        return True

    except Exception as e:
        _LOGGER.error("Error setting up IRC integration: %s", e)
        raise


class IRCSensor(SensorEntity):
    """Representation of an IRC sensor."""

    def __init__(self, config: dict[str, Any]) -> None:
        """Initialize the sensor."""
        self._config = config
        self._state = None
        self._last_messages = []
        self._protocol = None
        self._reactor_thread = None
        self._name = f"IRC: {config['host']}"
        self._unique_id = f"{config['host']}:{config['port']}:{config['nick']}"

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

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes."""
        return {"last_messages": self._last_messages}

    async def async_added_to_hass(self) -> None:
        """Run when entity about to be added to hass."""
        await self._connect()

    async def async_will_remove_from_hass(self) -> None:
        """Run when entity will be removed from hass."""
        await self._disconnect()

    async def _connect(self) -> None:
        """Connect to the IRC server."""
        if self._reactor_thread is None or not self._reactor_thread.is_alive():
            self._reactor_thread = threading.Thread(
                target=start_reactor, daemon=True
            )
            self._reactor_thread.start()

        def connect():
            try:
                if self._protocol is not None:
                    self._protocol.transport.loseConnection()
                    self._protocol = None

                factory = IRCClientFactory(self._config, self._message_callback)
                if self._config.get("ssl", False):
                    reactor.connectSSL(
                        self._config["host"],
                        self._config["port"],
                        factory,
                        CertificateOptions(verify=False),
                    )
                else:
                    reactor.connectTCP(
                        self._config["host"],
                        self._config["port"],
                        factory,
                    )
                self._protocol = factory.protocol
            except Exception as e:
                _LOGGER.error("Error connecting to IRC server: %s", e)

        reactor.callFromThread(connect)

    async def _disconnect(self) -> None:
        """Disconnect from the IRC server."""
        def disconnect():
            try:
                if self._protocol is not None:
                    self._protocol.transport.loseConnection()
                    self._protocol = None
            except Exception as e:
                _LOGGER.error("Error disconnecting from IRC server: %s", e)

        reactor.callFromThread(disconnect)

    def _message_callback(self, message: str) -> None:
        """Handle incoming messages."""
        self._last_messages.append(message)
        if len(self._last_messages) > 10:
            self._last_messages.pop(0)
        self._state = message
        self.async_write_ha_state()

    async def async_send_message(self, message: str) -> None:
        """Send a message to the IRC channel."""
        def send():
            try:
                if self._protocol is not None and self._protocol.transport is not None:
                    self._protocol.msg(self._config["autojoins"][0], message)
                    _LOGGER.debug("Message sent to channel %s: %s", 
                                self._config["autojoins"][0], message)
                else:
                    _LOGGER.error("Cannot send message: Not connected to IRC server")
            except Exception as e:
                _LOGGER.error("Error sending message: %s", e)

        reactor.callFromThread(send)

    async def async_update(self) -> None:
        """Update the sensor state."""
        # No need to update as we receive updates through callbacks
        pass
