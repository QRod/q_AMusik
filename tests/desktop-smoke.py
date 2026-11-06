"""Contenedor real GTK/Qt, audio de prueba y ventanas de autorización internas."""

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import io
import json
import os
from pathlib import Path
import sys
import tempfile
import threading
import time
import wave

source = Path('/usr/share/q-amusik') if '--installed' in sys.argv else Path(__file__).resolve().parents[1]
sys.path.insert(0, str(source))
from demo_library import seed
from q_amusik.library import Library
from q_amusik.qt_runtime import QtCore, QtWidgets, enum
from q_amusik.desktop import DesktopWindow

try:
    from PyQt6.QtTest import QTest
except ImportError:
    from PyQt5.QtTest import QTest

page = b'''<!doctype html><meta charset="utf-8"><title>Reproductor de demostraci\xc3\xb3n</title>
<style>body{font:16px sans-serif;background:#1e1e20;color:white;margin:24px}button{height:40px;width:180px;background:#c92c4c;color:white;border:0;border-radius:6px}</style>
<h1>Reproductor integrado de prueba</h1><p>Audio sint\xc3\xa9tico; sin cuenta ni contenido de Apple.</p>
<audio id="audio" src="/tone.wav"></audio>
<button id="play" style="position:absolute;top:120px;left:24px" onclick="document.getElementById('audio').play()">Reproducir prueba</button>
<button style="position:absolute;top:180px;left:24px" onclick="window.open('/signin','auth')">Probar acceso</button>'''
audio_stream = io.BytesIO()
with wave.open(audio_stream, 'wb') as out:
    out.setnchannels(1)
    out.setsampwidth(2)
    out.setframerate(8000)
    out.writeframes(b'\0\0' * 8000 * 20)


class Fixture(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/tone.wav':
            data, content = audio_stream.getvalue(), 'audio/wav'
        elif self.path == '/signin':
            data, content = b'<h1>Ventana de acceso de prueba</h1><p>Sin credenciales.</p>', 'text/html'
        else:
            data, content = page, 'text/html; charset=utf-8'
        self.send_response(200)
        self.send_header('Content-Type', content)
        self.send_header('Content-Length', str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, *_):
        pass


with tempfile.TemporaryDirectory(prefix='q-amusik-desktop-') as temporary:
    os.environ['XDG_DATA_HOME'] = temporary
    os.environ['NO_AT_BRIDGE'] = '1'
    root = Path(temporary)
    fixture = root/'demo'
    fixture.mkdir()
    directory = root/'q_amusik'
    directory.mkdir()
    library = Library(directory/'library.db')
    seed(library, fixture)
    library.close()
    server = ThreadingHTTPServer(('127.0.0.1', 0), Fixture)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    QtCore.QCoreApplication.setAttribute(enum(QtCore.Qt, 'ApplicationAttribute', 'AA_ShareOpenGLContexts'))
    app = QtWidgets.QApplication([sys.argv[0]])
    public = '--public-player' in sys.argv
    url = None if public else f'http://127.0.0.1:{server.server_port}/'
    window = DesktopWindow(fixture_url=url, test_audio=True)
    window.show()
    output = Path('validation')
    output.mkdir(exist_ok=True)
    errors = []
    phase = 0
    entered = time.monotonic()
    javascript = None

    def capture(name):
        geometry = window.geometry()
        image = app.primaryScreen().grabWindow(0, geometry.x(), geometry.y(), geometry.width(), geometry.height())
        assert image.save(str(output/name), 'PNG')

    def result(value):
        global javascript
        javascript = value

    def advance():
        global phase, entered, javascript
        try:
            if time.monotonic()-entered > 40:
                raise AssertionError(f'Timeout en fase {phase}')
            if phase == 0:
                if window.container is None:
                    return
                assert window.child.poll() is None
                capture('desktop-hosted.png')
                window.send_command('play')
            elif phase == 1:
                if not window.local_playing:
                    return
                window.show_apple()
            elif phase == 2:
                if not window.web_loaded or window.local_playing:
                    return
                assert not window.browser.page().isAudioMuted()
                capture('apple-public.png' if public else 'desktop-web-fixture.png')
                if public:
                    window.browser.page().runJavaScript('document.title', result)
                else:
                    QTest.mouseClick(window.browser.focusProxy(), enum(QtCore.Qt, 'MouseButton', 'LeftButton'),
                                     enum(QtCore.Qt, 'KeyboardModifier', 'NoModifier'), QtCore.QPoint(80, 140))
            elif phase == 3:
                if public:
                    if javascript is None:
                        return
                    assert 'music' in str(javascript).lower(), javascript
                    print('Reproductor oficial cargado, sin cuenta; título:', javascript, flush=True)
                    window.close()
                    app.quit()
                    return
                window.browser.page().runJavaScript("({paused:document.querySelector('audio').paused,time:document.querySelector('audio').currentTime})", result)
            elif phase == 4:
                if javascript is None:
                    return
                assert javascript['paused'] is False and javascript['time'] > 0, javascript
                QTest.mouseClick(window.browser.focusProxy(), enum(QtCore.Qt, 'MouseButton', 'LeftButton'),
                                 enum(QtCore.Qt, 'KeyboardModifier', 'NoModifier'), QtCore.QPoint(80, 200))
            elif phase == 5:
                if not window.popups:
                    return
                capture('desktop-auth-fixture.png')
                window.popups[0].close()
                window.show_library()
                assert window.browser.page().isAudioMuted()
                javascript = None
                window.browser.page().runJavaScript("document.querySelector('audio').paused", result)
            elif phase == 6:
                if javascript is None:
                    return
                assert javascript is True
                window.send_command('play')
            elif phase == 7:
                if not window.local_playing:
                    return
                assert window.browser.page().isAudioMuted()
                capture('desktop-return-library.png')
                window.close()
                app.quit()
                return
            phase += 1
            entered = time.monotonic()
        except Exception as error:
            errors.append(repr(error))
            capture('desktop-error.png')
            window.close()
            app.quit()

    timer = QtCore.QTimer()
    timer.timeout.connect(advance)
    timer.start(1000)
    status = app.exec() if hasattr(app, 'exec') else app.exec_()
    server.shutdown()
    server.server_close()
    assert not errors, errors
    assert window.child.poll() is not None
    if not public:
        print('GTK alojado, WebEngine dentro de la ventana, audio web/local y popup interno: OK')
