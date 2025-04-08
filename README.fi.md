# IRC Home Assistant Integration

Home Assistant-integraatio, joka mahdollistaa yhteyden IRC-palvelimiin ja -kanaviin Home Assistant -esiintymäsi kanssa kommunikointia varten.

## Ominaisuudet

- Yhteys IRC-palvelimiin
- Liittyminen IRC-kanaville
- SSL-salauksen tuki
- Palvelimen salasanan tuki
- Saapuvien viestien lokitus
- GUI-määritys

## Asennus

### HACS-asennus (Suositeltu)

1. Avaa HACS Home Assistant -esiintymässäsi
2. Siirry "Integraatiot"-osioon
3. Napsauta kolmea pistettä oikeassa yläkulmassa
4. Valitse "Mukautetut säilytöt"
5. Lisää tämä säilytö:
   - Säilytö: `yourusername/hairc`
   - Kategoria: Integraatio
6. Napsauta "Lisää"
7. Etsi "IRC Home Assistant Integration" listasta
8. Napsauta "Asenna"
9. Käynnistä Home Assistant uudelleen

### Manuaalinen asennus

1. Kopioi `custom_components/hairc` -kansio Home Assistant -esiintymäsi `custom_components`-kansioon
2. Käynnistä Home Assistant uudelleen
3. Siirry Home Assistant GUI:n integraatioihin
4. Napsauta "+ Lisää integraatio"
5. Etsi "IRC Home Assistant Integration"
6. Täytä seuraavat kentät:
   - Palvelin (IRC-palvelin, johon haluat yhdistää)
   - Portti (oletus 6667)
   - Nickname (botin käyttäjätunnus)
   - Kanava (kanava, johon haluat liittyä)
   - Salasana (valinnainen, jos palvelin vaatii sitä)
   - SSL (jos haluat käyttää suojattua yhteyttä)

## Määritys

### YAML-määritys (valinnainen)

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

## Vianetsintä

Jos kohtaat yhteyden ongelmia:

1. Tarkista, että palvelimen osoite on oikein
2. Vahvista, että portti on oikein
3. Varmista, että nicknimi on saatavilla
4. Tarkista, onko kanava olemassa
5. Etsi virheilmoituksia Home Assistant -lokista

## Osallistuminen

Osallistuminen on tervetullutta! Noudata näitä ohjeita:

1. Forkkaa projekti
2. Luo uusi haara
3. Tee muutokset
4. Lähetä pull request

## Lisenssi

Tämä projekti on lisensoitu MIT-lisenssillä - katso [LICENSE](LICENSE) tiedostosta lisätietoja. 