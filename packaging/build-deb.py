#!/usr/bin/env python3
"""Construye un .deb independiente de arquitectura con herramientas de Debian."""

from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from q_amusik import __version__


def main():
    if not shutil.which("dpkg-deb"):
        raise SystemExit("Construye en Ubuntu/Zorin con dpkg-deb instalado (paquete dpkg).")
    output = ROOT / "dist"
    output.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="q-amusik-deb-") as directory:
        package = Path(directory)
        app = package / "usr/share/q-amusik/q_amusik"
        shutil.copytree(ROOT / "q_amusik", app, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        files = {
            "packaging/q-amusik": "usr/bin/q-amusik",
            "packaging/io.github.qrod.qAMusik.desktop": "usr/share/applications/io.github.qrod.qAMusik.desktop",
            "assets/io.github.qrod.qAMusik.svg": "usr/share/icons/hicolor/scalable/apps/io.github.qrod.qAMusik.svg",
            "README.md": "usr/share/doc/q-amusik/README.md",
        }
        for source, destination in files.items():
            target = package / destination
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / source, target)
        (package / "usr/bin/q-amusik").chmod(0o755)
        control = package / "DEBIAN/control"
        control.parent.mkdir()
        control.write_text(f"""Package: q-amusik
Version: {__version__}
Architecture: all
Maintainer: q_AMusik contributors
Section: sound
Priority: optional
Depends: python3 (>= 3.10), python3-gi, python3-mutagen, gir1.2-gtk-3.0, gir1.2-gstreamer-1.0, gstreamer1.0-plugins-base, gstreamer1.0-plugins-good, gstreamer1.0-plugins-bad, gstreamer1.0-libav, gstreamer1.0-pulseaudio, xdg-utils
Description: Biblioteca musical nativa para Ubuntu y Zorin
 Reproduce archivos locales y abre el reproductor oficial de Apple Music.
""", encoding="utf-8")
        target = output / f"q-amusik_{__version__}_all.deb"
        subprocess.run(["dpkg-deb", "--root-owner-group", "--build", str(package), str(target)], check=True)
        print(target)


if __name__ == "__main__":
    main()
