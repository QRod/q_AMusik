"""Persistencia local; nunca lee cuentas, cookies ni credenciales de Apple."""

from dataclasses import dataclass
from pathlib import Path
import os
import sqlite3

EXTENSIONS = {".mp3", ".flac", ".ogg", ".opus", ".m4a", ".aac", ".wav", ".aiff", ".aif"}


@dataclass(frozen=True)
class Track:
    id: int
    path: str
    title: str
    artist: str
    album: str
    duration: float
    favorite: bool


def data_directory() -> Path:
    base = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local/share"))
    if not base.is_absolute():
        base = Path.home() / ".local/share"
    directory = base / "q_amusik"
    directory.mkdir(mode=0o700, parents=True, exist_ok=True)
    return directory


def audio_files(paths):
    """Recorre carpetas sin seguir enlaces a directorios; elimina duplicados."""
    seen = set()
    for source in paths:
        root = Path(source)
        if root.is_dir():
            candidates = (Path(base) / name for base, _, names in os.walk(root)
                          for name in names)
        else:
            candidates = iter([root])
        for candidate in candidates:
            if candidate.suffix.lower() in EXTENSIONS and candidate.is_file():
                resolved = str(candidate.resolve())
                if resolved not in seen:
                    seen.add(resolved)
                    yield Path(resolved)


def metadata(path: Path) -> dict:
    from mutagen import File, MutagenError

    result = dict(title=path.stem, artist="Artista desconocido",
                  album="Sin álbum", duration=0.0)
    try:
        media = File(path, easy=True)
        if media is not None:
            for key in ("title", "artist", "album"):
                values = media.get(key)
                if values:
                    result[key] = str(values[0])[:1000]
            result["duration"] = max(0.0, float(media.info.length))
    except (MutagenError, OSError, ValueError, AttributeError):
        pass  # GStreamer decidirá si puede decodificar un archivo sin etiquetas.
    return result


class Library:
    def __init__(self, path: Path):
        self.db = sqlite3.connect(path, timeout=15)
        self.db.create_function("casefold", 1, str.casefold, deterministic=True)
        self.db.execute("PRAGMA foreign_keys = ON")
        self.db.execute("PRAGMA journal_mode = WAL")
        self.db.executescript("""
            CREATE TABLE IF NOT EXISTS tracks (
                id INTEGER PRIMARY KEY, path TEXT UNIQUE NOT NULL,
                title TEXT NOT NULL, artist TEXT NOT NULL, album TEXT NOT NULL,
                duration REAL NOT NULL DEFAULT 0,
                favorite INTEGER NOT NULL DEFAULT 0);
            CREATE TABLE IF NOT EXISTS playlists (
                id INTEGER PRIMARY KEY, name TEXT UNIQUE NOT NULL);
            CREATE TABLE IF NOT EXISTS playlist_tracks (
                playlist_id INTEGER REFERENCES playlists(id) ON DELETE CASCADE,
                track_id INTEGER REFERENCES tracks(id) ON DELETE CASCADE,
                PRIMARY KEY (playlist_id, track_id));
        """)

    def close(self):
        self.db.close()

    def import_paths(self, paths, read_metadata=metadata) -> tuple[int, int]:
        added = skipped = 0
        batch = []

        def save_batch():
            count = 0
            with self.db:
                for values in batch:
                    cursor = self.db.execute("""
                        INSERT INTO tracks(path,title,artist,album,duration)
                        VALUES(?,?,?,?,?) ON CONFLICT(path) DO NOTHING
                    """, values)
                    count += cursor.rowcount
            return count

        for path in audio_files(paths):
            # Leer archivos puede ser lento; nunca retener un bloqueo SQL aquí.
            tags = read_metadata(path)
            batch.append((str(path), tags["title"], tags["artist"], tags["album"], tags["duration"]))
            if len(batch) == 64:
                count = save_batch()
                added += count
                skipped += len(batch) - count
                batch.clear()
        if batch:
            count = save_batch()
            added += count
            skipped += len(batch) - count
        return added, skipped

    def tracks(self, search="", favorites=False, playlist=None) -> list[Track]:
        query = "SELECT t.* FROM tracks t WHERE 1=1"
        params = []
        if search:
            query += " AND instr(casefold(t.title || ' ' || t.artist || ' ' || t.album), casefold(?)) > 0"
            params.append(search)
        if favorites:
            query += " AND t.favorite = 1"
        if playlist is not None:
            query += " AND t.id IN (SELECT track_id FROM playlist_tracks WHERE playlist_id = ?)"
            params.append(playlist)
        query += " ORDER BY t.artist COLLATE NOCASE, t.album COLLATE NOCASE, t.title COLLATE NOCASE"
        return [Track(*row[:-1], bool(row[-1])) for row in self.db.execute(query, params)]

    def toggle_favorite(self, track_id):
        with self.db:
            self.db.execute("UPDATE tracks SET favorite = 1 - favorite WHERE id = ?", (track_id,))

    def playlists(self):
        return self.db.execute("SELECT id, name FROM playlists ORDER BY name COLLATE NOCASE").fetchall()

    def create_playlist(self, name):
        name = name.strip()
        if not name or len(name) > 100:
            raise ValueError("Escribe un nombre de entre 1 y 100 caracteres.")
        with self.db:
            cursor = self.db.execute("INSERT INTO playlists(name) VALUES(?)", (name,))
        return cursor.lastrowid

    def add_to_playlist(self, playlist_id, track_id):
        with self.db:
            self.db.execute("INSERT OR IGNORE INTO playlist_tracks VALUES(?,?)", (playlist_id, track_id))

    def remove(self, track_id, playlist=None):
        """Quita una referencia de la biblioteca/lista; nunca borra el audio."""
        with self.db:
            if playlist is None:
                self.db.execute("DELETE FROM tracks WHERE id = ?", (track_id,))
            else:
                self.db.execute("DELETE FROM playlist_tracks WHERE playlist_id = ? AND track_id = ?",
                                (playlist, track_id))
