# IRC Home Assistant Integration

Eine Home Assistant-Integration, die es Ihnen ermöglicht, sich mit IRC-Servern und -Kanälen zu verbinden, um mit Ihrer Home Assistant-Instanz zu kommunizieren.

## Funktionen

- Verbindung zu IRC-Servern
- Beitreten von IRC-Kanälen
- SSL-Verschlüsselungsunterstützung
- Server-Passwort-Unterstützung
- Protokollierung eingehender Nachrichten
- GUI-Konfiguration

## Installation

### HACS-Installation (Empfohlen)

1. Öffnen Sie HACS in Ihrer Home Assistant-Instanz
2. Gehen Sie zum Abschnitt "Integrationen"
3. Klicken Sie auf die drei Punkte in der oberen rechten Ecke
4. Wählen Sie "Benutzerdefinierte Repositories"
5. Fügen Sie dieses Repository hinzu:
   - Repository: `yourusername/hairc`
   - Kategorie: Integration
6. Klicken Sie auf "Hinzufügen"
7. Finden Sie "IRC Home Assistant Integration" in der Liste
8. Klicken Sie auf "Installieren"
9. Starten Sie Home Assistant neu

### Manuelle Installation

1. Kopieren Sie den Ordner `custom_components/hairc` in Ihren Home Assistant `custom_components`-Ordner
2. Starten Sie Home Assistant neu
3. Gehen Sie zu Integrationen in der Home Assistant GUI
4. Klicken Sie auf "+ Integration hinzufügen"
5. Suchen Sie nach "IRC Home Assistant Integration"
6. Füllen Sie die folgenden Felder aus:
   - Server (IRC-Server, mit dem Sie sich verbinden möchten)
   - Port (Standard 6667)
   - Nickname (Benutzername des Bots)
   - Kanal (Kanal, dem Sie beitreten möchten)
   - Passwort (optional, falls vom Server erforderlich)
   - SSL (wenn Sie eine sichere Verbindung verwenden möchten)

## Konfiguration

### YAML-Konfiguration (optional)

```yaml
# configuration.yaml
hairc:
  server: irc.example.com
  port: 6667
  nickname: homeassistant
  channel: "#homeassistant"
  password: !secret irc_password
  ssl: false
```

## Fehlerbehebung

Wenn Sie Verbindungsprobleme haben:

1. Überprüfen Sie, ob die Serveradresse korrekt ist
2. Bestätigen Sie, dass der Port korrekt ist
3. Verifizieren Sie, ob der Nickname verfügbar ist
4. Prüfen Sie, ob der Kanal existiert
5. Suchen Sie nach Fehlermeldungen im Home Assistant-Log

## Mitwirken

Beiträge sind willkommen! Folgen Sie diesen Schritten:

1. Forken Sie das Projekt
2. Erstellen Sie einen neuen Branch
3. Nehmen Sie Ihre Änderungen vor
4. Senden Sie einen Pull Request

## Lizenz

Dieses Projekt ist unter der MIT-Lizenz lizenziert - siehe [LICENSE](LICENSE) Datei für Details. 