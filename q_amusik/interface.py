"""Composición GTK de la biblioteca y del reproductor, inspirada en Music para Mac."""

from collections import OrderedDict
from pathlib import Path
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gdk, Gio, Gtk, Pango
from .artwork import ArtworkCache, Cover


def text(value, style=None, ellipsize=False):
    widget = Gtk.Label(label=value, xalign=0)
    if style:
        widget.get_style_context().add_class(style)
    if ellipsize:
        widget.set_ellipsize(Pango.EllipsizeMode.END)
        widget.set_max_width_chars(24)
        widget.set_tooltip_text(value)
    return widget


def icon_button(name, tooltip, callback, style="icon-button", toggle=False):
    widget = Gtk.ToggleButton() if toggle else Gtk.Button()
    widget.set_image(Gtk.Image.new_from_icon_name(name, Gtk.IconSize.BUTTON))
    widget.set_tooltip_text(tooltip)
    widget.get_accessible().set_name(tooltip)
    widget.get_style_context().add_class(style)
    widget.connect("toggled" if toggle else "clicked", callback)
    return widget


def action_button(title, callback, primary=False):
    widget = Gtk.Button(label=title)
    widget.connect("clicked", callback)
    widget.get_style_context().add_class("primary" if primary else "secondary")
    return widget


class Interface:
    def setup_interface(self):
        self.artwork = ArtworkCache()
        self.collection = None
        self.album_limit = 120
        self.nav_items = {}
        self.get_style_context().add_class("music-window")
        self.set_default_size(1280, 820)
        self.set_size_request(960, 680)
        self.provider = Gtk.CssProvider()
        self.provider.load_from_path(str(Path(__file__).with_name("style.css")))
        Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(), self.provider, 600)
        self.settings = Gtk.Settings.get_default()
        self.desktop_settings = None
        source = Gio.SettingsSchemaSource.get_default()
        schema = source.lookup("org.gnome.desktop.interface", True) if source else None
        if schema and schema.has_key("color-scheme"):
            self.desktop_settings = Gio.Settings.new_full(schema, None, None)
            self.desktop_signal = self.desktop_settings.connect("changed::color-scheme", self.update_theme)
        self.theme_signal = self.settings.connect("notify::gtk-theme-name", self.update_theme)
        self.dark_signal = self.settings.connect("notify::gtk-application-prefer-dark-theme", self.update_theme)
        self.update_theme()
        self.build_player_header()
        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.add(root)
        body = Gtk.Box()
        root.pack_start(body, True, True, 0)
        body.pack_start(self.build_sidebar(), False, False, 0)
        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        content.get_style_context().add_class("content")
        body.pack_start(content, True, True, 0)
        heading = Gtk.Box(spacing=12)
        heading.get_style_context().add_class("content-heading")
        self.back = icon_button("go-previous-symbolic", "Volver a la biblioteca", self.close_collection)
        heading.pack_start(self.back, False, False, 0)
        self.title_label = text("Añadido recientemente", "page-title")
        heading.pack_start(self.title_label, True, True, 0)
        heading.pack_end(icon_button("folder-new-symbolic", "Añadir carpeta", lambda *_: self.choose(True)), False, False, 0)
        heading.pack_end(icon_button("list-add-symbolic", "Añadir canciones", lambda *_: self.choose(False)), False, False, 0)
        content.pack_start(heading, False, False, 0)
        self.stack = Gtk.Stack()
        content.pack_start(self.stack, True, True, 0)
        self.build_library()
        self.build_apple_page()
        self.status = text("", "status")
        self.status.set_line_wrap(True)
        self.status.set_selectable(True)
        content.pack_end(self.status, False, False, 0)

    def update_theme(self, *_):
        name = (self.settings.get_property("gtk-theme-name") or "").lower()
        prefer = self.settings.get_property("gtk-application-prefer-dark-theme")
        scheme = self.desktop_settings.get_string("color-scheme") if self.desktop_settings else "default"
        context = self.get_style_context()
        if prefer or "dark" in name or scheme == "prefer-dark":
            context.add_class("dark")
        else:
            context.remove_class("dark")

    def build_sidebar(self):
        sidebar = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        sidebar.set_size_request(224, -1)
        sidebar.get_style_context().add_class("sidebar")
        brand = Gtk.Box(spacing=8)
        image = Gtk.Image.new_from_icon_name("audio-x-generic-symbolic", Gtk.IconSize.LARGE_TOOLBAR)
        brand.pack_start(image, False, False, 0)
        brand.pack_start(text("q_AMusik", "brand"), False, False, 0)
        brand.get_style_context().add_class("brand-row")
        sidebar.pack_start(brand, False, False, 0)
        self.search = Gtk.SearchEntry(placeholder_text="Buscar")
        self.search.get_accessible().set_name("Buscar en la biblioteca local")
        self.search.connect("search-changed", self.search_changed)
        sidebar.pack_start(self.search, False, False, 10)
        sidebar.pack_start(text("Apple Music", "nav-section"), False, False, 0)
        self.add_nav(sidebar, "Escuchar", "audio-headphones-symbolic", "apple")
        sidebar.pack_start(text("Biblioteca", "nav-section"), False, False, 0)
        for title, icon, view in (
            ("Añadido recientemente", "document-open-recent-symbolic", "recent"),
            ("Artistas", "avatar-default-symbolic", "artists"),
            ("Álbumes", "media-optical-symbolic", "albums"),
            ("Canciones", "audio-x-generic-symbolic", "songs"),
            ("Favoritos", "starred-symbolic", "favorites")):
            self.add_nav(sidebar, title, icon, view)
        lists_heading = Gtk.Box()
        lists_heading.pack_start(text("Listas de reproducción", "nav-section"), True, True, 0)
        lists_heading.pack_end(icon_button("list-add-symbolic", "Nueva lista local", self.new_playlist), False, False, 0)
        sidebar.pack_start(lists_heading, False, False, 10)
        self.playlist_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroll.add(self.playlist_box)
        sidebar.pack_start(scroll, True, True, 0)
        account = action_button("Abrir Apple Music", lambda *_: self.navigate("apple"))
        account.get_style_context().add_class("account")
        sidebar.pack_end(account, False, False, 0)
        return sidebar

    def add_nav(self, box, title, icon, view, playlist=None):
        item = Gtk.Button()
        item.get_style_context().add_class("nav-item")
        row = Gtk.Box(spacing=10)
        row.pack_start(Gtk.Image.new_from_icon_name(icon, Gtk.IconSize.MENU), False, False, 0)
        row.pack_start(text(title, ellipsize=True), True, True, 0)
        item.add(row)
        item.set_tooltip_text(title)
        item.connect("clicked", lambda *_: self.navigate(view, playlist, title))
        box.pack_start(item, False, False, 0)
        self.nav_items[(view, playlist)] = item
        return item

    def update_navigation(self):
        for key, item in self.nav_items.items():
            context = item.get_style_context()
            if key == (self.view, self.playlist):
                context.add_class("selected")
                item.get_accessible().set_description("Vista actual")
            else:
                context.remove_class("selected")
                item.get_accessible().set_description("")

    def build_player_header(self):
        header = Gtk.HeaderBar()
        header.set_show_close_button(True)
        header.get_style_context().add_class("player-header")
        controls = Gtk.Box(spacing=2)
        controls.pack_start(icon_button("media-shuffle-symbolic", "Reproducción aleatoria",
                    lambda b: setattr(self.queue, "shuffle", b.get_active()), toggle=True), False, False, 0)
        controls.pack_start(icon_button("media-skip-backward-symbolic", "Canción anterior", self.previous), False, False, 0)
        self.play_button = icon_button("media-playback-start-symbolic", "Reproducir o pausar", self.toggle, "play-button")
        controls.pack_start(self.play_button, False, False, 0)
        controls.pack_start(icon_button("media-skip-forward-symbolic", "Canción siguiente", lambda *_: self.advance(False)), False, False, 0)
        self.repeat = icon_button("media-playlist-repeat-symbolic", "Repetición desactivada", self.repeat_mode)
        controls.pack_start(self.repeat, False, False, 0)
        header.pack_start(controls)
        playing = Gtk.Box(spacing=10)
        playing.get_style_context().add_class("now-playing")
        self.now_cover = Cover(self.artwork, size=44)
        playing.pack_start(self.now_cover, False, False, 0)
        details = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        details.set_size_request(280, -1)
        self.now = text("q_AMusik", "now-title", True)
        self.now_artist = text("Elige algo que te encante.", "now-artist", True)
        details.pack_start(self.now, False, False, 0)
        details.pack_start(self.now_artist, False, False, 0)
        timeline = Gtk.Box(spacing=8)
        self.elapsed, self.duration = text("0:00", "time"), text("0:00", "time")
        self.seek = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, 1, 1)
        self.seek.set_draw_value(False)
        self.seek.set_hexpand(True)
        self.seek.get_accessible().set_name("Posición de reproducción local")
        self.seek.connect("change-value", self.seek_to)
        timeline.pack_start(self.elapsed, False, False, 0)
        timeline.pack_start(self.seek, True, True, 0)
        timeline.pack_end(self.duration, False, False, 0)
        details.pack_start(timeline, False, False, 0)
        playing.pack_start(details, True, True, 0)
        header.set_custom_title(playing)
        volume = Gtk.VolumeButton()
        volume.set_value(.8)
        self.player.volume(.8)
        volume.connect("value-changed", lambda _, value: self.player.volume(value))
        volume.get_style_context().add_class("icon-button")
        volume.set_tooltip_text("Volumen local")
        header.pack_end(volume)
        self.set_titlebar(header)

    def build_library(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=18)
        box.get_style_context().add_class("library")
        self.subtitle = text("Tu colección, siempre contigo.", "subtitle")
        box.pack_start(self.subtitle, False, False, 0)
        self.collection_hero = Gtk.Box(spacing=22)
        box.pack_start(self.collection_hero, False, False, 0)
        self.actions = Gtk.Box(spacing=8)
        self.actions.pack_start(action_button("Reproducir", self.play_selected, True), False, False, 0)
        self.actions.pack_start(icon_button("starred-symbolic", "Marcar o desmarcar favoritas", self.favorite), False, False, 0)
        self.actions.pack_start(icon_button("list-add-symbolic", "Añadir selección a lista", self.add_to_playlist), False, False, 0)
        self.actions.pack_end(icon_button("list-remove-symbolic", "Quitar referencia; conservar archivo", self.remove_selected), False, False, 0)
        box.pack_start(self.actions, False, False, 0)
        self.library_stack = Gtk.Stack()
        box.pack_start(self.library_stack, True, True, 0)
        self.grid = Gtk.FlowBox()
        self.grid.set_selection_mode(Gtk.SelectionMode.NONE)
        self.grid.set_homogeneous(True)
        self.grid.set_row_spacing(24)
        self.grid.set_column_spacing(22)
        self.grid.set_max_children_per_line(6)
        self.grid.set_min_children_per_line(1)
        self.grid.set_valign(Gtk.Align.START)
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroll.add(self.grid)
        self.library_stack.add_named(scroll, "grid")
        self.store = Gtk.ListStore(int, str, str, str, str, str)
        self.table = Gtk.TreeView(model=self.store)
        self.table.set_enable_search(False)
        self.table.get_selection().set_mode(Gtk.SelectionMode.MULTIPLE)
        self.table.get_style_context().add_class("songs")
        for index, title in enumerate(("", "Título", "Artista", "Álbum", "Tiempo"), 1):
            if index == 1:
                renderer = Gtk.CellRendererPixbuf()
                column = Gtk.TreeViewColumn(title, renderer, icon_name=index)
            else:
                renderer = Gtk.CellRendererText()
                renderer.set_property("ellipsize", Pango.EllipsizeMode.END)
                renderer.set_property("ypad", 12)
                column = Gtk.TreeViewColumn(title, renderer, text=index)
            column.set_resizable(True)
            column.set_expand(index in (2,3,4))
            if index in (2,3,4):
                column.set_min_width(90)
            self.table.append_column(column)
        self.table.connect("row-activated", lambda *_: self.play_selected())
        table_scroll = Gtk.ScrolledWindow()
        table_scroll.add(self.table)
        self.library_stack.add_named(table_scroll, "table")
        self.empty_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14)
        self.empty_box.set_halign(Gtk.Align.CENTER)
        self.empty_box.set_valign(Gtk.Align.CENTER)
        symbol = Gtk.Image.new_from_icon_name("audio-x-generic-symbolic", Gtk.IconSize.DIALOG)
        symbol.get_style_context().add_class("empty-icon")
        self.empty_box.pack_start(symbol, False, False, 0)
        self.empty = text("Tu biblioteca empieza contigo.", "empty-title")
        self.empty_box.pack_start(self.empty, False, False, 0)
        self.empty_help = text("Añade tus canciones favoritas y dales un lugar aquí.", "subtitle")
        self.empty_help.set_line_wrap(True)
        self.empty_box.pack_start(self.empty_help, False, False, 0)
        self.import_empty = action_button("Añadir música", lambda *_: self.choose(True), True)
        self.import_empty.set_halign(Gtk.Align.CENTER)
        self.empty_box.pack_start(self.import_empty, False, False, 8)
        self.library_stack.add_named(self.empty_box, "empty")
        self.stack.add_named(box, "library")

    def render_library(self):
        grid_view = self.view in ("recent", "albums", "artists") and self.collection is None
        self.actions.set_visible(not grid_view and bool(self.visible_tracks))
        self.back.set_visible(self.collection is not None)
        for child in self.collection_hero.get_children():
            child.destroy()
        self.collection_hero.set_visible(bool(self.collection and self.visible_tracks))
        if self.collection and self.visible_tracks:
            track = self.visible_tracks[0]
            self.collection_hero.pack_start(Cover(self.artwork, track.path, 120), False, False, 0)
            info = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
            info.set_valign(Gtk.Align.CENTER)
            info.pack_start(text(track.artist, "collection-artist", True), False, False, 0)
            info.pack_start(text(f"{len(self.visible_tracks)} canciones · Archivos locales", "subtitle"), False, False, 0)
            self.collection_hero.pack_start(info, True, True, 0)
            self.collection_hero.show_all()
        if not self.visible_tracks:
            searching = bool(self.search.get_text())
            self.empty.set_text("No encontramos esa canción." if searching else "Tu biblioteca empieza contigo.")
            self.empty_help.set_text("Prueba con otro título, artista o álbum." if searching else
                                     "Añade tus canciones favoritas y dales un lugar aquí.")
            self.import_empty.set_visible(not searching)
            self.library_stack.set_visible_child_name("empty")
        elif grid_view:
            self.render_grid()
            self.library_stack.set_visible_child_name("grid")
        else:
            self.library_stack.set_visible_child_name("table")
        count = len(self.visible_tracks)
        self.subtitle.set_text(f"{count} {'canción' if count == 1 else 'canciones'} en tu biblioteca local")

    def render_grid(self):
        for child in self.grid.get_children():
            child.destroy()
        artists = self.view == "artists"
        groups = OrderedDict()
        for track in self.visible_tracks:
            key = track.artist if artists else (track.album, track.artist)
            groups.setdefault(key, []).append(track)
        for key, tracks in list(groups.items())[:self.album_limit]:
            first = tracks[0]
            title = first.artist if artists else first.album
            subtitle = f"{len(tracks)} canciones" if artists else first.artist
            card = Gtk.Button()
            card.get_style_context().add_class("album-card")
            card.set_tooltip_text(f"{title}\n{subtitle}")
            card.get_accessible().set_name(f"Abrir {title}, {subtitle}")
            contents = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
            contents.pack_start(Cover(self.artwork, first.path, 170, artists), False, False, 0)
            contents.pack_start(text(title, "album-title", True), False, False, 5)
            contents.pack_start(text(subtitle, "album-artist", True), False, False, 0)
            card.add(contents)
            card.connect("clicked", lambda _, ts=tracks, name=title: self.open_collection(ts, name))
            self.grid.add(card)
        if len(groups) > self.album_limit:
            more = action_button("Mostrar más", self.more_albums)
            self.grid.add(more)
        self.grid.show_all()

    def more_albums(self, *_):
        self.album_limit += 120
        self.render_grid()

    def open_collection(self, tracks, title):
        self.collection = {track.id for track in tracks}
        self.title_label.set_text(title)
        self.refresh()

    def close_collection(self, *_):
        self.navigate(self.view, self.playlist)

    def build_apple_page(self):
        wrapper = Gtk.ScrolledWindow()
        wrapper.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        page.get_style_context().add_class("apple-page")
        page.set_halign(Gtk.Align.CENTER)
        page.set_valign(Gtk.Align.CENTER)
        symbol = Gtk.Image.new_from_icon_name("audio-headphones-symbolic", Gtk.IconSize.DIALOG)
        symbol.get_style_context().add_class("apple-symbol")
        page.pack_start(symbol, False, False, 8)
        title = text("Toda tu música.\nTambién en Linux.", "apple-title")
        title.set_justify(Gtk.Justification.CENTER)
        title.set_xalign(.5)
        page.pack_start(title, False, False, 0)
        detail = text("Tu suscripción, tus álbumes y tus listas de Apple Music.\n"
                      "Continúa en el reproductor oficial e inicia sesión con Apple.", "apple-description")
        detail.set_justify(Gtk.Justification.CENTER)
        detail.set_xalign(.5)
        detail.set_line_wrap(True)
        detail.set_max_width_chars(50)
        page.pack_start(detail, False, False, 0)
        launch = action_button("Abrir Apple Music", self.launch_apple, True)
        launch.set_halign(Gtk.Align.CENTER)
        page.pack_start(launch, False, False, 4)
        note = text("Se abrirá en tu navegador. La reproducción del catálogo y el inicio\n"
                    "de sesión se gestionan allí; los controles de q_AMusik son locales.", "apple-note")
        note.set_line_wrap(True)
        note.set_max_width_chars(55)
        note.set_justify(Gtk.Justification.CENTER)
        note.set_xalign(.5)
        page.pack_start(note, False, False, 12)
        wrapper.add(page)
        self.stack.add_named(wrapper, "apple")
