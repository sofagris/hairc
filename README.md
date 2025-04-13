# Home Assistant IRC Integration

This integration allows Home Assistant to connect to an IRC server, enabling bidirectional communication between IRC and Home Assistant.

## Features

- Connect to IRC servers (with or without SSL)
- Send and receive messages
- Trigger automations based on IRC messages
- Send messages to IRC from Home Assistant
- Automatic reconnection on connection loss

## Installation

### Via HACS (Recommended)

1. Open HACS in your Home Assistant instance
2. Go to the "Integrations" section
3. Click the three dots in the top right corner and select "Custom repositories"
4. Add this repository: `https://github.com/sofagris/hairc`
5. Click "Add"
6. Search for "IRC" in the HACS store
7. Click "Install" on the "Home Assistant IRC" integration
8. Restart Home Assistant

### Manual Installation

1. Copy the `hairc` directory to your `custom_components` directory in Home Assistant
2. Restart Home Assistant

## Configuration

Add the following to your `configuration.yaml`:

```yaml
# Example configuration
hairc:
  server: irc.example.com
  port: 6697
  nickname: yourbot
  channel: "#yourchannel"
  ssl: true
  password: yourpassword  # Optional
```

## Automation Examples

### Sending Messages

You can send messages to IRC using the `hairc.send_message` service:

```yaml
# Send a message when bot joins channel
automation:
  - alias: "IRC Welcome Message"
    trigger:
    platform: event
    event_type: hairc_connected
  action:
    service: hairc.send_message
    data:
      message: "Home Assistant at your service. Type !help for list of commands"
```	


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

### Receiving Messages

IRC messages trigger the `hairc_message` event. You can create automations based on these events:

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

If you encounter issues:

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