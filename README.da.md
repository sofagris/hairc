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

### HACS-installation (Anbefalet)

1. Åbn HACS i din Home Assistant-instans
2. Gå til "Integrationer"-sektionen
3. Klik på de tre prikker i øverste højre hjørne
4. Vælg "Brugerdefinerede repositories"
5. Tilføj dette repository:
   - Repository: `yourusername/hairc`
   - Kategori: Integration
6. Klik "Tilføj"
7. Find "IRC Home Assistant Integration" i listen
8. Klik "Installer"
9. Genstart Home Assistant

### Manuel installation

1. Kopier mappen `custom_components/hairc` til din Home Assistant `custom_components`-mappe
2. Genstart Home Assistant
3. Gå til Integrationer i Home Assistant GUI
4. Klik på "+ Tilføj integration"
5. Søg efter "IRC Home Assistant Integration"
6. Udfyld følgende felter:
   - Server (IRC-serveren du vil forbinde til)
   - Port (standard 6667)
   - Nickname (botens brugernavn)
   - Channel (kanalen du vil deltage i)
   - Password (valgfrit, hvis serveren kræver det)
   - SSL (hvis du vil bruge sikker forbindelse)

## Konfiguration

### YAML-konfiguration (valgfrit)

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

## Fejlfinding

Hvis du oplever forbindelsesproblemer:

1. Kontroller at serveradressen er korrekt
2. Bekræft at porten er korrekt
3. Verificer at nicknamet er tilgængeligt
4. Tjek om kanalen eksisterer
5. Kig efter fejlmeddelelser i Home Assistant-loggen

## Bidrag

Bidrag er velkomne! Følg disse trin:

1. Fork projektet
2. Opret en ny branch
3. Lav dine ændringer
4. Indsend en pull request

## Licens

Dette projekt er licenseret under MIT-licensen - se [LICENSE](LICENSE) filen for detaljer. 