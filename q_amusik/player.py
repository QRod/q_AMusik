"""Motor GStreamer: sólo acepta archivos locales seleccionados en la biblioteca."""

from pathlib import Path
import gi

gi.require_version("Gst", "1.0")
from gi.repository import Gst


class Player:
    def __init__(self, on_end, on_error, on_state):
        Gst.init(None)
        self.pipeline = Gst.ElementFactory.make("playbin", "q-amusik-player")
        if self.pipeline is None:
            raise RuntimeError("Falta el componente playbin de GStreamer.")
        # No renderizar vídeo incrustado en un archivo con extensión de audio.
        self.pipeline.set_property("flags", 2 | 16)  # audio + software volume
        self.playing = False
        self.loaded = False
        self.on_end, self.on_error, self.on_state = on_end, on_error, on_state
        self.bus = self.pipeline.get_bus()
        self.bus.add_signal_watch()
        self.bus.connect("message", self._message)

    def play(self, track):
        self.stop()
        path = Path(track.path)
        if not path.is_file():
            self.on_error("No se encuentra el archivo. Comprueba que la unidad esté conectada.")
            return
        self.pipeline.set_property("uri", path.resolve().as_uri())
        self.loaded = True
        result = self.pipeline.set_state(Gst.State.PLAYING)
        if result == Gst.StateChangeReturn.FAILURE:
            self.stop()
            self.on_error("No se pudo iniciar el dispositivo de audio.")

    def toggle(self):
        if self.loaded:
            self.pipeline.set_state(Gst.State.PAUSED if self.playing else Gst.State.PLAYING)

    def pause(self):
        if self.loaded:
            self.pipeline.set_state(Gst.State.PAUSED)

    def stop(self):
        self.pipeline.set_state(Gst.State.NULL)
        self.loaded = self.playing = False
        self.on_state(False)

    def position(self):
        ok, position = self.pipeline.query_position(Gst.Format.TIME)
        valid, duration = self.pipeline.query_duration(Gst.Format.TIME)
        return (position / Gst.SECOND if ok else 0,
                duration / Gst.SECOND if valid else 0)

    def seek(self, seconds):
        if self.loaded:
            self.pipeline.seek_simple(Gst.Format.TIME, Gst.SeekFlags.FLUSH | Gst.SeekFlags.KEY_UNIT,
                                      int(max(0, seconds) * Gst.SECOND))

    def volume(self, value):
        self.pipeline.set_property("volume", min(1.0, max(0.0, value)))

    def _message(self, bus, message):
        if message.type == Gst.MessageType.ERROR:
            self.stop()
            self.on_error("No se pudo reproducir el archivo. Puede estar dañado o faltar un códec.")
        elif message.type == Gst.MessageType.EOS:
            self.stop()
            self.on_end()
        elif message.type == Gst.MessageType.STATE_CHANGED and message.src == self.pipeline:
            _, current, _ = message.parse_state_changed()
            self.playing = current == Gst.State.PLAYING
            self.on_state(self.playing)

    def close(self):
        self.stop()
        self.bus.remove_signal_watch()
