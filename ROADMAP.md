# Camino hacia un cliente completo

## 0.1 · Base implementada
- Interfaz GTK nativa en español, biblioteca SQLite y motor GStreamer.
- Importación, búsqueda, favoritos y listas locales; controles de reproducción.
- Acceso explícito al sitio de Apple en el navegador.
- Constructor Debian y flujo de pruebas Ubuntu preparados.

## Próximo hito · Validación en Linux
- Ejecutar las pruebas nativas y revisar las capturas en Ubuntu/Zorin.
- Probar salida de audio real, cambios de dispositivo y formatos/códecs.
- Probar inicio de sesión y reproducción completa del servicio en el navegador.
- Entregar un .deb sólo después de verificar instalación y desinstalación.

## Integración del catálogo en la interfaz propia
- Configurar un identificador de medios y un firmante de tokens MusicKit bajo
  la cuenta de desarrollador del propietario; claves privadas fuera del cliente.
- Prototipar reproducción oficial en Linux con DRM antes de fijar el motor web.
- Integrar autorización de Apple, storefront, catálogo, búsqueda y biblioteca.
- Manejar caducidad de sesión, restricciones de cuenta y errores de suscripción.
- Listas de Apple, cola, favoritos y letras sólo donde la API lo permita.

## Reproductor local avanzado
- Carátulas, cuadrícula de álbumes, páginas de artista y orden por pista/disco.
- Renombrar/eliminar listas, reordenar cola y listas e importar/exportar M3U.
- Integración MPRIS, teclas multimedia, preferencias y persistencia de volumen.
- Detección de cambios en carpetas y archivos movidos; bibliotecas grandes.

## Funciones que requieren investigación
Descargas offline del servicio, lossless del catálogo, Dolby Atmos, AirPlay,
sincronización de archivos locales a la nube y funciones exclusivas de macOS.
No se promete disponibilidad de estas funciones mediante APIs públicas.
