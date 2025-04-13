# Home Assistant IRC Integration

Denne integration gør det muligt for Home Assistant at forbinde til en IRC-server og muliggør tovejskommunikation mellem IRC og Home Assistant.

## Funktioner

- Forbind til IRC-servere (med eller uden SSL)
- Send og modtag beskeder
- Udløs automatiseringer baseret på IRC-beskeder
- Send beskeder til IRC fra Home Assistant
- Automatisk genoprettelse af forbindelse ved tab af forbindelse

## Installation

### Via HACS (Anbefalet)

1. Åbn HACS i din Home Assistant-instans
2. Gå til "Integrationer"-sektionen
3. Klik på de tre prikker i øverste højre hjørne og vælg "Brugerdefinerede repositories"
4. Tilføj dette repository: `https://github.com/sofagris/hairc`
5. Klik "Tilføj"
6. Søg efter "IRC" i HACS-butikken
7. Klik "Installer" på "Home Assistant IRC"-integrationen
8. Genstart Home Assistant

### Manuel Installation

1. Kopier `hairc`-mappen til din `custom_components`-mappe i Home Assistant
2. Genstart Home Assistant

## Konfiguration

Tilføj følgende til din `configuration.yaml`:

```yaml
hairc:
  server: irc.example.com
  port: 6697
  nickname: dinbot
  channel: "#dinkanal"
  ssl: true
  password: ditkodeord  # Valgfrit
```

## Brug

### Sende Beskeder

Du kan sende beskeder til IRC ved at bruge `hairc.send_message`-tjenesten:

```yaml
service: hairc.send_message
data:
  message: "Hej fra Home Assistant!"
  channel: "#dinkanal"  # Valgfrit, bruger standardkanal hvis ikke angivet
```

### Modtage Beskeder

IRC-beskeder udløser `hairc_message`-hændelsen. Du kan oprette automatiseringer baseret på disse hændelser:

```yaml
alias: "Svar på IRC ping"
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

### Velkomstbesked

For at få boten til at sende en velkomstbesked når den forbinder til en kanal, tilføj denne automatisering:

```yaml
alias: "IRC Velkomstbesked"
trigger:
  platform: event
  event_type: hairc_connected
action:
  service: hairc.send_message
  data:
    message: "Home Assistant til din tjeneste. Skriv !help for liste over kommandoer"
```

## Fejlfinding

Hvis du oplever problemer:

1. Tjek Home Assistant-loggene for fejlmeddelelser
2. Verificér dine IRC-serverindstillinger
3. Sikr at din firewall tillader udgående forbindelser til IRC-serveren
4. Tjek at boten har tilladelse til at deltage i kanalen

## Licens

Dette projekt er licenseret under MIT-licensen - se LICENSE-filen for detaljer. 