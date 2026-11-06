# Biblioteca de escritorio

Modo: Operate. Construcción directa sobre GTK, sin cambiar el motor de audio.
Dirección fijada por el usuario: Apple Music de macOS; el usuario rechazó la
apariencia GTK anterior y confirmó modos claro/oscuro siguiendo el sistema.
FORM: seed:15a904f88bf3da17. La referencia explícita del usuario prevalece
sobre alternativas del sorteo; no se sustituye por una identidad temática.

## Contrato de dirección

THESIS: La colección musical se reconoce por sus carátulas y su navegación,
sin que una tabla administrativa sea la portada de la aplicación.

OWN-WORLD: Music de macOS como referencia explícita; superficies blancas o
carbón, lateral gris neutro, tipografía sans e iconos simbólicos rosa rojizo.

STORY: El usuario encuentra su colección, abre un álbum o artista y reproduce
sus archivos; el acceso a la suscripción se identifica como apertura en navegador.

FIRST VIEWPORT: Lateral de 224 px con búsqueda y biblioteca, reproductor superior
centrado y cuadrícula de carátulas de 170 px. Las acciones de importar están
junto al título; cada colección abre sus canciones con reproducción disponible.

FORM: Referencia Apple Music fijada por el usuario y preferencia clara/oscura
confirmada. seed:15a904f88bf3da17; prevalece la dirección explícita del usuario.

FINISH: unreviewed and undocumented is unfinished; this build ends with the finish review, the verdict, DESIGN.md, and every shipping raster carrying its provenance

### Compromisos de implementación
- Barra lateral compacta, selección visible, iconos simbólicos de una sola familia.
- Reproductor superior: anterior, pausa, siguiente, carátula, posición y volumen.
- Biblioteca inicial de carátulas; vistas de álbumes, artistas y canciones reales.
- Fondo blanco y navegación gris cálido en claro; carbón neutro en oscuro.
- Acento rosa rojizo para navegación y acciones, tipografía sans de escritorio.
- Carátulas incrustadas o de carpeta; sustituto neutro cuando no existe imagen.
- Sin contenidos falsos en la biblioteca real. Pruebas y capturas con audio y arte
  geométrico sintéticos identificados como demostración.
- Reproducción, búsqueda, importación, selección múltiple, favoritos y listas
  existentes se mantienen. El acceso a Apple Music continúa en el navegador.

## Verificación
Linux real en CI con GTK/GStreamer, dos tamaños de escritorio, temas claro/oscuro,
estados poblado/vacío/búsqueda/suscripción y reproducción local. Revisar capturas
de la aplicación, nunca una maqueta HTML como evidencia. Revisión independiente
de Impeccable y actualización de DESIGN.md y tokens al terminar.
