# Verificación · 2026-11-06

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

## Preparada, sin ejecutar todavía
- Workflow Linux Ubuntu 22.04/24.04: lógica, GTK con Xvfb, decodificación de WAV
  mediante GStreamer/fakesink y capturas a dos tamaños.
- Construcción e instalación del .deb, validación de la entrada de escritorio,
  prueba de la copia instalada y ayuda del lanzador.

No hay binario Linux validado ni capturas de la interfaz ejecutada. El host no
tiene PyGObject, GStreamer ni dpkg-deb. El workflow no se ejecutó en GitHub porque
este repositorio permanece local.

## Prueba manual necesaria antes de distribuir
- Ubuntu y Zorin reales: instalación, icono, arranque, audio físico y desinstalación.
- Formatos variados, carpetas grandes y unidades extraíbles.
- Revisión visual, teclado, lector de pantalla y tema de alto contraste.
- Cuenta de Apple del usuario en navegador compatible: sesión, suscripción,
  reproducción completa, permisos DRM, región y cierre de sesión.

El estado de desarrollo no implica equivalencia con Apple Music de macOS.
