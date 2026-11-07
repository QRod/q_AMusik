# Cambios

## 0.3.0 · 2026-11-06 · Apple Music integrado (preliminar)

### Añadido
- Reproductor oficial de Apple Music dentro de la ventana de q_AMusik, con
  ventanas de acceso propias y sesión separada de los navegadores del usuario.
- Contenedor Qt WebEngine que conserva la biblioteca GTK mediante X11/XWayland.
- Pausa/silencio coordinados entre audio local y web, incluidas ventanas secundarias.
- Ayuda sobre DRM y guía de instalación incluida en el paquete.

### Cambiado
- «Escuchar» abre la vista integrada; se elimina la apertura de navegadores externos.
- Qt se prepara en `about:blank` antes de alojar GTK para mantener estable la
  superficie nativa, sin contactar con Apple antes de elegir su reproductor.

### Límites
- Necesita Widevine compatible y una suscripción activa. El CDM no se distribuye.
- La carga pública y audio de prueba están verificados; el inicio de sesión y
  canciones completas con una cuenta real requieren comprobación en el equipo del usuario.
- No requiere Apple Developer Program para el reproductor oficial incrustado.

## 0.2.0 · 2026-11-06 · Biblioteca visual

### Cambiado
- Interfaz inspirada en Music de macOS: navegación compacta, reproductor superior
  e iconos simbólicos coherentes, manteniendo los controles del escritorio Linux.
- Modos claro y oscuro según las preferencias del sistema.
- Pantalla inicial de álbumes; artistas y detalle de cada colección.
- Estados vacíos y búsqueda con textos específicos para biblioteca, listas y favoritos.

### Añadido
- Carátulas incrustadas y de carpeta, cargadas en segundo plano con caché limitada.
- Pruebas de cola de 240 carátulas, capturas X11 de ambas apariencias, selección
  múltiple, foco y volumen desplegado.

### Conservado
- SQLite existente, reproducción local, favoritos y listas. Apple Music continúa
  en el navegador; no se añade integración del catálogo ni DRM al cliente.

## 0.1.0 · 2026-11-06 · Primera versión

### Añadido
- Biblioteca musical local persistente, favoritos y listas.
- Reproductor nativo con GStreamer y controles de cola.
- Apertura del reproductor oficial de Apple Music para la suscripción.
- Publicación GitHub con licencia MIT, guía de instalación y .deb con SHA-256.
- Pruebas de lógica, interfaz e instalación del paquete en GitHub Actions.

### Limitaciones
- Sin catálogo integrado ni paridad con la aplicación de macOS.
- Audio físico, Zorin y suscripción pendientes de validar en equipos reales.
