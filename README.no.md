# IRC Home Assistant Integrasjon

En Home Assistant-integrasjon som lar deg koble til IRC-servere og kanaler for å kommunisere med din Home Assistant-instans.

## Funksjoner

- Koble til IRC-servere
- Delta i IRC-kanaler
- Støtte for SSL-kryptering
- Støtte for server-passord
- Logging av innkommende meldinger
- GUI-konfigurasjon

## Installasjon

### HACS-installasjon (Anbefalt)

1. Åpne HACS i din Home Assistant-instans
2. Gå til "Integrasjoner"-seksjonen
3. Klikk på de tre prikkene i øvre høyre hjørne
4. Velg "Egendefinerte repositorier"
5. Legg til dette repositoriet:
   - Repository: `yourusername/hairc`
   - Kategori: Integrasjon
6. Klikk "Legg til"
7. Finn "IRC Home Assistant Integration" i listen
8. Klikk "Installer"
9. Start om Home Assistant

### Manuell installasjon

1. Kopier mappen `custom_components/hairc` til din Home Assistant `custom_components`-mappe
2. Start om Home Assistant
3. Gå til Integrasjoner i Home Assistant GUI
4. Klikk på "+ Legg til integrasjon"
5. Søk etter "IRC Home Assistant Integration"
6. Fyll ut følgende felter:
   - Server (IRC-serveren du vil koble til)
   - Port (standard 6667)
   - Nickname (botens brukernavn)
   - Channel (kanalen du vil koble til)
   - Password (valgfritt, hvis serveren krever det)
   - SSL (hvis du vil bruke sikker tilkobling)

## Konfigurasjon

### YAML-konfigurasjon (valgfritt)

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

## Feilsøking

Hvis du opplever problemer med tilkoblingen:

1. Sjekk at serveradressen er korrekt
2. Bekreft at porten er riktig
3. Verifiser at nicknamet er tilgjengelig
4. Sjekk at kanalen eksisterer
5. Se etter feilmeldinger i Home Assistant-loggen

## Bidra

Bidrag er velkomne! Vennligst følg disse trinnene:

1. Fork prosjektet
2. Opprett en ny branch
3. Gjør dine endringer
4. Send en pull request

## Lisens

Dette prosjektet er lisensiert under MIT-lisensen - se [LICENSE](LICENSE) filen for detaljer. 