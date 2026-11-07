# Verificación · 2026-11-07

## Reproductor integrado v0.3.0

[Ejecución 42353643523](https://github.com/QRod/q_AMusik/actions/runs/42353643523):
Ubuntu 22.04/Qt 5 y Ubuntu 24.04/Qt 6 completaron lógica, UI GTK, contenedor
GTK/Qt, construcción e instalación. La página pública real de Apple Music cargó
sin cuenta y mostró controles, sin lanzar un navegador externo.

La revisión visual independiente de Impeccable validó barra, ventana interna
y retorno; su veredicto final **ship** resolvió dos correcciones documentales
sobre la integración y su contrato. No amplía la validación a cuenta o DRM real.

El paquete 0.3.0 descargado se verificó con SHA-256: contiene 19 archivos
en las rutas esperadas, propiedad root, y sus módulos coinciden con el código
validado. Incluye la guía de instalación, sin perfiles, CDM ni herramientas compartidas.

El smoke integrado usa WAV silencioso y un servicio HTTP de fixture en loopback.
Con clicks nativos comprueba reproducción web, pausa de GStreamer al cambiar,
ventana secundaria con audio, cierre/silencio al volver y reproducción local.
Exige que el proceso GTK termine con código cero y que el identificador nativo
de ventana no cambie al abrir WebEngine. El cierre ya no genera avisos críticos.

La disponibilidad anunciada de AAC/EME/Widevine se midió aparte, sin solicitudes
de licencia ni cuenta Apple. No prueba autorización, segundo factor, licencia de
una canción completa, calidad de audio, salida física o compatibilidad de Zorin.
Esas comprobaciones requieren la cuenta y el equipo del usuario.

Las ventanas de acceso de fixture se identifican como prueba y no piden datos.
Las capturas públicas de Apple usan un perfil nuevo y no muestran una cuenta.
Los perfiles de prueba se crean en directorios temporales y no se distribuyen.

## Rediseño v0.2.0

El rediseño conserva GTK/GStreamer y SQLite. La revisión visual independiente de
Impeccable emitió **ship** sobre 12 capturas X11: biblioteca clara/oscura, artistas,
detalle de álbum, lista multiselección, canciones y cuadrícula compactas,
volumen desplegado, búsqueda sin resultados, Apple Music, lista vacía y error.
Los fixtures son 20 WAV silenciosos con arte geométrico original; el manifiesto
está en `docs/images/manifest.json` y no se incluye en el paquete de aplicación.

La [ejecución 42297313036](https://github.com/QRod/q_AMusik/actions/runs/42297313036)
incluye pruebas de 16 casos de lógica, GTK y reinstalación del paquete. La nueva
prueba solicita 240 carátulas simultáneas y exige recibir todas, conservando un
máximo de ocho trabajos activos y una caché de 128 imágenes.

Las capturas anteriores con `Gtk.Widget.draw` omitían subventanas de tabla y dos
estados no habían completado su asignación. Se descartaron para evaluación;
la evidencia final usa ImageMagick/X11 y estados separados en el bucle GTK.
Tampoco se usa `gdk_pixbuf_get_from_window`, que provocaba un aborto Cairo/MIME
en el entorno de Ubuntu 22.04. Son cambios del método de captura de pruebas.

El seguimiento de tema utiliza notificaciones GTK y la preferencia de color
del escritorio cuando existe. Las pruebas conmutan GTK y comprueban las dos
paletas; no sustituyen una prueba en todos los escritorios o lectores de pantalla.
No se ejecuta el detector HTML de Impeccable porque la superficie es GTK nativa.

## Ejecutada en el equipo de desarrollo (macOS)
- `python3 -m unittest discover -s tests -v`: 15 pruebas pasan.
- Sintaxis Python con `compileall`: correcta.
- Sintaxis del lanzador con `sh -n`: correcta.
- Mutación controlada de la repetición: la prueba detectó que «siguiente» manual
  no debe quedar en la misma canción con repetir una. Archivo restaurado.
- Revisión estática independiente: detectó una transacción demasiado larga en
  la importación; corregida con lotes cortos y restricciones de edición mientras
  importa. Regresión cubierta con lectura de etiquetas bloqueada y dos conexiones.

Las pruebas de biblioteca inyectan etiquetas sintéticas. No prueban decodificación
real ni importación de etiquetas con Mutagen en este host.

## Ejecutada en GitHub Actions

La primera comprobación de Ubuntu 24.04 pasó en
[la ejecución 42293059931](https://github.com/QRod/q_AMusik/actions/runs/42293059931):

- Las 15 pruebas de lógica.
- GTK con Xvfb, lectura de etiquetas WAV mediante Mutagen y decodificación
  mediante GStreamer/fakesink; capturas de biblioteca y acceso a Apple Music.
- Construcción e instalación del .deb, validación de la entrada de escritorio,
  prueba de la copia instalada y ayuda del lanzador.
- Descarga del artefacto y verificación local de SHA-256.
- Inspección del paquete: 13 archivos en rutas esperadas y propiedad root,
  sin datos privados ni herramientas compartidas.

La captura de biblioteca se revisó y está en `docs/images/biblioteca-linux.png`.
Es audio sintético y no una sesión de Apple Music. La matriz del workflow incluye
Ubuntu 22.04/24.04; consulta
[las ejecuciones](https://github.com/QRod/q_AMusik/actions/workflows/linux.yml)
para comprobar el estado de cada versión y commit. El equipo de desarrollo sigue
siendo macOS: el paquete se construye en Linux, no se simula su instalación local.

## Comprobaciones manuales pendientes
- Ubuntu y Zorin reales: instalación, icono, arranque, audio físico y desinstalación.
- Formatos variados, carpetas grandes y unidades extraíbles.
- Revisión visual, teclado, lector de pantalla y tema de alto contraste.
- Cuenta de Apple del usuario en el reproductor integrado: sesión, suscripción,
  reproducción completa, permisos DRM, región y cierre de sesión.

El estado de desarrollo no implica equivalencia con Apple Music de macOS.
