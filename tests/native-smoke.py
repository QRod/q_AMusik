"""Ejecutar en Linux: dbus-run-session -- xvfb-run -a python3 tests/native-smoke.py."""

from pathlib import Path
import os
import sys
import tempfile
import wave

source = Path("/usr/share/q-amusik") if "--installed" in sys.argv else Path(__file__).resolve().parents[1]
sys.path.insert(0, str(source))

with tempfile.TemporaryDirectory(prefix="q-amusik-smoke-") as directory:
    os.environ["XDG_DATA_HOME"] = directory
    os.environ["NO_AT_BRIDGE"] = "1"
    from q_amusik.app import Application, Window
    from gi.repository import Gdk, GLib, Gst, Gtk

    app = Application()
    app.register(None)
    window = Window(app)
    sink = Gst.ElementFactory.make("fakesink")
    sink.set_property("sync", True)
    window.player.pipeline.set_property("audio-sink", sink)
    audio = Path(directory) / "Prueba.wav"
    with wave.open(str(audio), "wb") as output:
        output.setnchannels(1)
        output.setsampwidth(2)
        output.setframerate(8000)
        output.writeframes(b"\x00\x00" * 8000 * 4)
    assert window.library.import_paths([audio]) == (1, 0)
    window.refresh()
    playlist = window.library.create_playlist("Mi lista")
    track = window.visible_tracks[0]
    window.library.add_to_playlist(playlist, track.id)
    window.refresh_playlists()
    window.navigate("playlist", playlist, "Mi lista")
    assert len(window.visible_tracks) == 1
    window.show_all()
    window.table.get_selection().select_path(Gtk.TreePath.new_from_indices([0]))
    window.favorite()
    assert window.library.tracks(favorites=True)
    window.play_selected()
    errors = []
    window.player.on_error = errors.append
    loop = GLib.MainLoop()
    artifact = Path("validation")
    artifact.mkdir(exist_ok=True)

    def capture(name):
        native = window.get_window()
        image = Gdk.pixbuf_get_from_window(native, 0, 0, native.get_width(), native.get_height())
        assert image is not None
        image.savev(str(artifact / name), "png", [], [])

    def desktop():
        try:
            assert window.player.loaded
            assert window.player.playing
            assert window.player.position()[1] > 0
            window.player.seek(1)
            capture("desktop.png")
            window.navigate("apple")
            window.resize(820, 560)
        except Exception as error:
            errors.append(str(error) or repr(error))
        return False

    def finish():
        try:
            capture("compact-apple.png")
            assert window.stack.get_visible_child_name() == "apple"
            window.player.pause()
        except Exception as error:
            errors.append(str(error) or repr(error))
        window.destroy()
        loop.quit()
        return False

    GLib.timeout_add(700, desktop)
    GLib.timeout_add(1300, finish)
    loop.run()
    if errors:
        raise AssertionError(errors)
    print("GTK, biblioteca, lista, favoritos, decodificación WAV y capturas: OK")
