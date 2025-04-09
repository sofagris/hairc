# Home Assistant IRC Integration

A Home Assistant integration that allows you to connect to IRC servers and automate actions based on IRC messages.

## Installation

1. Copy this folder to `custom_components/hairc` in your Home Assistant installation
2. Restart Home Assistant
3. Go to Integrations and add "IRC" from the user interface

## Configuration

Configure the integration through the user interface or `configuration.yaml`:

```yaml
# Example configuration
hairc:
  server: irc.oftc.net
  port: 6667
  nickname: mybot
  channel: "#mychannel"
  ssl: false
  password: null  # Optional
```

## Automation Examples

### Sending Messages to IRC

```yaml
# Example automation for sending messages
automation:
  - alias: "Send IRC message when light turns on"
    trigger:
      platform: state
      entity_id: light.living_room
      to: "on"
    action:
      service: hairc.send_message
      data:
        message: "The living room light was turned on!"
        channel: "#mychannel"  # Optional, uses default channel if not specified
```

### Reacting to IRC Messages

```yaml
# Example automation for reacting to IRC messages
automation:
  - alias: "Turn on light when someone writes 'light on' in IRC"
    trigger:
      platform: event
      event_type: hairc_message
      event_data:
        message: "light on"
        type: public
    action:
      service: light.turn_on
      target:
        entity_id: light.living_room
```

### Advanced Examples

```yaml
# Example of complex automation
automation:
  - alias: "Handle IRC Commands"
    trigger:
      platform: event
      event_type: hairc_message
    condition:
      condition: template
      value_template: >
        {% set message = trigger.event.data.message %}
        {% set sender = trigger.event.data.sender %}
        {{ message.startswith('!') }}
    action:
      - choose:
          - conditions:
              - condition: template
                value_template: "{{ trigger.event.data.message == '!status' }}"
            sequence:
              - service: hairc.send_message
                data:
                  message: >
                    Status: 
                    Light: {{ states('light.living_room') }}
                    Temperature: {{ states('sensor.temperature') }}°C
          - conditions:
              - condition: template
                value_template: "{{ trigger.event.data.message == '!help' }}"
            sequence:
              - service: hairc.send_message
                data:
                  message: >
                    Available commands:
                    !status - Show home status
                    !help - Show this help text
```

## Events

The integration sends the following events that can be used in automations:

### `hairc_message`
Triggered when a message is received in the IRC channel.

Event data:
- `message`: The message text
- `sender`: The sender's nick
- `channel`: The channel the message came from
- `type`: "public" or "private"

### `hairc_connected`
Triggered when the bot connects to the IRC server.

### `hairc_disconnected`
Triggered when the bot disconnects from the IRC server.

## Services

### `hairc.send_message`
Sends a message to an IRC channel.

```yaml
service: hairc.send_message
data:
  message: "Hello from Home Assistant!"
  channel: "#mychannel"  # Optional
```

## Sensor Attributes

The IRC sensor has the following attributes:

- `messages`: The last 10 messages received in the channel
- `connected`: Connection status (true/false)

## Troubleshooting

If you experience connection issues:

1. Verify the server address and port are correct
2. Try with `ssl: false` if you have SSL issues
3. Enable debug logging for the integration:

```yaml
logger:
  default: warning
  logs:
    custom_components.hairc: debug
```

## Contributing

Contributions are welcome! Please create a pull request with your changes. 