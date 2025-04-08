# IRC Home Assistant Integration

En Home Assistant-integration, der giver dig mulighed for at forbinde til IRC-servere og kanaler for at kommunikere med din Home Assistant-instans.

## Funktioner

- Forbind til IRC-servere
- Deltag i IRC-kanaler
- Understøttelse af SSL-kryptering
- Understøttelse af server-adgangskode
- Logning af indgående beskeder
- GUI-konfiguration

## Installation

1. Kopier mappen `custom_components/uairc` til din Home Assistant `custom_components`-mappe
2. Genstart Home Assistant
3. Gå til Integrationer i Home Assistant GUI
4. Klik på "+ Tilføj integration"
5. Søg efter "IRC Home Assistant Integration"
6. Udfyld følgende felter:
   - Server (IRC-serveren du vil forbinde til)
   - Port (standard 6667)
   - Nickname (botens brugernavn)
   - Channel (kanalen du vil forbinde til)
   - Password (valgfrit, hvis krævet af serveren)
   - SSL (hvis du vil bruge sikker forbindelse)

## Konfiguration

### YAML-konfiguration (valgfrit)

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

## Fejlfinding

Hvis du oplever forbindelsesproblemer:

1. Kontroller at serveradressen er korrekt
2. Bekræft at porten er korrekt
3. Verificer at kaldenavnet er tilgængeligt
4. Kontroller at kanalen eksisterer
5. Kig efter fejlmeddelelser i Home Assistant-loggen

## Bidrag

Bidrag er velkomne! Følg disse trin:

1. Fork projektet
2. Opret en ny branch
3. Lav dine ændringer
4. Indsend en pull request

## Licens

Dette projekt er licenseret under MIT-licensen - se [LICENSE](LICENSE) filen for detaljer. 