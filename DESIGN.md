---
name: q_AMusik
description: Biblioteca musical de escritorio con widgets GTK nativos.
colors:
  brand: "#c92c50"
typography:
  page-title:
    fontSize: "30px"
    fontWeight: 700
  section-title:
    fontSize: "24px"
    fontWeight: 600
  brand:
    fontSize: "24px"
    fontWeight: 700
  section-label:
    fontSize: "11px"
    fontWeight: 700
  sidebar-label:
    fontSize: "14px"
spacing:
  control: "8px"
  row: "12px"
  content-gap: "16px"
  content-inset: "24px"
components:
  sidebar-button:
    backgroundColor: "transparent"
    padding: "8px"
    typography: "{typography.sidebar-label}"
  page-heading:
    typography: "{typography.page-title}"
---

# Design System: q_AMusik

## Overview

Referencia funcional y visual solicitada: Apple Music; implementación actual con
widgets GTK 3 e identidad propia. La biblioteca lateral, tabla central y controles
inferiores describen la superficie implementada. No se ha acordado una metáfora
creativa adicional.

Este documento extrae valores de `q_amusik/style.css` y `q_amusik/app.py`.
La revisión visual, las capturas y la ejecución nativa en Linux están pendientes;
la extracción estática no certifica contraste, accesibilidad ni ajuste real.

**Key Characteristics:**
- Widgets y tipografía del escritorio.
- Fondos, texto, selección y foco heredados del tema GTK.
- Un acento de marca y organización mediante espacios y separadores.

## Colors

### Primary
El acento de marca se aplica al nombre de la aplicación en la barra lateral.

### Neutral
Las superficies usan `@theme_bg_color` y `@theme_base_color`; el texto y las
selecciones dependen de `@theme_fg_color`, `@theme_selected_bg_color` y
`@theme_selected_fg_color`. Son referencias del tema GTK, sin equivalentes hex
fijos. Los separadores emplean el texto del tema con alfa 0.12; el hover lateral,
con alfa 0.08. El texto secundario tiene opacidad 0.75 y las etiquetas de sección,
0.72. La compatibilidad con temas claros, oscuros y alto contraste requiere
comprobación visual.

## Typography

La familia, el tamaño de cuerpo y las métricas no sobrescritas proceden del tema
del escritorio. Los roles del frontmatter recogen tamaños y pesos explícitos.
El texto de reproducción usa peso 600. No hay fuentes descargadas ni una escala
completa de cuerpo definida por la aplicación.

## Layout

Ventana inicial de 1120 × 740; mínimo solicitado de 820 × 560. Barra lateral con
ancho solicitado de 210 px y padding de 22 px verticales y 16 px horizontales.
El contenido tiene margen de 24 px. El reproductor inferior tiene padding de
16 px verticales y 24 px horizontales. Los espacios entre widgets usan los
valores del frontmatter; la sección Apple también usa 20 px.

La tabla y las listas laterales disponen de desplazamiento. Los nombres largos
de lista y de reproducción se eliden. No hay breakpoints ni composición móvil
implementados. El ancho mínimo real depende de las medidas naturales del tema
y queda pendiente de ejecución nativa.

## Elevation & Depth

La barra lateral elimina las sombras de sus botones. Los separadores distinguen
barra lateral y reproductor. El resto de elevación y estados conserva lo que
proporcione GTK; no se define una escala propia de sombras o movimiento.

## Shapes

Los radios y contornos de controles ordinarios pertenecen al tema GTK. La barra
lateral elimina bordes y sombras de los botones. No existe una escala propia de
radios que deba extrapolarse.

## Components

Los botones ordinarios, diálogos, buscador, selector de archivos y control de
volumen son widgets GTK. Los botones laterales tienen fondo transparente,
padding propio y hover tonal; los estados de foco restantes dependen del tema.
La navegación no define todavía un tratamiento propio de destino activo.

La biblioteca utiliza una tabla multiselección con columnas de favorito,
título, artista, álbum y duración. Los controles con símbolos incluyen nombres
accesibles. Su funcionamiento con teclado y lector de pantalla requiere una
comprobación nativa. Los estados vacíos describen la falta de canciones o
coincidencias, sin contenido de demostración.

La sección Apple explica la apertura externa y distingue los controles locales.
Las vistas HTML del sidecar son únicamente equivalentes de documentación;
no representan capturas ni reproducen el tema GTK del usuario.

## Do's and Don'ts

### Do:
- **Do** conservar los colores y la tipografía del tema GTK para controles nativos.
- **Do** mantener nombres accesibles en controles con símbolos.
- **Do** verificar la interfaz en Linux antes de declarar calidad visual o accesibilidad.

### Don't:
- **Don't** presentar vistas HTML de documentación como capturas GTK.
- **Don't** sustituir los colores dependientes del tema por valores hex inventados.
- **Don't** copiar recursos propietarios de Apple.
