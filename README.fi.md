# Home Assistant IRC-integraatio

Tämä integraatio mahdollistaa Home Assistantin yhteyden IRC-palvelimeen ja kaksisuuntaisen viestinnän IRC:n ja Home Assistantin välillä.

## Ominaisuudet

- Yhteys IRC-palvelimiin (SSL-tuella tai ilman)
- Viestien lähettäminen ja vastaanottaminen
- Automaatioiden käynnistäminen IRC-viestien perusteella
- Viestien lähettäminen IRC:lle Home Assistantista
- Automaattinen uudelleenyhdistäminen yhteyden katketessa

## Asennus

### HACS:n kautta (Suositeltu)

1. Avaa HACS Home Assistant -esiintymässäsi
2. Siirry "Integraatiot"-osioon
3. Napsauta kolmea pistettä oikeassa yläkulmassa ja valitse "Mukautetut säilytöt"
4. Lisää tämä säilytö: `https://github.com/sofagris/hairc`
5. Napsauta "Lisää"
6. Etsi "IRC" HACS-kaupasta
7. Napsauta "Asenna" "Home Assistant IRC"-integraatiossa
8. Käynnistä Home Assistant uudelleen

### Manuaalinen asennus

1. Kopioi `hairc`-hakemisto Home Assistantin `custom_components`-hakemistoon
2. Käynnistä Home Assistant uudelleen

## Määritys

Lisää seuraava `configuration.yaml`-tiedostoosi:

```yaml
hairc:
  server: irc.example.com
  port: 6697
  nickname: bottisi
  channel: "#kanavasi"
  ssl: true
  password: salasanasi  # Valinnainen
```

## Käyttö

### Viestien lähettäminen

Voit lähettää viestejä IRC:lle käyttämällä `hairc.send_message`-palvelua:

```yaml
service: hairc.send_message
data:
  message: "Hei Home Assistantista!"
  channel: "#kanavasi"  # Valinnainen, käyttää oletuskanavaa jos ei määritetty
```

### Viestien vastaanottaminen

IRC-viestit laukaisevat `hairc_message`-tapahtuman. Voit luoda automaatioita näiden tapahtumien perusteella:

```yaml
alias: "Vastaus IRC pingiin"
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

### Tervetuloviesti

Saadaksesi botin lähettämään tervetuloviestin kanavalle liityttyään, lisää tämä automaatio:

```yaml
alias: "IRC Tervetuloviesti"
trigger:
  platform: event
  event_type: hairc_connected
action:
  service: hairc.send_message
  data:
    message: "Home Assistant palveluksessasi. Kirjoita !help nähdäksesi komentolistauksen"
```

## Vianetsintä

Jos kohtaat ongelmia:

1. Tarkista Home Assistantin lokit virheilmoituksista
2. Tarkista IRC-palvelimen asetukset
3. Varmista, että palomuurisi sallii lähtevät yhteydet IRC-palvelimeen
4. Tarkista, että botilla on oikeus liittyä kanavalle

## Lisenssi

Tämä projekti on lisensoitu MIT-lisenssillä - katso LICENSE-tiedosto lisätietoja varten. 