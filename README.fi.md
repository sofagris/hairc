# IRC Home Assistant Integration

Home Assistant -integraatio, joka mahdollistaa yhteyden IRC-palvelimiin ja -kanaviin kommunikoidaksesi Home Assistant -esiintymäsi kanssa.

## Ominaisuudet

- Yhteys IRC-palvelimiin
- Liittyminen IRC-kanaville
- SSL-salauksen tuki
- Palvelimen salasanan tuki
- Saapuvien viestien lokitus
- GUI-määritys

## Asennus

1. Kopioi `custom_components/uairc` -kansio Home Assistant -esiintymäsi `custom_components` -kansioon
2. Käynnistä Home Assistant uudelleen
3. Siirry Home Assistant GUI:n Integraatiot -osioon
4. Napsauta "+ Lisää integraatio"
5. Etsi "IRC Home Assistant Integration"
6. Täytä seuraavat kentät:
   - Server (IRC-palvelin, johon haluat yhdistää)
   - Port (oletus 6667)
   - Nickname (botin käyttäjätunnus)
   - Channel (kanava, johon haluat liittyä)
   - Password (valinnainen, jos palvelin vaatii sitä)
   - SSL (jos haluat käyttää suojattua yhteyttä)

## Määritys

### YAML-määritys (valinnainen)

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

## Vianetsintä

Jos kohtaat yhteyden ongelmia:

1. Tarkista, että palvelimen osoite on oikein
2. Vahvista, että portti on oikein
3. Varmista, että nimimerkki on saatavilla
4. Tarkista, että kanava on olemassa
5. Etsi virheilmoituksia Home Assistant -lokista

## Osallistuminen

Osallistuminen on tervetullutta! Noudata näitä vaiheita:

1. Forkkaa projekti
2. Luo uusi haara
3. Tee muutoksesi
4. Lähetä pull request

## Lisenssi

Tämä projekti on lisensoitu MIT-lisenssillä - katso [LICENSE](LICENSE) -tiedosto yksityiskohdista. 