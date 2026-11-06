"""Cola independiente del toolkit para verificar navegación y repetición."""

import random


class Queue:
    def __init__(self):
        self.tracks = []
        self.index = -1
        self.shuffle = False
        self.repeat = "off"
        self.history = []

    @property
    def current(self):
        return self.tracks[self.index] if 0 <= self.index < len(self.tracks) else None

    def start(self, tracks, index=0):
        self.tracks = list(tracks)
        self.index = index if 0 <= index < len(self.tracks) else -1
        self.history = []
        return self.current

    def next(self, automatic=False):
        if not self.tracks:
            return None
        if automatic and self.repeat == "one":
            return self.current
        previous = self.index
        if self.shuffle and len(self.tracks) > 1:
            self.index = random.choice([i for i in range(len(self.tracks)) if i != self.index])
        elif self.index + 1 < len(self.tracks):
            self.index += 1
        elif self.repeat == "all":
            self.index = 0
        else:
            return None
        if previous >= 0:
            self.history.append(previous)
            self.history = self.history[-1000:]
        return self.current

    def previous(self):
        if not self.tracks:
            return None
        self.index = self.history.pop() if self.history else max(0, self.index - 1)
        return self.current
