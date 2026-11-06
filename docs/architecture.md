# Arquitectura y decisión inicial · 2026-11-06

## ADR 001: GTK y GStreamer para Linux

Decisión aceptada por el usuario: Python, GTK 3, GStreamer y SQLite del sistema.
GTK 3 está disponible en las bases Ubuntu objetivo. No se necesita un runtime de
Electron para reproducir audio local. La contrapartida es que la vista del
catálogo todavía no está integrada.

- `app.py`: UI y coordinación; conexión SQLite usada sólo por el hilo GTK.
- `library.py`: rutas, lectura de etiquetas y consultas parametrizadas. Cada
  importación abre otra conexión en su hilo. Lee metadatos sin bloqueo SQL y
  guarda lotes de 64 referencias en transacciones cortas. La UI impide cambios
  en favoritos, listas y referencias durante la importación, conservando búsqueda
  y reproducción. Una interrupción conserva los lotes completados; repetir la
  importación omite duplicados.
- `player.py`: playbin de GStreamer, eventos de bus y archivos `file://`.
- `queue.py`: navegación, historial aleatorio y repetición sin dependencias GTK.
- `apple.py`: lanzamiento del sitio oficial con argumentos separados y sin shell.

Las entradas son archivos elegidos por el usuario y sus etiquetas. No se ejecutan
como comandos, no se interpretan como markup GTK ni se insertan en SQL. Se limita
la longitud de etiquetas mostradas. No se siguen enlaces recursivos a carpetas.
Los decodificadores son los paquetes mantenidos por la distribución. El proyecto
no procesa credenciales de Apple ni tiene un puente privilegiado a una web remota.

## ADR 002: no prometer DRM en un webview sin verificarlo

MusicKit web requiere un developer token y autorización del usuario; un Apple ID
con suscripción no sustituye las credenciales de desarrollador. Activar EME en
un webview tampoco demuestra disponibilidad de un módulo DRM compatible.
La primera versión abre el reproductor oficial en el navegador del usuario.
La sesión permanece en su perfil habitual; q_AMusik no la inspecciona.

Esto permite empezar por una base nativa útil, pero implica dos interfaces y
controles independientes. La suscripción no es todavía una capacidad integrada
de este cliente. La decisión del motor para MusicKit queda abierta hasta tener
reproducción comprobada en Ubuntu/Zorin.

## Límites de rendimiento y verificación

La importación se ejecuta en un hilo; el refresco de la biblioteca carga todas
las filas en memoria. Paginación y cancelación quedan para bibliotecas grandes.
La cola es una instantánea de la vista al iniciar reproducción. Las vistas de
álbum y artista son listas ordenadas, sin páginas dedicadas ni carátulas aún.
La prueba nativa usa audio sintético y fakesink; hace falta verificación auditiva
en una máquina Linux y una prueba de suscripción realizada por el usuario.
