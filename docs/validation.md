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
- Cuenta de Apple del usuario en navegador compatible: sesión, suscripción,
  reproducción completa, permisos DRM, región y cierre de sesión.

El estado de desarrollo no implica equivalencia con Apple Music de macOS.
