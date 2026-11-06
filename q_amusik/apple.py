"""Abre exclusivamente el sitio oficial, sin acceso a las cookies del navegador."""

import shutil
import subprocess

APPLE_MUSIC_URL = "https://music.apple.com/"


def open_apple_music():
    # App mode conserva DRM y autenticación en el navegador instalado por el usuario.
    for name in ("google-chrome-stable", "google-chrome", "chromium", "chromium-browser"):
        executable = shutil.which(name)
        if executable:
            subprocess.Popen([executable, "--app=" + APPLE_MUSIC_URL],
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return
    executable = shutil.which("xdg-open")
    if not executable:
        raise RuntimeError("Instala un navegador compatible y xdg-utils para abrir Apple Music.")
    subprocess.run([executable, APPLE_MUSIC_URL], check=True, timeout=15,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
