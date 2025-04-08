# IRC Home Assistant Integration

A Home Assistant integration that allows you to connect to IRC servers and channels to communicate with your Home Assistant instance.

## Features

- Connect to IRC servers
- Join IRC channels
- SSL encryption support
- Server password support
- Incoming message logging
- GUI configuration

## Installation

1. Copy the `custom_components/uairc` folder to your Home Assistant `custom_components` folder
2. Restart Home Assistant
3. Go to Integrations in Home Assistant GUI
4. Click on "+ Add Integration"
5. Search for "IRC Home Assistant Integration"
6. Fill in the following fields:
   - Server (IRC server you want to connect to)
   - Port (default 6667)
   - Nickname (bot's username)
   - Channel (channel you want to join)
   - Password (optional, if required by the server)
   - SSL (if you want to use secure connection)

## Configuration

### YAML Configuration (optional)

```yaml
# configuration.yaml
uairc:
  server: irc.example.com
  port: 6667
  nickname: homeassistant
  channel: "#homeassistant"
  password: !secret irc_password
  ssl: false
```

## Troubleshooting

If you experience connection issues:

1. Verify the server address is correct
2. Confirm the port is correct
3. Verify the nickname is available
4. Check if the channel exists
5. Look for error messages in the Home Assistant log

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the project
2. Create a new branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Translations

This integration is available in multiple languages:

- [English](README.md) (default)
- [Spanish](README.es.md)
- [French](README.fr.md)
- [German](README.de.md)
- [Chinese](README.zh.md)
- [Japanese](README.ja.md)
- [Norwegian](README.no.md)
- [Swedish](README.sv.md)
- [Danish](README.da.md)
- [Finnish](README.fi.md) 