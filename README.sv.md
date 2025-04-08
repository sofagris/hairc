# IRC Home Assistant Integration

En Home Assistant-integration som låter dig ansluta till IRC-servrar och kanaler för att kommunicera med din Home Assistant-instans.

## Funktioner

- Ansluta till IRC-servrar
- Delta i IRC-kanaler
- Stöd för SSL-kryptering
- Stöd för serverlösenord
- Loggning av inkommande meddelanden
- GUI-konfiguration

## Installation

1. Kopiera mappen `custom_components/uairc` till din Home Assistant `custom_components`-mapp
2. Starta om Home Assistant
3. Gå till Integrationer i Home Assistant GUI
4. Klicka på "+ Lägg till integration"
5. Sök efter "IRC Home Assistant Integration"
6. Fyll i följande fält:
   - Server (IRC-servern du vill ansluta till)
   - Port (standard 6667)
   - Nickname (botens användarnamn)
   - Channel (kanalen du vill ansluta till)
   - Password (valfritt, om krävs av servern)
   - SSL (om du vill använda säker anslutning)

## Konfiguration

### YAML-konfiguration (valfritt)

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

## Felsökning

Om du upplever anslutningsproblem:

1. Kontrollera att serveradressen är korrekt
2. Bekräfta att porten är korrekt
3. Verifiera att smeknamnet är tillgängligt
4. Kontrollera att kanalen existerar
5. Leta efter felmeddelanden i Home Assistant-loggen

## Bidra

Bidrag är välkomna! Följ dessa steg:

1. Forka projektet
2. Skapa en ny branch
3. Gör dina ändringar
4. Skicka en pull request

## Licens

Detta projekt är licensierat under MIT-licensen - se [LICENSE](LICENSE) filen för detaljer. 