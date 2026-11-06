---
name: q_AMusik
description: Biblioteca musical GTK inspirada en Music de macOS, con apariencia clara y oscura del sistema.
colors:
  light-content: "#ffffff"
  dark-content: "#1e1e20"
  light-text: "#242426"
  dark-text: "#f4f4f5"
  light-sidebar: "#f3f2f5"
  dark-sidebar: "#28282c"
  light-header: "#f8f8f9"
  dark-header: "#242426"
  light-divider: "#e3e2e6"
  dark-divider: "#38383d"
  light-accent: "#d63151"
  dark-accent: "#ff6d86"
  light-primary: "#c92c4c"
  light-primary-hover: "#b92341"
  dark-primary: "#d63151"
  dark-primary-hover: "#c92c4c"
  light-secondary: "#f1f0f4"
  dark-secondary: "#36363c"
  light-muted: "#77717e"
  dark-muted: "#b4aeba"
  light-nav-selected: "#e3e1e7"
  dark-nav-selected: "#414147"
  light-search: "#e8e7ec"
  dark-search: "#36363c"
  light-hover: "#ebebee"
  dark-hover: "#38383d"
  light-active: "#e1e1e5"
  dark-active: "#46464d"
  focus: "#cf3453"
  light-selection: "#fbe6eb"
  dark-selection: "#4b2e39"
  light-selection-text: "#9c1937"
  dark-selection-text: "#ffabbc"
  dark-toggle-text: "#ff8198"
  light-cover: "#efedf2"
  dark-cover: "#35353c"
  light-cover-symbol: "#b3aebc"
  dark-cover-symbol: "#76717f"
  light-card-hover: "#f5f4f7"
  dark-card-hover: "#2c2c30"
  light-track: "#dedde2"
  dark-track: "#49494f"
  light-progress: "#8d8992"
  dark-progress: "#c7c3ce"
typography:
  body:
    fontSize: "13px"
    fontFamily: '"Inter", "Ubuntu", "Cantarell", sans-serif'
  page-title:
    fontSize: "28px"
    fontWeight: 700
    letterSpacing: "-.6px"
  brand:
    fontSize: "22px"
    fontWeight: 700
    letterSpacing: "-.5px"
  section-label:
    fontSize: "11px"
    fontWeight: 600
  album-title:
    fontSize: "13px"
    fontWeight: 500
  album-artist:
    fontSize: "12px"
  now-title:
    fontSize: "12px"
    fontWeight: 600
  time:
    fontSize: "9px"
  collection-artist:
    fontSize: "20px"
    fontWeight: 500
  empty-title:
    fontSize: "23px"
    fontWeight: 600
  apple-title:
    fontSize: "38px"
    fontWeight: 700
    letterSpacing: "-.8px"
  apple-description:
    fontSize: "14px"
rounded:
  control: "6px"
  search: "7px"
  artwork: "8px"
spacing:
  small: "4px"
  control: "8px"
  inset: "12px"
  section: "16px"
  collection: "22px"
  grid-row: "24px"
  content: "30px"
components:
  primary-light:
    backgroundColor: "{colors.light-primary}"
    textColor: "{colors.light-content}"
    rounded: "{rounded.control}"
    padding: "6px 22px"
  primary-dark:
    backgroundColor: "{colors.dark-primary}"
    textColor: "{colors.light-content}"
    rounded: "{rounded.control}"
    padding: "6px 22px"
  secondary-light:
    backgroundColor: "{colors.light-secondary}"
    rounded: "{rounded.control}"
    padding: "6px 14px"
  navigation-light:
    backgroundColor: "transparent"
    rounded: "{rounded.control}"
    padding: "4px 10px"
  search-light:
    backgroundColor: "{colors.light-search}"
    rounded: "{rounded.search}"
    typography: "{typography.album-artist}"
---
# Design System: q_AMusik

## Overview

Music de macOS es la referencia visual elegida por el usuario. q_AMusik la expresa con identidad propia mediante una barra lateral compacta, un reproductor superior y una biblioteca de carátulas sobre superficies neutras. La implementación es Python y GTK 3; no usa una interfaz web.

El modo claro u oscuro sigue la preferencia del sistema: preferencia GTK, nombre del tema con «dark» o esquema GNOME «prefer-dark». La paleta de la ventana es explícita; los diálogos y controles auxiliares conservan comportamiento nativo. No se ha elegido una metáfora adicional.

**Key Characteristics:**
- Biblioteca de carátulas con jerarquía tipográfica sobria.
- Acento rosa rojizo sobre blanco/gris cálido o carbón neutro.
- Controles, navegación y semántica GTK nativos.

Extraído de `q_amusik/style.css`, `interface.py`, `artwork.py` y `app.py`.
La revisión independiente dio SHIP visual sobre doce capturas de GTK en X11,
con fixtures identificadas como demostración. Referencias publicables:
[claro](docs/images/biblioteca-clara.png) y [oscuro](docs/images/biblioteca-oscura.png).
Esta evidencia no constituye una auditoría exhaustiva de accesibilidad, contraste
o compatibilidad con todos los temas. No se ejecuta un detector HTML sobre GTK.

## Colors

### Primary
El rosa rojizo señala marca, iconos laterales, artista de colección y acceso a
Apple Music. El botón principal tiene variantes propias de reposo y hover por
modo. La selección y los controles activados usan tintes rosados independientes.
Los nombres `light-*` y `dark-*` del frontmatter son pares de apariencia, no una
rampa tonal ni valores intercambiables.

### Neutral
El contenido blanco o carbón contrasta con la navegación gris cálido y la
cabecera ligeramente diferenciada. Divisores finos, texto secundario, campos y
hover establecen la jerarquía. El frontmatter recoge los colores reutilizados;
los matices particulares de cuenta, secciones y metadatos siguen en el CSS.

## Typography

La pila explícita de escritorio es Inter, Ubuntu, Cantarell y sans-serif; no se
descargan fuentes. El cuerpo parte de (13px). Los roles y pesos explícitos están
en el frontmatter; métricas no sobrescritas, como interlineado, dependen de GTK.
El título de página domina la biblioteca y la portada de Apple Music usa el
mayor tamaño. Artista, duración y estado ocupan niveles menores. Los textos
largos se eliden con Pango y tienen tooltip; los mensajes explicativos se ajustan.

## Layout

Ventana inicial (1280 × 820), solicitud mínima (960 × 680). La barra lateral pide
(224px) y añade padding (16px 12px); GTK resuelve la asignación final. La cabecera
nativa superior pide altura mínima (62px) y padding (8px 18px), con transporte a
la izquierda, carátula y reproducción al centro, volumen a la derecha. Los
detalles centrales piden (340px). El título tiene márgenes (28px 30px 0) y el
contenido de biblioteca (16px 30px 12px).

Gtk.FlowBox redistribuye entre uno y seis elementos por fila según espacio;
separación horizontal (22px), vertical (24px). La biblioteca muestra inicialmente
hasta 120 grupos y ofrece «Mostrar más». Carátulas de cuadrícula (170px),
colección (120px) y reproducción (44px). Tablas y biblioteca tienen scroll
vertical; las listas laterales también. No hay breakpoints web ni modo móvil.

## Elevation & Depth

La ventana usa capas tonales y separadores de un píxel. Botones, buscador,
cabecera y sliders eliminan sombras propias. No hay escala de elevación ni
animaciones propias definidas; los comportamientos auxiliares dependen de GTK.

## Shapes

Controles con esquinas suaves, buscador algo más redondeado y carátulas con
recorte Cairo. Las carátulas ordinarias usan radio `min(8, width / 8)`; artistas
usan círculo. Las tablas mantienen cabeceras rectas y divisores horizontales.

## Components

### Buttons
Gtk.Button y Gtk.ToggleButton: radio de control, altura mínima (28px), sin
borde ni sombra. Foco con contorno (2px) y desplazamiento (2px); deshabilitado
con opacidad (.45). Principal y secundario usan los paddings del frontmatter.
Los controles simbólicos usan padding (4px 7px), mínimo (22 × 26px); reproducción
usa (5px 10px), ancho mínimo (32px) e icono escalado (1.3).

### Inputs / Fields
Gtk.SearchEntry lateral, altura mínima (31px), tamaño de texto (12px), borde
transparente de un píxel que toma el acento al enfocarse. Filtra la biblioteca
local; buscar desde Apple Music conduce a canciones locales.

### Navigation
Botones nativos con iconos simbólicos, texto (13px), padding (4px 10px) y altura
mínima (26px). Destino actual con fondo tonal explícito y descripción accesible
«Vista actual». Las listas mantienen el mismo patrón y eliden nombres largos.

### Cards / Containers
Cada álbum es un Gtk.Button transparente con carátula, título y artista; hover
tonal, radio (8px) y padding inferior (8px). El clic abre la colección. Artistas
usan imagen circular y recuento de canciones. El arte proviene del archivo o
carpeta; sin arte se dibuja una nota neutra. La decodificación es asíncrona.

### Songs and player
Gtk.TreeView permite selección múltiple, columnas redimensionables y reproducción
con activación de fila. Cabeceras de (11px), celdas de texto con padding vertical
(12px), selección rosa en ambos modos. Gtk.HeaderBar conserva transporte,
shuffle, repetición, posición y Gtk.VolumeButton; los controles son locales.

### Empty states and Apple Music
Los estados vacíos distinguen biblioteca, favoritos, listas y búsqueda. El
buscador sin resultados oculta la acción de importar. La superficie Apple Music
explica que catálogo e inicio de sesión se abren en el navegador. Los diálogos
y selectores de archivo son GTK; las analogías HTML del sidecar son únicamente
documentales y no reproducen medidas naturales, semántica ni renderizado nativo.

## Do's and Don'ts

### Do:
- **Do** conservar los modos claro y oscuro siguiendo el sistema.
- **Do** mantener nombres accesibles y ayudas en controles con símbolos.
- **Do** usar carátulas locales reales y el sustituto neutro cuando falten.
- **Do** verificar los cambios visuales sobre la aplicación GTK en Linux.

### Don't:
- **Don't** presentar analogías HTML como capturas o pruebas de GTK.
- **Don't** copiar logotipos ni recursos propietarios de Apple.
- **Don't** introducir contenido de demostración en la biblioteca real.
