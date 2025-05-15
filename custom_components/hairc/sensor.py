"""Support for IRC sensors."""
from __future__ import annotations

import logging
import asyncio
from typing import Any
import threading
from datetime import datetime

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
        self.realname = "Home Assistant IRC Bot"  # TODO: Make this configurable
        self.factory = None
        self._nick_attempts = 0
        self._reconnecting = False
        # Add the supported attribute used by Twisted to compute maximum line length.
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

    def alterCollidedNick(self, nickname):
        """Generate an alternative nickname when there's a collision."""
        self._nick_attempts += 1
        if self._nick_attempts > 5:  # Maksimalt antall forsøk
            _LOGGER.error("Too many nick collisions, giving up")
            return None
        new_nick = f"{nickname}_{self._nick_attempts}"
        _LOGGER.debug("Nick collision, trying: %s", new_nick)
        return new_nick

    def signedOn(self):
        """Handle successful connection."""
        try:
            _LOGGER.info("Successfully signed on to IRC server")
            self.connected = True
            self._nick_attempts = 0  # Reset nick attempts on successful signon
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
            self._nick_attempts = 0  # Reset nick attempts on disconnect

            if not self._reconnecting:
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
        _LOGGER.debug("IRCClient.send_message called from thread: %s", threading.current_thread().name)
        _LOGGER.debug("Got message : %s", message)
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
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Parse sender information if it exists in the message
        if " from " in message:
            # Extract the full sender info (e.g., "Sofagris!~roy@host")
            sender_part = message.split(" from ")[1].split(":")[0]
            message_content = (
                message.split(": ", 1)[1] if ": " in message else message
            )
            
            # Parse nick and host
            if "!" in sender_part:
                nick, host = sender_part.split("!", 1)
                formatted_message = {
                    "timestamp": timestamp,
                    "nick": nick,
                    "host": host,
                    "message": message_content
                }
            else:
                formatted_message = {
                    "timestamp": timestamp,
                    "nick": sender_part,
                    "host": "",
                    "message": message_content
                }
        else:
            formatted_message = {
                "timestamp": timestamp,
                "nick": "System",
                "host": "",
                "message": message
            }
            
        self.messages.append(formatted_message)
        if len(self.messages) > MAX_MESSAGES:
            self.messages = self.messages[-MAX_MESSAGES:]

    def send_message(self, message: str, channel: str = None) -> None:
        """Send a message to IRC."""
        try:
            target = channel or self._config["autojoins"][0]
            _LOGGER.debug("IRCClient.send_message called from thread: %s", threading.current_thread().name)
            self.msg(target, message)
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


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> bool:
    """Set up the IRC sensor from a config entry."""
    try:
        # Build up the configuration
        config = {
            "host": entry.data["server"],
            "port": entry.data["port"],
            "nick": entry.data["nickname"],
            "autojoins": [entry.data["channel"]],
            "ssl": entry.data.get("ssl", False),
            "password": entry.data.get("password"),
        }
        _LOGGER.debug("Setting up IRC integration with config: %s", config)

        # Start Twisted-reactoren (in a separate thread) if it's not already running
        start_reactor()
        await asyncio.sleep(1)

        # Create IRCClientFactory and store it in hass.data so it's available for service callback
        factory = IRCClientFactory(config, hass)
        hass.data.setdefault(DOMAIN, {})["factory"] = factory

        # Create IRCSensor and pass in factory – sensor gets connection status and messages from factory._current_protocol
        sensor = IRCSensor(factory, entry.title)
        async_add_entities([sensor])
        _LOGGER.debug("Sensor entity added.")

        # Let the reactor create the active connection (we call connect via reactor.callFromThread)
        def connect():
            _LOGGER.debug("Inside connect() function.")
            try:
                if config["ssl"]:
                    options = CertificateOptions(verify=False)
                    reactor.connectSSL(config["host"], config["port"], factory, options)
                else:
                    reactor.connectTCP(config["host"], config["port"], factory)
                _LOGGER.debug("connect() executed successfully.")
            except Exception:
                _LOGGER.exception("Error connecting to IRC server")
        reactor.callFromThread(connect)
        _LOGGER.debug("Connect() scheduled; waiting briefly...")
        await asyncio.sleep(0.5)

        # Register the service with a direct async callback that gets the active protocol from factory
        async def async_handle_send_message(call: ServiceCall) -> None:
            try:
                message = call.data.get("message")
                channel = call.data.get("channel")
                if channel is None:
                    # Get default channel from config and check if channel name starts with #
                    channel = config["autojoins"][0]
                    if not channel.startswith("#"):
                        channel = "#" + channel
                if not message:
                    _LOGGER.error("No message provided in service call")
                    return
                # Get factory from hass.data
                current_factory = hass.data.get(DOMAIN, {}).get("factory")
                if not current_factory or not current_factory._current_protocol:
                    _LOGGER.error("No active IRC protocol available for sending message")
                    return
                if not current_factory._current_protocol.connected:
                    _LOGGER.error("The active IRC protocol is not connected")
                    return
                _LOGGER.debug("Sending message from thread: %s",
                            threading.current_thread().name)
                _LOGGER.debug("Sending message: %s to channel: %s", message, channel)
                # Ensure the message is sent via the reactor's thread
                reactor.callFromThread(
                    current_factory._current_protocol.send_message,
                    message,
                    channel
                )
                _LOGGER.debug("Scheduled sending message: %s", message)
            except Exception:
                _LOGGER.exception("Error handling send_message service")

        hass.services.async_register(DOMAIN, SERVICE_SEND_MESSAGE, async_handle_send_message, schema=SERVICE_SCHEMA)
        _LOGGER.debug("Service %s registered under domain %s", SERVICE_SEND_MESSAGE, DOMAIN)

        # Register a cleanup callback – here we disconnect the active connection,
        # but we do NOT stop the reactor (since it's shared by HA)
        def cleanup():
            _LOGGER.debug("Running cleanup callback.")
            try:
                if factory._current_protocol and factory._current_protocol.connected:
                    _LOGGER.debug("Disconnecting IRC client in cleanup.")
                    reactor.callFromThread(factory._current_protocol.transport.loseConnection)
            except Exception:
                _LOGGER.exception("Error during cleanup")
        entry.async_on_unload(cleanup)

        _LOGGER.debug("async_setup_entry completed successfully")
        return True

    except Exception:
        _LOGGER.exception("Error setting up IRC integration")
        return False


class IRCSensor(SensorEntity):
    """Representation of an IRC sensor."""

    def __init__(self, factory: IRCClientFactory, name: str) -> None:
        """Initialize the sensor."""
        self._factory = factory
        self._name = name
        _LOGGER.debug("IRC sensor initialized with name: %s", name)

    @property
    def name(self) -> str:
        """Return the sensor's name."""
        return self._name

    @property
    def state(self) -> str:
        """Return the current connection state."""
        if not self._factory._current_protocol:
            return "disconnected"
        return "connected" if self._factory._current_protocol.connected else "disconnected"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional attributes, like recent messages."""
        if not self._factory._current_protocol:
            return {"messages": [], "connected": False}
        return {
            "messages": self._factory._current_protocol.messages[-10:],
            "connected": self._factory._current_protocol.connected,
        }

    async def async_added_to_hass(self) -> None:
        """Called when the sensor is added to Home Assistant."""
        _LOGGER.debug("IRCSensor added to HA.")

    async def async_will_remove_from_hass(self) -> None:
        """Clean up resources when the sensor is removed.

        Disconnect the IRC client's transport.
        """
        _LOGGER.debug("IRCSensor is being removed; running cleanup.")
        if self._factory and hasattr(self._factory, '_current_protocol'):
            try:
                protocol_instance = self._factory._current_protocol
                if protocol_instance and protocol_instance.connected:
                    _LOGGER.debug("Disconnecting IRC client during cleanup.")
                    reactor.callFromThread(protocol_instance.transport.loseConnection)
            except Exception:
                _LOGGER.exception("Error during cleanup")

    async def async_update(self) -> None:
        """Update the sensor state."""
        if self._factory._current_protocol:
            self._state = "connected" if self._factory._current_protocol.connected else "disconnected"
        else:
            self._state = "disconnected"
