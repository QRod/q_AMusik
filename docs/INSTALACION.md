# Instalar q_AMusik en Ubuntu / Zorin

Versión inicial **0.1.0**. La biblioteca local es nativa; Apple Music se abre en
el navegador. No es todavía un reemplazo completo de la aplicación de macOS.

## Requisitos

- Escritorio Ubuntu 22.04/24.04 o Zorin basado en esas versiones.
- Cuenta con `sudo` para instalar; ejecuta la aplicación con tu usuario habitual.
- Internet para descargar dependencias y escuchar Apple Music.
- Para la suscripción: navegador con reproducción de contenido protegido,
  cuenta de Apple y suscripción activa.

El paquete Python es `all`; APT instala GTK y códecs para la arquitectura de tu
equipo. Las pruebas automatizadas usan Ubuntu x86_64; ARM y Zorin necesitan
confirmación en equipos reales.

## Descargar, verificar e instalar

Desde [la publicación v0.1.0](https://github.com/QRod/q_AMusik/releases/tag/v0.1.0),
descarga `q-amusik_0.1.0_all.deb` y `SHA256SUMS` en una misma carpeta, o usa:

```sh
mkdir -p ~/Descargas/q-AMusik-0.1.0
cd ~/Descargas/q-AMusik-0.1.0
curl -fLO https://github.com/QRod/q_AMusik/releases/download/v0.1.0/q-amusik_0.1.0_all.deb
curl -fLO https://github.com/QRod/q_AMusik/releases/download/v0.1.0/SHA256SUMS
sha256sum -c SHA256SUMS
sudo apt update
sudo apt install ./q-amusik_0.1.0_all.deb
```

Continúa con la instalación sólo si la comprobación muestra `OK`. La suma
detecta daños o discrepancias con el archivo publicado; no es una firma de autor.
Usa `apt install ./archivo.deb` para resolver las dependencias automáticamente.
También puedes abrir el `.deb` con el instalador de paquetes de tu escritorio.

Busca **q_AMusik** en el menú de aplicaciones, o ejecuta:

```sh
q-amusik
```

## Primer uso

1. Pulsa «Añadir carpeta» o «Añadir canciones». Se conservan los archivos originales.
2. Haz doble clic en una canción para reproducirla. Los favoritos y listas de
   esta ventana son locales.
3. Para tu suscripción, elige «Escuchar suscripción» y «Abrir Apple Music e iniciar
   sesión». El inicio de sesión ocurre en el sitio oficial de Apple.

El catálogo, las listas de Apple y su reproducción siguen en el navegador.
No se sincronizan con las listas locales. Si sólo hay avances, comprueba la
cuenta, la suscripción y los permisos de contenido protegido del navegador.

## Actualizar y desinstalar

Para actualizar, descarga el `.deb` de la versión deseada y su `SHA256SUMS`,
verifica la suma y repite `sudo apt install ./nombre-del-paquete.deb`.

```sh
sudo apt remove q-amusik
```

La desinstalación conserva tu biblioteca y no borra archivos de música. Los datos
están en `~/.local/share/q_amusik/`, o `$XDG_DATA_HOME/q_amusik/` si se configuró.
Para un respaldo, cierra q_AMusik y copia ese directorio. Si quieres borrar la
biblioteca, elimínalo desde tu gestor de archivos con la aplicación cerrada.
Las sesiones de Apple se cierran desde el navegador.

## Resolver problemas

- **Dependencias no disponibles:** revisa que los repositorios oficiales de tu
  distribución estén habilitados y ejecuta `sudo apt update`. Algunos códecs
  requieren los componentes adicionales de Ubuntu/Zorin.
- **No hay audio local:** comprueba la salida seleccionada en el escritorio y
  prueba otro archivo. El paquete instala los complementos GStreamer; archivos
  con DRM o dañados pueden no reproducirse.
- **No arranca:** ejecuta `q-amusik` en una terminal y adjunta el error a
  [Issues](https://github.com/QRod/q_AMusik/issues), sin rutas privadas ni credenciales.
- **No abre Apple Music:** abre `https://music.apple.com/` directamente en tu
  navegador. q_AMusik no instala ni modifica módulos DRM.
