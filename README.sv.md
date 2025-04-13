# Home Assistant IRC Integration

Denna integration låter Home Assistant ansluta till en IRC-server och möjliggör tvåvägskommunikation mellan IRC och Home Assistant.

## Funktioner

- Ansluta till IRC-servrar (med eller utan SSL)
- Skicka och ta emot meddelanden
- Utlösa automatiseringar baserat på IRC-meddelanden
- Skicka meddelanden till IRC från Home Assistant
- Automatisk återanslutning vid förlust av anslutning

## Installation

### Via HACS (Rekommenderas)

1. Öppna HACS i din Home Assistant-instans
2. Gå till "Integrationer"-sektionen
3. Klicka på de tre punkterna i övre högra hörnet och välj "Anpassade förråd"
4. Lägg till detta förråd: `https://github.com/sofagris/hairc`
5. Klicka "Lägg till"
6. Sök efter "IRC" i HACS-butiken
7. Klicka "Installera" på "Home Assistant IRC"-integrationen
8. Starta om Home Assistant

### Manuell Installation

1. Kopiera `hairc`-katalogen till din `custom_components`-katalog i Home Assistant
2. Starta om Home Assistant

## Konfiguration

Lägg till följande i din `configuration.yaml`:

```yaml
hairc:
  server: irc.example.com
  port: 6697
  nickname: dinbot
  channel: "#dinkanal"
  ssl: true
  password: dittlösenord  # Valfritt
```

## Användning

### Skicka Meddelanden

Du kan skicka meddelanden till IRC genom att använda `hairc.send_message`-tjänsten:

```yaml
service: hairc.send_message
data:
  message: "Hej från Home Assistant!"
  channel: "#dinkanal"  # Valfritt, använder standardkanal om inte angiven
```

### Ta Emot Meddelanden

IRC-meddelanden utlöser `hairc_message`-händelsen. Du kan skapa automatiseringar baserade på dessa händelser:

```yaml
alias: "Svara på IRC ping"
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

### Välkomstmeddelande

För att få boten att skicka ett välkomstmeddelande när den ansluter till en kanal, lägg till denna automatisering:

```yaml
alias: "IRC Välkomstmeddelande"
trigger:
  platform: event
  event_type: hairc_connected
action:
  service: hairc.send_message
  data:
    message: "Home Assistant till din tjänst. Skriv !help för lista över kommandon"
```

## Felsökning

Om du upplever problem:

1. Kontrollera Home Assistant-loggarna för felmeddelanden
2. Verifiera dina IRC-serverinställningar
3. Se till att din brandvägg tillåter utgående anslutningar till IRC-servern
4. Kontrollera att boten har tillstånd att gå med i kanalen

## Licens

Detta projekt är licensierat under MIT-licensen - se LICENSE-filen för detaljer. 