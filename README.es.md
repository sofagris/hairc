# Integración IRC para Home Assistant

Una integración de Home Assistant que te permite conectarte a servidores y canales IRC para comunicarte con tu instancia de Home Assistant.

## Características

- Conexión a servidores IRC
- Unión a canales IRC
- Soporte para encriptación SSL
- Soporte para contraseña del servidor
- Registro de mensajes entrantes
- Configuración mediante interfaz gráfica

## Instalación

### Instalación mediante HACS (Recomendado)

1. Abre HACS en tu instancia de Home Assistant
2. Ve a la sección "Integraciones"
3. Haz clic en los tres puntos en la esquina superior derecha
4. Selecciona "Repositorios personalizados"
5. Añade este repositorio:
   - Repositorio: `yourusername/hairc`
   - Categoría: Integración
6. Haz clic en "Añadir"
7. Encuentra "IRC Home Assistant Integration" en la lista
8. Haz clic en "Instalar"
9. Reinicia Home Assistant

### Instalación manual

1. Copia la carpeta `custom_components/hairc` a tu carpeta `custom_components` de Home Assistant
2. Reinicia Home Assistant
3. Ve a Integraciones en la interfaz gráfica de Home Assistant
4. Haz clic en "+ Añadir integración"
5. Busca "IRC Home Assistant Integration"
6. Completa los siguientes campos:
   - Servidor (servidor IRC al que deseas conectarte)
   - Puerto (predeterminado 6667)
   - Nombre de usuario (nombre de usuario del bot)
   - Canal (canal al que deseas unirte)
   - Contraseña (opcional, si el servidor lo requiere)
   - SSL (si deseas usar una conexión segura)

## Configuración

### Configuración YAML (opcional)

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

## Solución de problemas

Si experimentas problemas de conexión:

1. Verifica que la dirección del servidor sea correcta
2. Confirma que el puerto sea correcto
3. Verifica que el nombre de usuario esté disponible
4. Comprueba si el canal existe
5. Busca mensajes de error en el registro de Home Assistant

## Contribuciones

¡Las contribuciones son bienvenidas! Sigue estos pasos:

1. Bifurca el proyecto
2. Crea una nueva rama
3. Realiza tus cambios
4. Envía una solicitud de extracción

## Licencia

Este proyecto está licenciado bajo la Licencia MIT - consulta el archivo [LICENSE](LICENSE) para más detalles. 