import unittest
from q_amusik.queue import Queue


class QueueTests(unittest.TestCase):
    def setUp(self):
        self.queue = Queue()
        self.queue.start(["a", "b", "c"])

    def test_end_stops_without_wrapping(self):
        self.assertEqual(self.queue.next(), "b")
        self.assertEqual(self.queue.next(), "c")
        self.assertIsNone(self.queue.next(automatic=True))

    def test_repeat_one_applies_to_eos_but_not_manual_next(self):
        self.queue.repeat = "one"
        self.assertEqual(self.queue.next(automatic=True), "a")
        self.assertEqual(self.queue.next(automatic=False), "b")

    def test_repeat_all_wraps(self):
        self.queue.repeat = "all"
        for _ in range(3):
            self.queue.next()
        self.assertEqual(self.queue.current, "a")

    def test_shuffle_previous_uses_history(self):
        self.queue.shuffle = True
        self.assertNotEqual(self.queue.next(), "a")
        self.assertEqual(self.queue.previous(), "a")

    def test_empty_queue(self):
        self.queue.start([])
        self.assertIsNone(self.queue.current)
        self.assertIsNone(self.queue.next())
        self.assertIsNone(self.queue.previous())


if __name__ == "__main__":
    unittest.main()
