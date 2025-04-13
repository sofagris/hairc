# Integración IRC para Home Assistant

Esta integración permite a Home Assistant conectarse a un servidor IRC y permite la comunicación bidireccional entre IRC y Home Assistant.

## Características

- Conexión a servidores IRC (con o sin SSL)
- Envío y recepción de mensajes
- Activación de automatizaciones basadas en mensajes IRC
- Envío de mensajes a IRC desde Home Assistant
- Reconexión automática en caso de pérdida de conexión

## Instalación

### A través de HACS (Recomendado)

1. Abra HACS en su instancia de Home Assistant
2. Vaya a la sección "Integraciones"
3. Haga clic en los tres puntos en la esquina superior derecha y seleccione "Repositorios personalizados"
4. Agregue este repositorio: `https://github.com/sofagris/hairc`
5. Haga clic en "Agregar"
6. Busque "IRC" en la tienda HACS
7. Haga clic en "Instalar" en la integración "Home Assistant IRC"
8. Reinicie Home Assistant

### Instalación manual

1. Copie el directorio `hairc` a su directorio `custom_components` en Home Assistant
2. Reinicie Home Assistant

## Configuración

Agregue lo siguiente a su `configuration.yaml`:

```yaml
hairc:
  server: irc.example.com
  port: 6697
  nickname: tubot
  channel: "#tucanal"
  ssl: true
  password: tucontraseña  # Opcional
```

## Uso

### Envío de mensajes

Puede enviar mensajes a IRC usando el servicio `hairc.send_message`:

```yaml
service: hairc.send_message
data:
  message: "¡Hola desde Home Assistant!"
  channel: "#tucanal"  # Opcional, usa el canal predeterminado si no se especifica
```

### Recepción de mensajes

Los mensajes IRC activan el evento `hairc_message`. Puede crear automatizaciones basadas en estos eventos:

```yaml
alias: "Respuesta a ping IRC"
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

### Mensaje de bienvenida

Para que el bot envíe un mensaje de bienvenida cuando se une a un canal, agregue esta automatización:

```yaml
alias: "Mensaje de bienvenida IRC"
trigger:
  platform: event
  event_type: hairc_connected
action:
  service: hairc.send_message
  data:
    message: "Home Assistant a su servicio. Escriba !help para ver la lista de comandos"
```

## Solución de problemas

Si experimenta problemas:

1. Verifique los mensajes de error en los registros de Home Assistant
2. Verifique su configuración del servidor IRC
3. Asegúrese de que su firewall permita conexiones salientes al servidor IRC
4. Verifique que el bot tenga permiso para unirse al canal

## Licencia

Este proyecto está licenciado bajo la licencia MIT - consulte el archivo LICENSE para más detalles. 