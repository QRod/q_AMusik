# Arquitectura y decisión inicial · 2026-11-06

## ADR 001: GTK y GStreamer para Linux

Decisión aceptada por el usuario: Python, GTK 3, GStreamer y SQLite del sistema.
GTK 3 está disponible en las bases Ubuntu objetivo. No se necesita un runtime de
Electron para reproducir audio local. La contrapartida inicial era que la vista
del catálogo no estaba integrada; ADR 003 añade el reproductor oficial interno.

- `app.py`: UI y coordinación; conexión SQLite usada sólo por el hilo GTK.
- `interface.py`: composición GTK, cuadrículas, selección y seguimiento de tema
  claro/oscuro. Se consultan las preferencias GTK y GNOME cuando están disponibles;
  no se modifica la configuración del escritorio.
- `artwork.py`: carátulas locales incrustadas o de carpeta. Decodifica fuera de
  GTK con dos trabajadores, hasta ocho tareas activas y caché LRU de 128 entradas.
  Limita los datos de imagen a 8 MiB y escala miniaturas antes de dibujarlas.
  Los callbacks débiles y la ruta actual evitan actualizar widgets destruidos
  o asignar la carátula de una canción anterior al reproductor.
- `library.py`: rutas, lectura de etiquetas y consultas parametrizadas. Cada
  importación abre otra conexión en su hilo. Lee metadatos sin bloqueo SQL y
  guarda lotes de 64 referencias en transacciones cortas. La UI impide cambios
  en favoritos, listas y referencias durante la importación, conservando búsqueda
  y reproducción. Una interrupción conserva los lotes completados; repetir la
  importación omite duplicados.
- `player.py`: playbin de GStreamer, eventos de bus y archivos `file://`.
- `queue.py`: navegación, historial aleatorio y repetición sin dependencias GTK.
- `desktop.py`: ventana Qt, perfil web privado, autorización y coordinación de audio.
- `web_policy.py`: política de navegación HTTPS de Apple/iCloud.
- `child_channel.py`: canal Unix heredado con mensajes acotados y comandos fijos.
- `qt_runtime.py`: binding Qt disponible en la distribución.

Las entradas son archivos elegidos por el usuario y sus etiquetas. No se ejecutan
como comandos, no se interpretan como markup GTK ni se insertan en SQL. Se limita
la longitud de etiquetas mostradas. No se siguen enlaces recursivos a carpetas.
Los decodificadores son los paquetes mantenidos por la distribución. El proyecto
no procesa credenciales de Apple ni tiene un puente privilegiado a una web remota.

## ADR 002: no prometer DRM en un webview sin verificarlo

Decisión inicial de 0.1/0.2; la apertura externa queda sustituida por ADR 003.

MusicKit web requiere un developer token y autorización del usuario; un Apple ID
con suscripción no sustituye las credenciales de desarrollador. Activar EME en
un webview tampoco demuestra disponibilidad de un módulo DRM compatible.
La primera versión abre el reproductor oficial en el navegador del usuario.
La sesión permanece en su perfil habitual; q_AMusik no la inspecciona.

Esto permite empezar por una base nativa útil, pero implica dos interfaces y
controles independientes. La suscripción no es todavía una capacidad integrada
de este cliente. La decisión del motor para MusicKit queda abierta hasta tener
reproducción comprobada en Ubuntu/Zorin.

## ADR 003: reproductor oficial dentro de la ventana

El usuario eligió incrustar el servicio oficial sin contratar Apple Developer
Program. Se conserva GTK en un proceso hijo alojado mediante Gtk.Plug y
QWindow/QWidget; el contenedor Qt mantiene una vista WebEngine y las ventanas
de acceso de Apple. X11/XWayland permite este alojamiento sin reescribir la UI.

Los procesos sólo intercambian controles fijos por un socketpair Unix heredado.
La web no accede a ese canal ni a funciones nativas. La sesión usa un perfil
privado independiente; no se inspeccionan credenciales ni perfiles de navegadores.

Qt 6.4 puede recrear la superficie al añadir el primer widget OpenGL. Por ello
se carga `about:blank` antes de alojar GTK y se comprueba que el identificador
nativo permanezca estable al entrar en Apple Music. La página del servicio no se
solicita hasta elegir esa vista. El cierre limpia recursos del hijo y termina
su bucle, sin destruir dos veces la ventana extranjera.

Las pruebas comprueban carga pública de Apple, controles, ventanas internas,
audio de fixtures, alternancia y cierre. La suscripción completa requiere una
prueba real del usuario; la disponibilidad EME/CDM no es equivalente a una licencia.

## Límites de rendimiento y verificación

La importación se ejecuta en un hilo; el refresco carga las filas en memoria.
La cuadrícula muestra grupos en lotes de 120 y permite pedir más. Paginación SQL
y cancelación de importación quedan para bibliotecas grandes. La cola es una
instantánea de la vista al iniciar reproducción. Álbumes y artistas abren sus
colecciones de canciones. La base anterior se conserva sin cambiar el esquema.
La prueba nativa usa audio sintético y fakesink; hace falta verificación auditiva
en una máquina Linux y una prueba de suscripción realizada por el usuario.
