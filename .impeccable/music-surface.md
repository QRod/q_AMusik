# Biblioteca de escritorio

Modo: Operate. Construcción directa sobre GTK, sin cambiar el motor de audio.
Dirección fijada por el usuario: Apple Music de macOS; el usuario rechazó la
apariencia GTK anterior y confirmó modos claro/oscuro siguiendo el sistema.
FORM: referencia explícita del usuario a Music de macOS; no se sustituye por
una identidad temática. El seed del documento histórico no se usa como evidencia
de selección para esta extensión.

## Contrato de dirección

THESIS: La colección musical se reconoce por sus carátulas y su navegación,
sin que una tabla administrativa sea la portada de la aplicación.

OWN-WORLD: Music de macOS como referencia explícita; superficies blancas o
carbón, lateral gris neutro, tipografía sans e iconos simbólicos rosa rojizo.

STORY: El usuario encuentra su colección, abre un álbum o artista y reproduce
sus archivos; el acceso a la suscripción abre el reproductor oficial dentro de la misma ventana.

FIRST VIEWPORT: Lateral de 224 px con búsqueda y biblioteca, reproductor superior
centrado y cuadrícula de carátulas de 170 px. Las acciones de importar están
junto al título; cada colección abre sus canciones con reproducción disponible.

FORM: Referencia Apple Music fijada por el usuario y preferencia clara/oscura
confirmada; prevalece la dirección explícita del usuario.

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
  existentes se mantienen. Apple Music se aloja en Qt WebEngine, con retorno a Mi biblioteca y ventanas de acceso internas.

## Verificación
Linux real en CI con GTK/GStreamer, dos tamaños de escritorio, temas claro/oscuro,
estados poblado/vacío/búsqueda/suscripción y reproducción local. Revisar capturas
de la aplicación, nunca una maqueta HTML como evidencia. Revisión independiente
de Impeccable y actualización de DESIGN.md y tokens al terminar.

## Extensión v0.3.0

La biblioteca GTK conserva su diseño. El contenedor Qt usa controles nativos para
Mi biblioteca, Recargar y Requisitos; el contenido de Apple conserva el diseño
del proveedor. No se aplica CSS ni un rediseño sobre la página oficial.
Las ventanas de autorización muestran identidad/dominio y dedican el espacio
al acceso. Al volver se silencia toda página web y se solicita pausar sus medios.
La validación pública no usa cuenta: autorización y canciones completas siguen
pendientes de la comprobación del usuario con su suscripción.

QUALITY BAR · Extensión Operate: retorno visible, controles nativos legibles,
contenido oficial sin intervención, dominio visible en ventanas internas y
biblioteca existente conservada. Evidencia: capturas reales de CI, sin confundir
fixtures o página pública con autenticación y reproducción licenciada.
