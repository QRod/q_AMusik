import importlib.util
import unittest
from unittest.mock import patch

HAS_GI = importlib.util.find_spec("gi") is not None
if HAS_GI:
    from gi.repository import GLib
    from q_amusik.artwork import ArtworkCache


@unittest.skipUnless(HAS_GI, "Carátulas GTK se prueban en Linux con PyGObject")
class ArtworkTests(unittest.TestCase):
    def test_large_batch_delivers_every_requested_cover(self):
        class Receiver:
            def __init__(self):
                self.paths = set()

            def receive(self, image, path):
                self.paths.add(path)

        receiver = Receiver()
        cache = ArtworkCache()
        loop = GLib.MainLoop()
        def poll():
            if len(receiver.paths) == 240:
                loop.quit()
                return False
            return True
        def timeout():
            loop.quit()
            return False
        with patch.object(ArtworkCache, "decode", return_value=None):
            for index in range(240):
                cache.request(str(index), 170, receiver.receive)
            poll_id = GLib.timeout_add(5, poll)
            timeout_id = GLib.timeout_add(3000, timeout)
            loop.run()
        if len(receiver.paths) == 240:
            GLib.source_remove(timeout_id)
        else:
            GLib.source_remove(poll_id)
        cache.close()
        self.assertEqual(len(receiver.paths), 240)
        self.assertLessEqual(len(cache.cache), 128)
