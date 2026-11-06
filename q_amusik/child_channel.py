"""Canal privado heredado del contenedor; sólo mensajes de control fijos."""

import json
import socket
from gi.repository import GLib


class ChildChannel:
    def __init__(self, descriptor, command):
        self.socket = socket.socket(fileno=descriptor)
        self.socket.setblocking(False)
        self.command = command
        self.buffer = b""
        self.closed = False
        self.watch = GLib.io_add_watch(descriptor, GLib.IO_IN | GLib.IO_HUP, self.read)

    def send(self, event):
        if not self.closed:
            try:
                self.socket.sendall((json.dumps(event) + "\n").encode())
            except OSError:
                pass

    def read(self, _, condition):
        try:
            data = self.socket.recv(4096)
        except BlockingIOError:
            return True
        except OSError:
            data = b""
        if not data:
            self.watch = 0
            self.command("shutdown")
            return False
        self.buffer += data
        if len(self.buffer) > 8192:
            self.watch = 0
            self.command("shutdown")
            return False
        while b"\n" in self.buffer:
            line, self.buffer = self.buffer.split(b"\n", 1)
            try:
                message = json.loads(line)
            except (ValueError, UnicodeError):
                continue
            if isinstance(message, dict) and message.get("command") in ("library", "pause", "play", "shutdown"):
                self.command(message["command"])
        return not self.closed

    def close(self):
        if not self.closed:
            self.closed = True
            if self.watch:
                GLib.source_remove(self.watch)
            self.socket.close()
