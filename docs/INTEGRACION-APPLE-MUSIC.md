# Reproducción de la suscripción dentro de q_AMusik

Estado: investigación; **todavía no implementada**. No cambia la versión 0.2.0.

## Contrato solicitado

La búsqueda, biblioteca y reproducción de la suscripción deben pertenecer a la
aplicación. No basta con abrir un navegador externo ni incrustar el sitio de
Apple como si fuera una integración de nuestra interfaz.

## Condiciones verificadas en documentación oficial

- MusicKit permite reproducción y acceso a la biblioteca con autorización del
  usuario. Para el cliente propio se necesita un developer token emitido para
  el proyecto. No se toma prestado de otra aplicación.
- El usuario final necesita su suscripción; no una membresía de desarrollador.
  El propietario del proyecto necesita acceso al Apple Developer Program para
  obtener las credenciales de MusicKit.
- Qt WebEngine contempla DRM con un Widevine CDM instalado, pero no lo incluye.
  Anunciar soporte EME no demuestra reproducción del catálogo de Apple.
- También hace falta un motor compilado con los códecs correspondientes.

Fuentes primarias:
[MusicKit](https://developer.apple.com/musickit/),
[tokens](https://developer.apple.com/documentation/applemusicapi/generating-developer-tokens),
[Qt WebEngine DRM y códecs](https://doc.qt.io/qt-6.8/qtwebengine-features.html).

## Decisión del motor pendiente de prueba

Se evalúa conservar GTK y usar un proceso de reproducción interno con Qt WebEngine
para MusicKit JS. Una ventana de autorización pertenecería a la aplicación y
mostraría exclusivamente el flujo de Apple. El catálogo seguiría en nuestra UI.
Los controles locales y remotos se coordinarían para evitar audio simultáneo.

Antes de implementar ese puente se prueba el motor. `research/probe_player.py`
comprueba un origen local seguro, AAC y disponibilidad anunciada de Widevine.
Usa un perfil temporal, no recibe Apple ID, no pide licencias y no persiste sesión.
No desactiva el sandbox ni descarga o distribuye CDM. Las dependencias Qt de esta
prueba no se añaden al instalador de producción.

Un resultado positivo sólo acredita prerrequisitos anunciados por el motor.
No acredita MusicKit, VMP, autorización, reproducción completa, calidad de audio,
compatibilidad con Wayland ni equivalencia con la app de macOS.

## Primer resultado · 2026-11-06

En [la prueba 42299929326](https://github.com/QRod/q_AMusik/actions/runs/42299929326),
Ubuntu 24.04 con Qt WebEngine 6.4.2 anunció AAC (`probably`), EME y Widevine.
Se utilizó el CDM que ya estaba instalado en el runner, con perfil off-the-record
y sin desactivar el sandbox. No se usó ninguna cuenta de Apple ni se solicitó
una licencia. La prueba de Ubuntu 22.04 se consulta en esa misma ejecución.
El script no mide el estado efectivo del sandbox de Chromium; sólo declara que
no lo desactiva. Las pruebas de esta rama se lanzan manualmente desde Actions.

Esto permite continuar evaluando un motor interno; no selecciona aún el runtime
de producción ni confirma que Apple acepte el cliente. El paso siguiente necesita
las credenciales de MusicKit del proyecto y reproducción real autorizada.

## Datos que faltan

1. Confirmar acceso a una membresía de desarrollador del propietario del proyecto.
2. Identificador de medios y firma del developer token fuera del cliente; las
   claves privadas `.p8` no se envían al chat ni se incluyen en Git.
3. Verificar reproducción completa con una cuenta real y una suscripción.

No se publica una versión como reproductor integrado hasta verificar el flujo
completo. La investigación permanece en una rama separada.
