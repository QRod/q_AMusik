"""Interfaz de escritorio GTK. El catálogo de Apple permanece en el navegador."""

from pathlib import Path
import sqlite3
import subprocess
import threading
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gdk, Gio, GLib, Gtk
from .apple import open_apple_music
from .library import EXTENSIONS, Library, data_directory
from .player import Player
from .queue import Queue


def label(text, style=None):
    widget = Gtk.Label(label=text, xalign=0)
    if style:
        widget.get_style_context().add_class(style)
    return widget


def button(text, callback, tooltip=None):
    widget = Gtk.Button(label=text)
    widget.connect("clicked", callback)
    if tooltip:
        widget.set_tooltip_text(tooltip)
        widget.get_accessible().set_name(tooltip)
    return widget


def clock(seconds):
    minutes, seconds = divmod(max(0, int(seconds)), 60)
    return f"{minutes}:{seconds:02d}"


class Window(Gtk.ApplicationWindow):
    def __init__(self, app):
        super().__init__(application=app, title="q_AMusik")
        self.set_default_size(1120, 740)
        self.set_size_request(820, 560)
        self.database = data_directory() / "library.db"
        self.library = Library(self.database)
        self.queue = Queue()
        self.view = "songs"
        self.playlist = None
        self.importing = False
        self.updating_seek = False
        self.player = Player(self.advance, self.notify, self.playback_state)
        provider = Gtk.CssProvider()
        provider.load_from_path(str(Path(__file__).with_name("style.css")))
        Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(), provider, 600)
        header = Gtk.HeaderBar(title="q_AMusik", subtitle="Tu música, en Linux")
        header.set_show_close_button(True)
        header.pack_end(button("Añadir carpeta", lambda *_: self.choose(True)))
        header.pack_end(button("Añadir canciones", lambda *_: self.choose(False)))
        self.set_titlebar(header)
        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.add(root)
        body = Gtk.Box()
        root.pack_start(body, True, True, 0)
        sidebar = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        sidebar.set_size_request(210, -1)
        sidebar.get_style_context().add_class("sidebar")
        sidebar.pack_start(label("q_AMusik", "brand"), False, False, 0)
        sidebar.pack_start(label("APPLE MUSIC", "eyebrow"), False, False, 0)
        sidebar.pack_start(button("Escuchar suscripción", lambda *_: self.navigate("apple")), False, False, 0)
        sidebar.pack_start(label("TU BIBLIOTECA", "eyebrow"), False, False, 0)
        for title, view in (("Canciones", "songs"), ("Álbumes", "albums"),
                            ("Artistas", "artists"), ("Favoritos", "favorites")):
            sidebar.pack_start(button(title, lambda _, v=view: self.navigate(v)), False, False, 0)
        sidebar.pack_start(label("LISTAS LOCALES", "eyebrow"), False, False, 0)
        self.playlist_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        playlist_scroll = Gtk.ScrolledWindow()
        playlist_scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        playlist_scroll.add(self.playlist_box)
        sidebar.pack_start(playlist_scroll, True, True, 0)
        sidebar.pack_end(button("+ Nueva lista", self.new_playlist), False, False, 0)
        body.pack_start(sidebar, False, False, 0)
        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        content.set_border_width(24)
        body.pack_start(content, True, True, 0)
        self.title_label = label("Canciones", "page-title")
        content.pack_start(self.title_label, False, False, 0)
        self.search = Gtk.SearchEntry(placeholder_text="Buscar en tu biblioteca local")
        self.search.connect("search-changed", lambda *_: self.refresh())
        content.pack_start(self.search, False, False, 0)
        self.stack = Gtk.Stack()
        content.pack_start(self.stack, True, True, 0)
        self.build_tracks()
        self.build_apple()
        self.status = label("Añade tu música para empezar.", "muted")
        self.status.set_line_wrap(True)
        self.status.set_selectable(True)
        content.pack_end(self.status, False, False, 0)
        self.build_controls(root)
        self.refresh_playlists()
        self.refresh()
        self.connect("destroy", self.cleanup)
        self.timer = GLib.timeout_add(400, self.tick)

    def build_tracks(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        actions = Gtk.Box(spacing=8)
        actions.pack_start(button("Reproducir", self.play_selected), False, False, 0)
        actions.pack_start(button("♥ Favorito", self.favorite), False, False, 0)
        actions.pack_start(button("Añadir a lista", self.add_to_playlist), False, False, 0)
        actions.pack_end(button("Quitar", self.remove_selected, "Quitar referencia; conservar archivo"), False, False, 0)
        box.pack_start(actions, False, False, 0)
        self.store = Gtk.ListStore(int, str, str, str, str, str)
        self.table = Gtk.TreeView(model=self.store)
        self.table.set_enable_search(False)
        self.table.get_selection().set_mode(Gtk.SelectionMode.MULTIPLE)
        for index, name in enumerate(("", "Título", "Artista", "Álbum", "Tiempo"), 1):
            cell = Gtk.CellRendererText()
            cell.set_property("ellipsize", 3)
            column = Gtk.TreeViewColumn(name, cell, text=index)
            column.set_resizable(True)
            column.set_expand(index in (2, 3, 4))
            if index in (2, 3, 4):
                column.set_min_width(100)
            self.table.append_column(column)
        self.table.connect("row-activated", lambda *_: self.play_selected())
        scroll = Gtk.ScrolledWindow()
        scroll.add(self.table)
        box.pack_start(scroll, True, True, 0)
        self.empty = label("Tu biblioteca empieza aquí. Añade canciones o una carpeta.", "muted")
        self.empty.set_line_wrap(True)
        box.pack_start(self.empty, False, False, 0)
        self.stack.add_named(box, "library")

    def build_apple(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        box.pack_start(label("Tu suscripción de Apple Music", "section-title"), False, False, 20)
        text = label("Escucha tu catálogo, radio y listas en el reproductor oficial de Apple.\n\n"
                     "Se abrirá en tu navegador. Inicia sesión allí con tu cuenta de Apple "
                     "y una suscripción activa.\n\nLos controles de esta ventana corresponden "
                     "a tus archivos locales. La integración del catálogo dentro de q_AMusik "
                     "está pendiente.")
        text.set_line_wrap(True)
        text.set_max_width_chars(65)
        box.pack_start(text, False, False, 0)
        launch = button("Abrir Apple Music e iniciar sesión", self.launch_apple)
        launch.get_style_context().add_class("suggested-action")
        launch.set_halign(Gtk.Align.START)
        box.pack_start(launch, False, False, 0)
        note = label("Si sólo escuchas avances, comprueba tu cuenta, suscripción y los permisos "
                     "de contenido protegido del navegador. No se incluyen descargas offline "
                     "del catálogo ni se garantiza paridad con macOS.", "muted")
        note.set_line_wrap(True)
        note.set_max_width_chars(65)
        box.pack_start(note, False, False, 0)
        self.stack.add_named(box, "apple")

    def build_controls(self, root):
        panel = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        panel.get_style_context().add_class("player")
        row = Gtk.Box(spacing=12)
        self.now = label("Sin reproducción", "now-playing")
        self.now.set_ellipsize(3)
        self.now.set_size_request(180, -1)
        row.pack_start(self.now, True, True, 0)
        row.pack_start(button("⏮", self.previous, "Canción anterior"), False, False, 0)
        self.play_button = button("▶", self.toggle, "Reproducir o pausar")
        row.pack_start(self.play_button, False, False, 0)
        row.pack_start(button("⏭", lambda *_: self.advance(False), "Canción siguiente"), False, False, 0)
        shuffle = Gtk.ToggleButton(label="Aleatorio")
        shuffle.connect("toggled", lambda b: setattr(self.queue, "shuffle", b.get_active()))
        row.pack_start(shuffle, False, False, 0)
        self.repeat = button("Repetir: no", self.repeat_mode)
        row.pack_start(self.repeat, False, False, 0)
        volume = Gtk.VolumeButton()
        volume.set_value(0.8)
        self.player.volume(0.8)
        volume.connect("value-changed", lambda _, v: self.player.volume(v))
        volume.set_tooltip_text("Volumen local")
        row.pack_end(volume, False, False, 0)
        panel.pack_start(row, False, False, 0)
        timeline = Gtk.Box(spacing=10)
        self.elapsed, self.duration = label("0:00"), label("0:00")
        self.seek = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, 1, 1)
        self.seek.set_draw_value(False)
        self.seek.get_accessible().set_name("Posición de reproducción local")
        self.seek.connect("change-value", self.seek_to)
        timeline.pack_start(self.elapsed, False, False, 0)
        timeline.pack_start(self.seek, True, True, 0)
        timeline.pack_end(self.duration, False, False, 0)
        panel.pack_start(timeline, False, False, 0)
        root.pack_end(panel, False, False, 0)

    def notify(self, text):
        self.status.set_text(text)

    def navigate(self, view, playlist=None, title=None):
        self.view, self.playlist = view, playlist
        names = dict(songs="Canciones", albums="Álbumes", artists="Artistas",
                     favorites="Favoritos", apple="Apple Music", playlist="Lista")
        self.title_label.set_text(title or names[view])
        self.search.set_visible(view != "apple")
        self.stack.set_visible_child_name("apple" if view == "apple" else "library")
        self.refresh()

    def refresh(self):
        self.visible_tracks = self.library.tracks(self.search.get_text(), self.view == "favorites", self.playlist)
        if self.view == "albums":
            self.visible_tracks.sort(key=lambda t: (t.album.casefold(), t.artist.casefold(), t.title.casefold()))
        self.store.clear()
        for track in self.visible_tracks:
            self.store.append([track.id, "♥" if track.favorite else "", track.title,
                               track.artist, track.album, clock(track.duration)])
        self.empty.set_visible(not self.visible_tracks)
        self.empty.set_text("No hay coincidencias." if self.search.get_text() else
                            "No hay canciones en esta vista. Añade música a tu biblioteca o lista.")
        if self.view != "apple" and not self.importing:
            self.notify(f"{len(self.visible_tracks)} canciones · Los archivos originales se conservan en su ubicación.")

    def selected(self):
        model, paths = self.table.get_selection().get_selected_rows()
        return [model[path][0] for path in paths]

    def play_selected(self, *_):
        ids = self.selected()
        if not self.visible_tracks:
            return self.notify("Añade canciones a tu biblioteca para reproducir.")
        index = next((i for i, t in enumerate(self.visible_tracks) if ids and t.id == ids[0]), 0)
        self.play(self.queue.start(self.visible_tracks, index))

    def play(self, track):
        if track:
            self.now.set_text(f"{track.title} · {track.artist}")
            self.now.set_tooltip_text(f"{track.title}\n{track.artist}\n{track.album}")
            self.player.play(track)

    def toggle(self, *_):
        if self.player.loaded:
            self.player.toggle()
        elif self.queue.current:
            self.play(self.queue.current)
        else:
            self.play_selected()

    def advance(self, automatic=True):
        track = self.queue.next(automatic)
        if track:
            self.play(track)
        else:
            self.player.stop()

    def previous(self, *_):
        if self.player.position()[0] > 3:
            self.player.seek(0)
        else:
            self.play(self.queue.previous())

    def playback_state(self, playing):
        if hasattr(self, "play_button"):
            self.play_button.set_label("⏸" if playing else "▶")

    def repeat_mode(self, *_):
        modes = ["off", "all", "one"]
        self.queue.repeat = modes[(modes.index(self.queue.repeat) + 1) % 3]
        self.repeat.set_label("Repetir: " + {"off": "no", "all": "todo", "one": "una"}[self.queue.repeat])

    def tick(self):
        position, duration = self.player.position()
        self.updating_seek = True
        self.seek.set_range(0, max(1, duration))
        self.seek.set_value(position)
        self.updating_seek = False
        self.seek.set_sensitive(self.player.loaded and duration > 0)
        self.elapsed.set_text(clock(position))
        self.duration.set_text(clock(duration))
        return True

    def seek_to(self, _, scroll, value):
        if not self.updating_seek:
            self.player.seek(value)
        return False

    def favorite(self, *_):
        if self.importing:
            return self.notify("Espera a que termine la importación para editar favoritos.")
        ids = self.selected()
        for track_id in ids:
            self.library.toggle_favorite(track_id)
        self.refresh()
        if not ids:
            self.notify("Selecciona una o más canciones para marcar favoritas.")

    def choose(self, folder):
        if self.importing:
            return self.notify("Espera a que termine la importación actual.")
        chooser = Gtk.FileChooserNative.new("Añadir música", self,
                    Gtk.FileChooserAction.SELECT_FOLDER if folder else Gtk.FileChooserAction.OPEN,
                    "Añadir", "Cancelar")
        chooser.set_select_multiple(True)
        if not folder:
            audio_filter = Gtk.FileFilter()
            audio_filter.set_name("Archivos de audio")
            for suffix in EXTENSIONS:
                audio_filter.add_pattern("*" + suffix)
                audio_filter.add_pattern("*" + suffix.upper())
            chooser.add_filter(audio_filter)
        if chooser.run() == Gtk.ResponseType.ACCEPT:
            paths = chooser.get_filenames()
            self.importing = True
            self.notify("Importando música… Puedes seguir usando la aplicación.")
            threading.Thread(target=self.import_worker, args=(paths,), daemon=True).start()
        chooser.destroy()

    def import_worker(self, paths):
        library = None
        try:
            library = Library(self.database)
            added, skipped = library.import_paths(paths)
            message = f"Importación terminada: {added} nuevas · {skipped} ya estaban en la biblioteca."
        except (OSError, sqlite3.Error):
            message = ("La importación quedó incompleta; se conservaron los lotes terminados. "
                       "Comprueba permisos y espacio disponible; puedes volver a intentarlo.")
        finally:
            if library:
                library.close()
        GLib.idle_add(self.import_finished, message)

    def import_finished(self, message):
        self.importing = False
        self.refresh()
        self.notify(message)
        return False

    def new_playlist(self, *_):
        if self.importing:
            return self.notify("Espera a que termine la importación para crear listas.")
        dialog = Gtk.Dialog(title="Nueva lista local", transient_for=self, modal=True)
        dialog.add_buttons("Cancelar", Gtk.ResponseType.CANCEL, "Crear", Gtk.ResponseType.OK)
        entry = Gtk.Entry(placeholder_text="Nombre de la lista", max_length=100)
        entry.set_margin_top(16)
        entry.set_margin_bottom(16)
        entry.set_margin_start(16)
        entry.set_margin_end(16)
        dialog.get_content_area().add(entry)
        dialog.show_all()
        if dialog.run() == Gtk.ResponseType.OK:
            try:
                playlist_id = self.library.create_playlist(entry.get_text())
                self.refresh_playlists()
                self.navigate("playlist", playlist_id, entry.get_text().strip())
            except (ValueError, sqlite3.IntegrityError):
                self.notify("Usa un nombre nuevo de entre 1 y 100 caracteres.")
        dialog.destroy()

    def refresh_playlists(self):
        for child in self.playlist_box.get_children():
            child.destroy()
        for playlist_id, name in self.library.playlists():
            item = button(name, lambda _, p=playlist_id, n=name: self.navigate("playlist", p, n), name)
            item.get_child().set_ellipsize(3)
            self.playlist_box.pack_start(item, False, False, 0)
        self.playlist_box.show_all()

    def add_to_playlist(self, *_):
        if self.importing:
            return self.notify("Espera a que termine la importación para editar listas.")
        ids = self.selected()
        playlists = self.library.playlists()
        if not ids or not playlists:
            return self.notify("Selecciona canciones y crea una lista local primero.")
        dialog = Gtk.Dialog(title="Añadir a lista", transient_for=self, modal=True)
        dialog.add_buttons("Cancelar", Gtk.ResponseType.CANCEL, "Añadir", Gtk.ResponseType.OK)
        combo = Gtk.ComboBoxText()
        for playlist_id, name in playlists:
            combo.append(str(playlist_id), name)
        combo.set_active(0)
        combo.set_border_width(16)
        dialog.get_content_area().add(combo)
        dialog.show_all()
        if dialog.run() == Gtk.ResponseType.OK:
            for track_id in ids:
                self.library.add_to_playlist(int(combo.get_active_id()), track_id)
            self.notify(f"{len(ids)} canciones añadidas a la lista.")
        dialog.destroy()

    def remove_selected(self, *_):
        if self.importing:
            return self.notify("Espera a que termine la importación para quitar canciones.")
        ids = self.selected()
        if not ids:
            return self.notify("Selecciona las canciones que quieres quitar.")
        for track_id in ids:
            self.library.remove(track_id, self.playlist)
        current = self.queue.current
        if current and current.id in ids:
            self.player.stop()
        # Reconstruir la cola evita reproducir referencias quitadas desde esta vista.
        remaining = [t for t in self.queue.tracks if t.id not in ids]
        index = next((i for i, t in enumerate(remaining) if current and t.id == current.id), -1)
        self.queue.start(remaining, index)
        self.refresh()

    def launch_apple(self, *_):
        self.player.pause()
        def launch():
            try:
                open_apple_music()
                message = "Apple Music se ha abierto en el navegador. Inicia sesión allí."
            except (OSError, RuntimeError, subprocess.SubprocessError):
                message = "No se pudo abrir el navegador. Abre https://music.apple.com/ en un navegador compatible."
            GLib.idle_add(self.notify, message)
        threading.Thread(target=launch, daemon=True).start()

    def cleanup(self, *_):
        GLib.source_remove(self.timer)
        self.player.close()
        self.library.close()


class Application(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="io.github.qrod.qAMusik", flags=Gio.ApplicationFlags.FLAGS_NONE)

    def do_activate(self):
        window = self.get_active_window()
        if window is None:
            window = Window(self)
            window.show_all()
            window.empty.set_visible(not window.visible_tracks)
        window.present()


def main():
    import sys
    return Application().run(sys.argv)
