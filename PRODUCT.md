# q_AMusik
<!-- impeccable:product-schema 1 -->

## Platform
Escritorio Linux nativo, Ubuntu y Zorin.

## Stack
Python 3 + GTK 3 + GStreamer para la biblioteca; contenedor Qt WebEngine para el
reproductor oficial, con X11/XWayland.

## Users
Usuario de Apple Music que quiere escuchar su suscripción y archivos locales en Linux.

## Product Purpose
Construir un cliente de escritorio inspirado en Apple Music. El objetivo final
es acercarse a sus funciones; la primera versión distingue capacidades reales
de las pendientes.

## Capabilities and Constraints
Biblioteca local persistente, búsqueda, favoritos, listas y controles nativos.
La suscripción se usa en el reproductor oficial incrustado en la misma ventana,
vía elegida por el usuario para evitar la membresía de desarrollador. Necesita
una cuenta con suscripción y soporte DRM compatible. La integración propia con
MusicKit queda como alternativa futura. No se promete paridad, descargas offline
del catálogo, Dolby Atmos, AirPlay o sincronización local/nube.

## Brand Commitments
Nombre q_AMusik; referencia funcional y visual: Apple Music. Identidad propia,
sin logotipos ni recursos propietarios de Apple.

## Product Principles
- Biblioteca propia siempre disponible sin cuenta.
- Inicio de sesión gestionado por Apple dentro del reproductor integrado.
- Acciones y límites expresados en español.
- No recopilar credenciales ni telemetría.
