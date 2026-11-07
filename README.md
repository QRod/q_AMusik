# q_AMusik · 0.3.0

Reproductor de escritorio para Ubuntu/Zorin con **biblioteca local nativa y
Apple Music dentro de la misma ventana**. La suscripción utiliza el reproductor
oficial incrustado: no abre un navegador externo ni requiere que contrates
Apple Developer Program. Proyecto independiente de Apple; versión preliminar.

[![Linux](https://github.com/QRod/q_AMusik/actions/workflows/linux.yml/badge.svg)](https://github.com/QRod/q_AMusik/actions/workflows/linux.yml)

[Descargar .deb](https://github.com/QRod/q_AMusik/releases/tag/v0.3.0) ·
[Instalación](docs/INSTALACION.md) · [Cambios](CHANGELOG.md) · [Licencia MIT](LICENSE)

## Instalar o actualizar

Descarga `q-amusik_0.3.0_all.deb` y `SHA256SUMS` desde la
[publicación v0.3.0](https://github.com/QRod/q_AMusik/releases/tag/v0.3.0), en la misma carpeta:

```sh
sha256sum -c SHA256SUMS
sudo apt update
sudo apt install ./q-amusik_0.3.0_all.deb
q-amusik
```

Continúa si la suma muestra `OK`. Cierra la versión anterior antes de actualizar;
se conservan canciones, favoritos y listas locales.

Para escuchar canciones completas de la suscripción hacen falta una cuenta con
Apple Music activo y **Widevine compatible instalado**. Qt puede utilizar el CDM
incluido en Google Chrome instalado en Linux; Chrome no se ejecuta para escuchar.
El `.deb` no incluye ni descarga ese componente. Consulta los
[requisitos y pasos de instalación](docs/INSTALACION.md).

## Usar la aplicación

- **Biblioteca local:** añade canciones o carpetas. Álbumes, artistas, búsqueda,
  favoritos, listas, cola y controles de reproducción siguen siendo nativos.
- **Apple Music:** pulsa «Escuchar» en la barra lateral. Inicia sesión desde el
  reproductor oficial que aparece dentro de q_AMusik; la autorización también
  permanece en ventanas de la aplicación.
- **Volver:** pulsa «Mi biblioteca». Se pausa y silencia el audio web, incluidas
  las ventanas secundarias. Entrar en Apple Music pausa el audio local.

Los controles y listas del servicio pertenecen al reproductor oficial; las listas
locales son independientes. No se añade sincronización de archivos locales hacia
Apple ni equivalencia con todas las funciones de Music para macOS.

## Funciones y compatibilidad

| Área | Alcance |
|---|---|
| Biblioteca local | Importación recursiva sin copiar el audio, metadatos y SQLite |
| Formatos locales | MP3, FLAC, Ogg, Opus, M4A/AAC, WAV y AIFF, según códecs |
| Organización | Búsqueda, favoritos, listas y cuadrículas de álbumes/artistas |
| Reproducción local | Pausa, anterior/siguiente, posición, volumen, aleatorio y repetición |
| Carátulas | Incrustadas en MP3/FLAC/M4A o imágenes cover/folder JPG y PNG |
| Apariencia local | Claro/oscuro según preferencias del escritorio |
| Apple Music | Reproductor oficial dentro de la ventana, sesión propia y DRM del motor |
| Escritorio | X11; Wayland mediante XWayland para alojar la biblioteca GTK |
| Pruebas | Ubuntu 22.04/Qt 5 y Ubuntu 24.04/Qt 6, x86_64 |
| Pendiente manual | Cuenta real, segundo factor, canciones completas, audio físico y Zorin |

No incluye descargas offline del catálogo, Dolby Atmos ni AirPlay. El catálogo,
región, suscripción y autorización dependen de Apple. Cargar la página y anunciar
soporte DRM no demuestra por sí solo reproducción completa con una cuenta.

## Datos y privacidad

Los datos están en `~/.local/share/q_amusik/`, o `$XDG_DATA_HOME/q_amusik/`:

- `library.db`: rutas, etiquetas, favoritos y listas locales.
- `apple-profile/`: sesión, cookies y almacenamiento del reproductor integrado.
- `apple-cache/`: caché web.

El directorio se crea privado para tu usuario. No se importan perfiles ni cookies
personales de Chrome/Firefox. Apple gestiona el inicio de sesión; el código nativo
no extrae contraseñas ni tokens del reproductor. Para cerrar sesión usa el menú
de cuenta de Apple Music. Con q_AMusik cerrado puedes eliminar `apple-profile/`
y `apple-cache/` desde el gestor de archivos para olvidar los datos web, sin tocar
`library.db`. «Quitar» canciones nunca borra los archivos originales.

## Desarrollo

Se usan paquetes del sistema, sin pip ni Node. Instala las dependencias GTK y
GStreamer descritas en [la guía](docs/INSTALACION.md), más Qt WebEngine:
`python3-pyqt6.qtwebengine` en Ubuntu 24.04 o `python3-pyqt5.qtwebengine` en 22.04.

```sh
git clone https://github.com/QRod/q_AMusik.git
cd q_AMusik
/usr/bin/python3 -m q_amusik
python3 -m unittest discover -s tests -v
python3 packaging/build-deb.py
```

El workflow Linux verifica lógica, interfaz GTK, alojamiento GTK/Qt, audio web y
local de prueba, ventanas internas, retorno entre fuentes, construcción e
instalación. La comprobación pública de Apple es separada y no usa una cuenta.
Las capturas y canciones sintéticas de prueba no se instalan en tu biblioteca.

[Arquitectura](docs/architecture.md) · [Integración Apple Music](docs/INTEGRACION-APPLE-MUSIC.md) ·
[Validación](docs/validation.md) · [Hoja de ruta](ROADMAP.md)

## Licencia

Código bajo [MIT](LICENSE); las dependencias conservan sus licencias.
No se distribuyen el catálogo, recursos del reproductor de Apple ni el CDM.
La vista oficial los carga directamente desde sus proveedores.
