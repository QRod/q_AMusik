"""Carátulas locales: lectura limitada y decodificación fuera del hilo GTK."""

from collections import OrderedDict
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import math
import weakref

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gdk, GdkPixbuf, Gio, GLib, Gtk

MAX_IMAGE_BYTES = 8 * 1024 * 1024


def image_bytes(path):
    from mutagen import File, MutagenError
    try:
        audio = File(path)
        if audio is not None:
            pictures = getattr(audio, "pictures", [])
            if pictures:
                data = pictures[0].data
                if len(data) <= MAX_IMAGE_BYTES:
                    return data
            tags = audio.tags
            if tags:
                for key in tags:
                    if str(key).startswith("APIC"):
                        data = tags[key].data
                        if len(data) <= MAX_IMAGE_BYTES:
                            return data
                covers = tags.get("covr")
                if covers and len(covers[0]) <= MAX_IMAGE_BYTES:
                    return bytes(covers[0])
    except (OSError, MutagenError, ValueError, AttributeError):
        pass
    for name in ("cover.jpg", "cover.png", "folder.jpg", "folder.png", "Cover.jpg"):
        try:
            with (Path(path).parent / name).open("rb") as stream:
                data = stream.read(MAX_IMAGE_BYTES + 1)
            if len(data) <= MAX_IMAGE_BYTES:
                return data
        except OSError:
            continue
    return None


class ArtworkCache:
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="artwork")
        self.cache = OrderedDict()
        self.pending = {}
        self.waiting = OrderedDict()
        self.active = set()
        self.closed = False

    def request(self, path, size, callback):
        key = (path, size)
        if key in self.cache:
            self.cache.move_to_end(key)
            callback(self.cache[key], path)
            return
        if self.closed:
            return
        reference = weakref.WeakMethod(callback)
        if key in self.pending:
            self.pending[key].append(reference)
            return
        self.pending[key] = [reference]
        self.waiting[key] = None
        self.drain()

    def drain(self):
        while self.waiting and len(self.active) < 8 and not self.closed:
            key, _ = self.waiting.popitem(last=False)
            if not any(reference() for reference in self.pending[key]):
                self.pending.pop(key)
                continue
            self.active.add(key)
            future = self.executor.submit(self.decode, *key)
            future.add_done_callback(lambda job, k=key: GLib.idle_add(self.complete, k, job))

    @staticmethod
    def decode(path, size):
        try:
            data = image_bytes(path)
            if data:
                stream = Gio.MemoryInputStream.new_from_bytes(GLib.Bytes.new(data))
                try:
                    return GdkPixbuf.Pixbuf.new_from_stream_at_scale(stream, size, size, True, None)
                finally:
                    stream.close(None)
        except (GLib.Error, OSError, ValueError):
            pass
        return None

    def complete(self, key, future):
        callbacks = self.pending.pop(key, [])
        self.active.discard(key)
        if self.closed or future.cancelled():
            return False
        try:
            pixbuf = future.result()
        except Exception:
            pixbuf = None
        self.cache[key] = pixbuf
        while len(self.cache) > 128:
            self.cache.popitem(last=False)
        for reference in callbacks:
            callback = reference()
            if callback:
                callback(pixbuf, key[0])
        self.drain()
        return False

    def close(self):
        self.closed = True
        self.pending.clear()
        self.waiting.clear()
        self.executor.shutdown(wait=False, cancel_futures=True)


class Cover(Gtk.DrawingArea):
    def __init__(self, cache, path=None, size=172, round_image=False):
        super().__init__()
        self.set_size_request(size, size)
        self.set_halign(Gtk.Align.CENTER)
        self.set_valign(Gtk.Align.CENTER)
        self.pixbuf = None
        self.round_image = round_image
        self.get_style_context().add_class("cover")
        self.connect("draw", self.draw_cover)
        self.connect("destroy", lambda *_: setattr(self, "alive", False))
        self.alive = True
        self.cache, self.size = cache, size
        if path:
            self.load(path)

    def load(self, path):
        self.pixbuf = None
        self.path = path
        self.cache.request(path, self.size, self.set_art)
        self.queue_draw()

    def set_art(self, pixbuf, path):
        if self.alive and path == self.path:
            self.pixbuf = pixbuf
            self.queue_draw()

    def draw_cover(self, _, cr):
        width, height = self.get_allocated_width(), self.get_allocated_height()
        radius = min(width, height) / 2 if self.round_image else min(8, width / 8)
        cr.new_sub_path()
        for x, y, start in ((width-radius, radius, -90), (width-radius, height-radius, 0),
                            (radius, height-radius, 90), (radius, radius, 180)):
            cr.arc(x, y, radius, math.radians(start), math.radians(start+90))
        cr.close_path()
        cr.clip()
        context = self.get_style_context()
        color = context.get_background_color(Gtk.StateFlags.NORMAL)
        Gdk.cairo_set_source_rgba(cr, color)
        cr.paint()
        if self.pixbuf:
            scale = max(width / self.pixbuf.get_width(), height / self.pixbuf.get_height())
            cr.translate((width-self.pixbuf.get_width()*scale)/2,
                         (height-self.pixbuf.get_height()*scale)/2)
            cr.scale(scale, scale)
            Gdk.cairo_set_source_pixbuf(cr, self.pixbuf, 0, 0)
            cr.paint()
        else:
            color = context.get_color(Gtk.StateFlags.NORMAL)
            Gdk.cairo_set_source_rgba(cr, color)
            cr.translate(width * .32, height * .27)
            cr.scale(width * .35, height * .35)
            cr.set_line_width(.1)
            cr.move_to(.18, .85)
            cr.line_to(.18, .15)
            cr.line_to(.85, 0)
            cr.line_to(.85, .68)
            cr.stroke()
            for x, y in ((.05,.86),(.72,.69)):
                cr.save()
                cr.translate(x,y)
                cr.scale(.21,.14)
                cr.arc(0,0,1,0,math.tau)
                cr.fill()
                cr.restore()
        return False
