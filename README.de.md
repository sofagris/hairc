# Home Assistant IRC Integration

Diese Integration ermöglicht es Home Assistant, sich mit einem IRC-Server zu verbinden und ermöglicht eine bidirektionale Kommunikation zwischen IRC und Home Assistant.

## Funktionen

- Verbindung zu IRC-Servern (mit oder ohne SSL)
- Senden und Empfangen von Nachrichten
- Auslösen von Automatisierungen basierend auf IRC-Nachrichten
- Senden von Nachrichten an IRC von Home Assistant
- Automatische Wiederverbindung bei Verbindungsverlust

## Installation

### Über HACS (Empfohlen)

1. Öffnen Sie HACS in Ihrer Home Assistant-Instanz
2. Gehen Sie zum "Integrationen"-Bereich
3. Klicken Sie auf die drei Punkte in der oberen rechten Ecke und wählen Sie "Benutzerdefinierte Repositories"
4. Fügen Sie dieses Repository hinzu: `https://github.com/sofagris/hairc`
5. Klicken Sie auf "Hinzufügen"
6. Suchen Sie nach "IRC" im HACS-Shop
7. Klicken Sie auf "Installieren" bei der "Home Assistant IRC"-Integration
8. Starten Sie Home Assistant neu

### Manuelle Installation

1. Kopieren Sie das `hairc`-Verzeichnis in Ihr `custom_components`-Verzeichnis in Home Assistant
2. Starten Sie Home Assistant neu

## Konfiguration

Fügen Sie Folgendes zu Ihrer `configuration.yaml` hinzu:

```yaml
hairc:
  server: irc.example.com
  port: 6697
  nickname: deinbot
  channel: "#deinkanal"
  ssl: true
  password: deinpasswort  # Optional
```

## Verwendung

### Nachrichten Senden

Sie können Nachrichten an IRC senden, indem Sie den `hairc.send_message`-Service verwenden:

```yaml
service: hairc.send_message
data:
  message: "Hallo von Home Assistant!"
  channel: "#deinkanal"  # Optional, verwendet Standardkanal wenn nicht angegeben
```

### Nachrichten Empfangen

IRC-Nachrichten lösen das `hairc_message`-Ereignis aus. Sie können Automatisierungen basierend auf diesen Ereignissen erstellen:

```yaml
alias: "Antwort auf IRC ping"
trigger:
  platform: event
  event_type: hairc_message
  event_data:
    message: "ping"
    type: public
action:
  service: hairc.send_message
  data:
    message: "pong"
```

### Willkommensnachricht

Um den Bot eine Willkommensnachricht senden zu lassen, wenn er einem Kanal beitritt, fügen Sie diese Automatisierung hinzu:

```yaml
alias: "IRC Willkommensnachricht"
trigger:
  platform: event
  event_type: hairc_connected
action:
  service: hairc.send_message
  data:
    message: "Home Assistant steht Ihnen zur Verfügung. Geben Sie !help für eine Liste der Befehle ein"
```

## Fehlerbehebung

Wenn Sie Probleme haben:

1. Überprüfen Sie die Home Assistant-Protokolle auf Fehlermeldungen
2. Verifizieren Sie Ihre IRC-Server-Einstellungen
3. Stellen Sie sicher, dass Ihre Firewall ausgehende Verbindungen zum IRC-Server erlaubt
4. Überprüfen Sie, ob der Bot die Berechtigung hat, dem Kanal beizutreten

## Lizenz

Dieses Projekt ist unter der MIT-Lizenz lizenziert - siehe LICENSE-Datei für Details. 