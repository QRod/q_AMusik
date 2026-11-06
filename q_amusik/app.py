"""Interfaz de escritorio GTK. El catálogo de Apple permanece en el navegador."""

import sqlite3
import os
import threading
import gi

gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
from gi.repository import Gdk, Gio, GLib, Gtk
from .library import EXTENSIONS, Library, data_directory
from .player import Player
from .queue import Queue
from .interface import Interface


def clock(seconds):
    minutes, seconds = divmod(max(0, int(seconds)), 60)
    return f"{minutes}:{seconds:02d}"


EMBEDDED = os.environ.get("Q_AMUSIK_EMBEDDED") == "1"
WindowBase = Gtk.Plug if EMBEDDED else Gtk.ApplicationWindow


class Window(Interface, WindowBase):
    def __init__(self, app):
        super().__init__(application=app, title="q_AMusik")
        self.embedded_header = None
        if EMBEDDED:
            self.set_decorated(False)
        self.desktop_channel = None
        if EMBEDDED:
            from .child_channel import ChildChannel
            self.desktop_channel = ChildChannel(int(os.environ["Q_AMUSIK_CONTROL_FD"]), self.desktop_command)
        self.database = data_directory() / "library.db"
        self.library = Library(self.database)
        self.queue = Queue()
        self.view = "recent"
        self.playlist = None
        self.importing = False
        self.updating_seek = False
        self.player = Player(self.advance, self.notify, self.playback_state)
        self.setup_interface()
        self.refresh_playlists()
        self.refresh()
        self.connect("destroy", self.cleanup)
        self.timer = GLib.timeout_add(400, self.tick)
        if EMBEDDED:
            if os.environ.get("Q_AMUSIK_TEST_AUDIO") == "1":
                from gi.repository import Gst
                sink = Gst.ElementFactory.make("fakesink")
                sink.set_property("sync", True)
                self.player.pipeline.set_property("audio-sink", sink)
            GLib.idle_add(self.desktop_ready)

    def set_titlebar(self, header):
        if EMBEDDED:
            # Un Gtk.Plug no debe crear una decoración CSD cuyo XID cambie
            # cuando Qt lo aloja. La barra es contenido de la biblioteca.
            self.embedded_header = header
            header.set_show_close_button(False)
        else:
            super().set_titlebar(header)

    def desktop_ready(self):
        self.desktop_channel.send({"event": "ready", "xid": int(self.get_id())})
        return False

    def desktop_command(self, command):
        if command == "pause":
            self.player.pause()
        elif command == "play":
            self.play_selected()
        elif command == "library":
            self.navigate("recent")
        elif command == "shutdown":
            self.destroy()

    def search_changed(self, *_):
        if self.view == "apple" and self.search.get_text():
            self.navigate("songs")
        else:
            self.refresh()

    def notify(self, text):
        self.status.set_text(text)
        self.status.set_visible(bool(text))

    def navigate(self, view, playlist=None, title=None):
        if view == "apple" and self.desktop_channel:
            self.launch_apple()
            return
        self.view, self.playlist = view, playlist
        self.collection = None
        self.album_limit = 120
        names = dict(recent="Añadido recientemente", songs="Canciones", albums="Álbumes",
                     artists="Artistas", favorites="Favoritos", apple="Apple Music", playlist="Lista")
        self.title_label.set_text(title or names[view])
        self.stack.set_visible_child_name("apple" if view == "apple" else "library")
        self.refresh()
        self.update_navigation()

    def refresh(self):
        selected_ids = set(self.selected())
        self.visible_tracks = self.library.tracks(self.search.get_text(), self.view == "favorites", self.playlist)
        if self.collection is not None:
            self.visible_tracks = [track for track in self.visible_tracks if track.id in self.collection]
        if self.view == "recent" and self.collection is None:
            self.visible_tracks.sort(key=lambda track: track.id, reverse=True)
        elif self.view == "albums":
            self.visible_tracks.sort(key=lambda track: (track.album.casefold(), track.artist.casefold(), track.title.casefold()))
        self.store.clear()
        for track in self.visible_tracks:
            self.store.append([track.id, "starred-symbolic" if track.favorite else "", track.title,
                               track.artist, track.album, clock(track.duration)])
        for row in self.store:
            if row[0] in selected_ids:
                self.table.get_selection().select_iter(row.iter)
        self.render_library()
        if not self.importing:
            self.notify("")

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
            self.now.set_text(track.title)
            self.now_artist.set_text(track.artist)
            self.now_cover.load(track.path)
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
        if self.desktop_channel:
            self.desktop_channel.send({"event": "playing", "value": playing})
        if hasattr(self, "play_button"):
            name = "media-playback-pause-symbolic" if playing else "media-playback-start-symbolic"
            self.play_button.set_image(Gtk.Image.new_from_icon_name(name, Gtk.IconSize.BUTTON))

    def repeat_mode(self, *_):
        modes = ["off", "all", "one"]
        self.queue.repeat = modes[(modes.index(self.queue.repeat) + 1) % 3]
        mode = self.queue.repeat
        name = "media-playlist-repeat-song-symbolic" if mode == "one" else "media-playlist-repeat-symbolic"
        self.repeat.set_image(Gtk.Image.new_from_icon_name(name, Gtk.IconSize.BUTTON))
        self.repeat.set_tooltip_text({"off": "Repetición desactivada", "all": "Repetir toda la cola", "one": "Repetir canción"}[mode])
        context = self.repeat.get_style_context()
        if mode == "off":
            context.remove_class("enabled")
        else:
            context.add_class("enabled")

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
        for key in list(self.nav_items):
            if key[0] == "playlist":
                del self.nav_items[key]
        for child in self.playlist_box.get_children():
            child.destroy()
        for playlist_id, name in self.library.playlists():
            self.add_nav(self.playlist_box, name, "view-list-symbolic", "playlist", playlist_id)
        self.playlist_box.show_all()
        self.update_navigation()

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
        if self.desktop_channel:
            self.desktop_channel.send({"event": "apple"})
        else:
            self.notify("Inicia q_AMusik con python3 -m q_amusik para usar el reproductor integrado.")

    def cleanup(self, *_):
        GLib.source_remove(self.timer)
        self.player.close()
        self.library.close()
        self.artwork.close()
        self.settings.disconnect(self.theme_signal)
        self.settings.disconnect(self.dark_signal)
        if self.desktop_settings:
            self.desktop_settings.disconnect(self.desktop_signal)
        Gtk.StyleContext.remove_provider_for_screen(Gdk.Screen.get_default(), self.provider)
        if self.desktop_channel:
            self.desktop_channel.close()


class Application(Gtk.Application):
    def __init__(self):
        app_id = "io.github.qrod.qAMusik.embedded" if EMBEDDED else "io.github.qrod.qAMusik"
        super().__init__(application_id=app_id, flags=Gio.ApplicationFlags.FLAGS_NONE)

    def do_activate(self):
        window = self.get_active_window()
        if window is None:
            window = Window(self)
            window.show_all()
            window.navigate("recent")
        window.present()


def main():
    import sys
    return Application().run(sys.argv)
