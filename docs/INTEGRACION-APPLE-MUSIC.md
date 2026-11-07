# Apple Music dentro de q_AMusik

## Decisión

Se integra el reproductor oficial de `https://music.apple.com/` en una vista Qt
WebEngine dentro de la misma ventana que la biblioteca GTK. El usuario eligió
esta vía para usar su suscripción sin contratar el Apple Developer Program.
No se abre un navegador externo ni se utilizan credenciales de otra aplicación.

La biblioteca local conserva la interfaz, SQLite, favoritos, listas y GStreamer.
Al seleccionar Apple Music se pausa el audio local. Al volver a la biblioteca,
se silencian y pausan los elementos multimedia del reproductor y de sus ventanas
secundarias, que se cierran. Las listas locales y las del servicio son distintas.

## Motor y requisitos

Qt WebEngine usa Chromium y necesita un CDM Widevine compatible para contenido
protegido. No redistribuimos ni descargamos ese módulo. Qt puede usar el módulo
de una instalación existente de Google Chrome o de rutas compatibles del sistema;
Chrome no se lanza para reproducir música.

La biblioteca GTK se aloja mediante X11; en escritorios Wayland se usa XWayland.
No se configura el compositor ni se modifican preferencias globales del sistema.
El motor disponible en Ubuntu 22.04 es Qt 5; en Ubuntu 24.04 se utiliza Qt 6.
El runtime se mantiene mediante las actualizaciones de la distribución.

## Sesión y límites de confianza

- Perfil web propio bajo el directorio privado de datos de q_AMusik; no se leen
  cookies, sesiones ni historial de Chrome/Firefox.
- Apple gestiona las contraseñas, segundo factor, biblioteca y licencias. El código
  nativo no extrae ni registra estos datos.
- Ventanas de autorización propiedad de q_AMusik y con el mismo perfil. Se muestra
  el dominio de destino. Sólo se permite navegación HTTPS de Apple/iCloud, sin
  protocolos externos ni `file://`; no se ignoran errores TLS.
- Sin WebChannel ni puente de JavaScript a funciones nativas. Permisos de cámara,
  micrófono, ubicación y descargas deshabilitados.
- El canal con la biblioteca es un `socketpair` Unix heredado sólo por el proceso
  hijo. Acepta comandos fijos y mensajes acotados; no es un servicio HTTP ni TCP.
- La página permanece en `about:blank` hasta abrir Apple Music. Preparar esta
  superficie antes de alojar GTK evita la recreación de la ventana introducida
  por los widgets OpenGL de Qt 6.4.

La cuenta del servicio, suscripción, región y políticas de reproducción de Apple
siguen siendo necesarias. Incrustar el reproductor no añade descargas offline,
Dolby Atmos, AirPlay ni todas las funciones de Music para macOS.

## Evidencia y validación pendiente

La prueba de prerrequisitos [42299929326](https://github.com/QRod/q_AMusik/actions/runs/42299929326)
anunció AAC, EME y Widevine tanto en Qt 5/Ubuntu 22.04 como Qt 6/Ubuntu 24.04,
usando el CDM preinstalado del runner y sin desactivar el sandbox desde el script.
No mide por sí sola el estado efectivo del sandbox.

La integración [42303776304](https://github.com/QRod/q_AMusik/actions/runs/42303776304)
comprobó el alojamiento GTK, audio web de prueba y local, retorno entre fuentes,
ventanas secundarias, instalación y carga pública real de Apple Music sin cuenta.
Las pruebas públicas se distinguen de las locales porque dependen de un servicio
externo. Los fixtures no son contenido del catálogo y no se instalan en la app.

El inicio de sesión con una cuenta real, reproducción completa de la suscripción,
segundo factor y audio físico necesitan comprobación por el propietario de la
cuenta en su equipo. Los prerrequisitos y una página cargada no demuestran que
Apple vaya a conceder una licencia de reproducción completa.

La alternativa futura de integrar el catálogo en nuestros propios controles
mediante MusicKit requeriría credenciales de desarrollador del proyecto. No se
ha confundido esa alternativa con el reproductor oficial incrustado.

Fuentes primarias: [MusicKit](https://developer.apple.com/musickit/),
[DRM y códecs de Qt](https://doc.qt.io/qt-6.8/qtwebengine-features.html),
[alojamiento de GTK en Qt](https://doc.qt.io/qt-6/qtdoc-demos-windowhosting-example.html),
[cambio de superficie OpenGL desde Qt 6.4](https://doc.qt.io/qt-6/qopenglwidget.html).
