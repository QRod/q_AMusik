# Instalar q_AMusik 0.3.0 en Ubuntu / Zorin

Versión preliminar con biblioteca local y reproductor oficial de Apple Music
**dentro de la aplicación**. No necesitas una membresía de desarrollador ni
publicar en la App Store para usar esta vía.

## Requisitos

- Escritorio Ubuntu 22.04/24.04 o Zorin basado en esas versiones.
- X11 o una sesión Wayland con XWayland disponible. La integración de GTK utiliza
  X11 dentro de la ventana; no cambia la configuración del escritorio.
- Cuenta con `sudo` para instalar. Ejecuta q_AMusik con tu usuario, sin sudo.
- Para Apple Music: Internet, suscripción activa y un CDM Widevine compatible.

El `.deb` es `all` por su código Python; APT instala las bibliotecas de la
arquitectura del equipo. Las pruebas son x86_64. No se certifica DRM en ARM.

## Descargar, verificar e instalar

Descarga el `.deb` y `SHA256SUMS` de
[la publicación v0.3.0](https://github.com/QRod/q_AMusik/releases/tag/v0.3.0),
o ejecuta:

```sh
mkdir -p ~/Descargas/q-AMusik-0.3.0
cd ~/Descargas/q-AMusik-0.3.0
curl -fLO https://github.com/QRod/q_AMusik/releases/download/v0.3.0/q-amusik_0.3.0_all.deb
curl -fLO https://github.com/QRod/q_AMusik/releases/download/v0.3.0/SHA256SUMS
sha256sum -c SHA256SUMS
sudo apt update
sudo apt install ./q-amusik_0.3.0_all.deb
```

Continúa sólo si la suma muestra `OK`. La suma comprueba integridad, no es una
firma del autor. `apt install ./archivo.deb` resuelve GTK, GStreamer y Qt WebEngine.
El paquete no incluye skills, herramientas compartidas, perfiles ni música.

## Preparar la reproducción de la suscripción

Qt WebEngine no incluye Widevine. Puede usar el módulo de una instalación
existente de [Google Chrome para Linux](https://www.google.com/chrome/) o de
rutas compatibles de la distribución. Instala el paquete oficial de Chrome si
necesitas ese módulo y vuelve a abrir q_AMusik. Chrome no necesita estar abierto
ni se lanza al escuchar música. q_AMusik no descarga, copia ni redistribuye CDM.

1. Abre **q_AMusik** desde el menú o con `q-amusik`.
2. Pulsa **Escuchar** o **Abrir Apple Music** en la biblioteca local.
3. En el reproductor integrado, pulsa la opción de iniciar sesión de Apple.
4. Completa allí tu Apple ID y segundo factor. No introduzcas datos en la terminal
   ni compartas claves privadas con el proyecto.
5. Reproduce una canción completa de tu suscripción para comprobar tu equipo.

La aplicación aloja el reproductor web oficial; su apariencia, catálogo y opciones
pueden cambiar con Apple. La prueba automatizada usa la página pública y audio
sintético: no sustituye el paso 5 con tu cuenta. Si escuchas sólo avances,
comprueba la cuenta, suscripción, región y compatibilidad DRM del motor.

## Biblioteca local y cambio de fuente

Añade archivos o carpetas desde la cabecera y abre un álbum o artista. Usa
Ctrl/Mayús para seleccionar varias canciones en las tablas. Las listas locales
no se sincronizan con las del servicio. «Mi biblioteca» vuelve a la colección
local y pausa/silencia el audio web; entrar en Apple Music pausa el audio local.

## Actualizar y desinstalar

Cierra q_AMusik antes de instalar una actualización y verifica el `.deb` con su
SHA256SUMS. `sudo apt install ./q-amusik_0.3.0_all.deb` conserva la base anterior.
Para quitar la aplicación:

```sh
sudo apt remove q-amusik
```

Tus datos permanecen en `~/.local/share/q_amusik/` o `$XDG_DATA_HOME/q_amusik/`.
Con la aplicación cerrada, copia ese directorio para respaldarlo. Para olvidar
la sesión web, cierra sesión en el menú de Apple Music o elimina sólo
`apple-profile/` y `apple-cache/` desde el gestor de archivos con q_AMusik cerrado.
No elimines `library.db` si deseas conservar tu biblioteca y listas.

## Resolver problemas

- **Falta Widevine o sólo hay avances:** comprueba los requisitos anteriores;
  tener el archivo del CDM no garantiza que Apple acepte esa combinación de motor
  y sistema. Prueba una canción completa después de iniciar sesión.
- **Sin X11/XWayland:** usa una sesión que proporcione compatibilidad X11 o
  habilita XWayland mediante tu distribución. q_AMusik no arranca un servidor X.
- **No hay sonido:** revisa la salida del escritorio y prueba un archivo local.
  El volumen del servicio se controla dentro de su reproductor.
- **No carga Apple:** usa «Recargar» dentro de q_AMusik y comprueba tu conexión.
  Los certificados no se omiten ni se desactiva el sandbox para sortear fallos.
- **No inicia:** ejecuta `q-amusik` en una terminal y comparte el error en
  [Issues](https://github.com/QRod/q_AMusik/issues), sin cookies, perfiles ni datos privados.

## Ejecutar desde código

Instala GTK/GStreamer y el binding Qt correspondiente. En Ubuntu 24.04:

```sh
sudo apt install python3-gi python3-gi-cairo python3-mutagen gir1.2-gtk-3.0 \
  gir1.2-gstreamer-1.0 gstreamer1.0-plugins-base gstreamer1.0-plugins-good \
  gstreamer1.0-plugins-bad gstreamer1.0-libav gstreamer1.0-pulseaudio \
  python3-pyqt6.qtwebengine
/usr/bin/python3 -m q_amusik
```

En Ubuntu 22.04 sustituye el binding por `python3-pyqt5.qtwebengine`.
Usa Python del sistema; un venv aislado normalmente no encuentra PyGObject de APT.
