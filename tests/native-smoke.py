"""Prueba GTK y capturas reales con biblioteca sintética; ejecutar bajo Xvfb."""
from pathlib import Path
import os
import sys
import tempfile

source = Path('/usr/share/q-amusik') if '--installed' in sys.argv else Path(__file__).resolve().parents[1]
sys.path.insert(0, str(source))
from demo_library import seed

with tempfile.TemporaryDirectory(prefix='q-amusik-smoke-') as directory:
    os.environ['XDG_DATA_HOME'] = directory
    os.environ['NO_AT_BRIDGE'] = '1'
    from q_amusik.app import Application, Window
    from gi.repository import Gdk, GLib, Gst, Gtk
    app = Application()
    app.register(None)
    window = Window(app)
    sink = Gst.ElementFactory.make('fakesink')
    sink.set_property('sync', True)
    window.player.pipeline.set_property('audio-sink', sink)
    fixture = Path(directory) / 'demo'
    fixture.mkdir()
    assert seed(window.library, fixture) == (20, 0)
    window.refresh()
    tracks = window.visible_tracks[:2]
    playlist = window.library.create_playlist('Para escuchar despacio')
    for track in tracks:
        window.library.add_to_playlist(playlist, track.id)
    window.refresh_playlists()
    window.show_all()
    window.settings.set_property('gtk-application-prefer-dark-theme', False)
    window.navigate('recent')
    errors = []
    window.player.on_error = errors.append
    window.play(tracks[0])
    loop = GLib.MainLoop()
    artifact = Path('validation')
    artifact.mkdir(exist_ok=True)

    def capture(name):
        native = window.get_window()
        image = Gdk.pixbuf_get_from_window(native, 0, 0, native.get_width(), native.get_height())
        assert image is not None
        image.savev(str(artifact/name), 'png', [], [])

    def initial():
        assert window.player.loaded and window.player.playing
        assert window.player.position()[1] > 0
        assert window.now_cover.pixbuf is not None, 'No se cargó la carátula local'
        assert len(window.grid.get_children()) == 10
        capture('desktop-light.png')
        window.settings.set_property('gtk-application-prefer-dark-theme', True)

    def dark():
        assert window.get_style_context().has_class('dark')
        capture('desktop-dark.png')
        window.navigate('artists')

    def artists():
        assert len(window.grid.get_children()) == 5
        capture('artists-dark.png')
        window.navigate('albums')
        first = window.grid.get_children()[0].get_child()
        first.clicked()
        assert len(window.visible_tracks) == 2
        assert window.library_stack.get_visible_child_name() == 'table'

    def album():
        capture('album-dark.png')
        window.navigate('playlist', playlist, 'Para escuchar despacio')
        window.table.get_selection().select_path(Gtk.TreePath.new_from_indices([0]))
        window.favorite()
        assert len(window.library.tracks(favorites=True)) == 1
        window.play_selected()
        window.repeat_mode()
        assert window.queue.repeat == 'all'
        window.repeat_mode()
        assert window.queue.repeat == 'one'
        window.player.seek(1)
        capture('playlist-dark.png')
        window.settings.set_property('gtk-application-prefer-dark-theme', False)
        window.navigate('songs')
        window.resize(960, 680)

    def compact():
        capture('compact-songs.png')
        window.navigate('recent')

    def compact_grid():
        capture('compact-grid.png')
        window.search.set_text('esta canción no existe')
        window.search_changed()
        assert window.library_stack.get_visible_child_name() == 'empty'

    def no_results():
        capture('no-results.png')
        window.search.set_text('')
        window.search_changed()
        window.navigate('apple')
        window.settings.set_property('gtk-application-prefer-dark-theme', True)

    def apple():
        capture('apple-dark.png')
        assert window.stack.get_visible_child_name() == 'apple'
        empty_playlist = window.library.create_playlist('Lista vacía')
        window.navigate('playlist', empty_playlist, 'Lista vacía')
        assert window.library_stack.get_visible_child_name() == 'empty'

    def empty():
        capture('empty-dark.png')
        window.notify('No se encuentra el archivo. Comprueba la unidad conectada.')
        capture('error-dark.png')
        window.player.pause()

    steps = iter([initial, dark, artists, album, compact, compact_grid, no_results, apple, empty])
    def advance():
        try:
            step = next(steps)
            step()
            return True
        except StopIteration:
            window.destroy()
            loop.quit()
            return False
        except Exception as error:
            errors.append(repr(error))
            window.destroy()
            loop.quit()
            return False
    GLib.timeout_add(800, advance)
    loop.run()
    if errors:
        raise AssertionError(errors)
    print('GTK, carátulas, temas, navegación, listas, búsqueda, cola y reproducción: OK')
