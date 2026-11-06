"""Política de navegación del reproductor: no expone funciones nativas a la web."""

from urllib.parse import urlsplit

APPLE_MUSIC_URL = "https://music.apple.com/"


def allowed_navigation(url, fixture_origin=None):
    if url == "about:blank":
        return True  # Ventana de autorización recién creada, sin privilegios.
    try:
        parsed = urlsplit(url)
        if parsed.username is not None or parsed.password is not None:
            return False
        if fixture_origin and parsed.scheme == "http" and parsed.hostname == "127.0.0.1":
            return f"http://127.0.0.1:{parsed.port}" == fixture_origin
        if parsed.scheme != "https" or parsed.port not in (None, 443):
            return False
        host = (parsed.hostname or "").lower()
        return any(host == domain or host.endswith("." + domain)
                   for domain in ("apple.com", "icloud.com"))
    except ValueError:
        return False
