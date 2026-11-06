from pathlib import Path
import tempfile
import threading
import unittest

from q_amusik.library import Library, audio_files


def tags(path):
    return dict(title=path.stem, artist="Artista", album="Álbum", duration=120)


class LibraryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.library = Library(self.root / "library.db")
        self.song = self.root / "Música ' especial.mp3"
        self.song.write_bytes(b"fixture")

    def tearDown(self):
        self.library.close()
        self.tmp.cleanup()

    def test_recursive_import_deduplicates_and_ignores_non_audio(self):
        (self.root / "ignore.txt").write_text("text")
        nested = self.root / "album"
        nested.mkdir()
        (nested / "segunda.FLAC").write_bytes(b"fixture")
        self.assertEqual(self.library.import_paths([self.root, self.song], tags), (2, 0))
        self.assertEqual(self.library.import_paths([self.root], tags), (0, 2))

    def test_favorites_search_and_persistence(self):
        self.library.import_paths([self.song], tags)
        song = self.library.tracks()[0]
        self.library.toggle_favorite(song.id)
        self.assertEqual(self.library.tracks(favorites=True)[0].id, song.id)
        self.assertEqual(len(self.library.tracks(search="ESPECIAL")), 1)
        self.assertEqual(len(self.library.tracks(search="ÁLBUM")), 1)
        self.assertEqual(len(self.library.tracks(search="' OR 1=1 --")), 0)
        self.assertEqual(len(self.library.tracks(search="%")), 0)
        second = Library(self.root / "library.db")
        self.assertTrue(second.tracks()[0].favorite)
        second.close()

    def test_playlist_removal_preserves_library_and_file(self):
        self.library.import_paths([self.song], tags)
        song = self.library.tracks()[0]
        playlist = self.library.create_playlist("Mi lista")
        self.library.add_to_playlist(playlist, song.id)
        self.library.add_to_playlist(playlist, song.id)
        self.assertEqual(len(self.library.tracks(playlist=playlist)), 1)
        self.library.remove(song.id, playlist)
        self.assertEqual(self.library.tracks(playlist=playlist), [])
        self.assertEqual(len(self.library.tracks()), 1)
        self.assertTrue(self.song.exists())

    def test_library_removal_cascades_without_deleting_audio(self):
        self.library.import_paths([self.song], tags)
        song = self.library.tracks()[0]
        playlist = self.library.create_playlist("Mi lista")
        self.library.add_to_playlist(playlist, song.id)
        self.library.remove(song.id)
        self.assertEqual(self.library.tracks(), [])
        self.assertEqual(self.library.tracks(playlist=playlist), [])
        self.assertTrue(self.song.exists())

    def test_playlist_validation_and_sql_names(self):
        for invalid in (" ", "x" * 101):
            with self.assertRaises(ValueError):
                self.library.create_playlist(invalid)
        name = "'); DROP TABLE tracks; --"
        self.library.create_playlist(name)
        self.assertEqual(self.library.playlists()[0][1], name)
        self.assertEqual(self.library.tracks(), [])

    def test_symlink_loop_is_not_followed(self):
        (self.root / "loop").symlink_to(self.root, target_is_directory=True)
        self.assertEqual(list(audio_files([self.root])), [self.song.resolve()])

    def test_slow_metadata_does_not_lock_favorite_writes(self):
        self.library.import_paths([self.song], tags)
        track = self.library.tracks()[0]
        other = self.root / "otra.mp3"
        other.write_bytes(b"fixture")
        waiting, release = threading.Event(), threading.Event()
        errors = []

        def slow_tags(path):
            if path == other.resolve():
                waiting.set()
                if not release.wait(5):
                    raise RuntimeError("Test timed out")
            return tags(path)

        def worker():
            connection = Library(self.root / "library.db")
            try:
                connection.import_paths([self.song, other], slow_tags)
            except Exception as error:
                errors.append(error)
            finally:
                connection.close()

        thread = threading.Thread(target=worker)
        thread.start()
        try:
            self.assertTrue(waiting.wait(5))
            self.library.db.execute("PRAGMA busy_timeout = 50")
            self.library.toggle_favorite(track.id)
            self.assertTrue(self.library.tracks(favorites=True)[0].favorite)
        finally:
            release.set()
            thread.join(5)
        self.assertFalse(thread.is_alive())
        self.assertEqual(errors, [])


if __name__ == "__main__":
    unittest.main()
