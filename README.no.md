# Home Assistant IRC Integrasjon

Denne integrasjonen lar Home Assistant koble til en IRC-server, og muliggjør toveis kommunikasjon mellom IRC og Home Assistant.

## Funksjoner

- Koble til IRC-servere (med eller uten SSL)
- Sende og motta meldinger
- Utløse automasjoner basert på IRC-meldinger
- Sende meldinger til IRC fra Home Assistant
- Automatisk gjenkobling ved tap av tilkobling

## Installasjon

### Via HACS (Anbefalt)

1. Åpne HACS i din Home Assistant-instans
2. Gå til "Integrasjoner"-seksjonen
3. Klikk på de tre prikkene i øvre høyre hjørne og velg "Egendefinerte repositorier"
4. Legg til dette repositoriet: `https://github.com/sofagris/hairc`
5. Klikk "Legg til"
6. Søk etter "IRC" i HACS-butikken
7. Klikk "Installer" på "Home Assistant IRC"-integrasjonen
8. Start om Home Assistant

### Manuell Installasjon

1. Kopier `hairc`-katalogen til din `custom_components`-katalog i Home Assistant
2. Start om Home Assistant

## Konfigurasjon

Legg til følgende i din `configuration.yaml`:

```yaml
hairc:
  server: irc.example.com
  port: 6697
  nickname: dinbot
  channel: "#dinkanal"
  ssl: true
  password: dittpassord  # Valgfritt
```

## Bruk

### Sende Meldinger

Du kan sende meldinger til IRC ved å bruke `hairc.send_message`-tjenesten:

```yaml
service: hairc.send_message
data:
  message: "Hei fra Home Assistant!"
  channel: "#dinkanal"  # Valgfritt, bruker standardkanal hvis ikke spesifisert
```

### Motta Meldinger

IRC-meldinger utløser `hairc_message`-hendelsen. Du kan lage automasjoner basert på disse hendelsene:

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

### Velkomstmelding

For å få boten til å sende en velkomstmelding når den kobler til en kanal, legg til denne automasjonen:

```yaml
alias: "IRC Velkomstmelding"
trigger:
  platform: event
  event_type: hairc_connected
action:
  service: hairc.send_message
  data:
    message: "Home Assistant til din tjeneste. Skriv !help for liste over kommandoer"
```

## Feilsøking

Hvis du opplever problemer:

1. Sjekk Home Assistant-loggene for feilmeldinger
2. Verifiser IRC-serverinnstillingene dine
3. Sikre at brannmuren din tillater utgående tilkoblinger til IRC-serveren
4. Sjekk at boten har tillatelse til å bli med i kanalen

## Lisens

Dette prosjektet er lisensiert under MIT-lisensen - se LICENSE-filen for detaljer. 