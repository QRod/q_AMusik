"""Una ventana: biblioteca GTK alojada y reproductor oficial en Qt WebEngine.

No hay puente JavaScript hacia el código nativo, claves MusicKit, API privada,
intercepción de credenciales ni apertura de navegadores externos.
"""

import argparse
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
from urllib.parse import urlsplit

from . import __version__
from .library import data_directory
from .web_policy import APPLE_MUSIC_URL, allowed_navigation
from .qt_runtime import QtCore, QtGui, QtWidgets, Web, enum

CDM_PATHS = (
    "/opt/google/chrome/WidevineCdm/_platform_specific/linux_x64/libwidevinecdm.so",
    "/usr/lib/chromium/WidevineCdm/_platform_specific/linux_x64/libwidevinecdm.so",
    "/usr/lib/chromium-browser/WidevineCdm/_platform_specific/linux_x64/libwidevinecdm.so",
)


class ApplePage(Web.QWebEnginePage):
    def __init__(self, profile, owner, parent):
        super().__init__(profile, parent)
        self.owner = owner
        self.featurePermissionRequested.connect(self.deny_permission)
        settings = self.settings()
        settings.setAttribute(enum(Web.QWebEngineSettings, "WebAttribute", "JavascriptCanOpenWindows"), True)
        for name in ("JavascriptCanAccessClipboard", "LocalContentCanAccessFileUrls", "LocalContentCanAccessRemoteUrls"):
            settings.setAttribute(enum(Web.QWebEngineSettings, "WebAttribute", name), False)

    def deny_permission(self, origin, feature):
        self.setFeaturePermission(origin, feature,
                                  enum(Web.QWebEnginePage, "PermissionPolicy", "PermissionDeniedByUser"))

    def acceptNavigationRequest(self, url, navigation_type, is_main_frame):
        if is_main_frame and not allowed_navigation(url.toString(), self.owner.fixture_origin):
            self.owner.web_status.setText("Este enlace no pertenece al reproductor ni al acceso de Apple.")
            return False
        return True

    def createWindow(self, window_type):
        return self.owner.create_auth_window()


class DesktopWindow(QtWidgets.QMainWindow):
    def __init__(self, fixture_url=None, test_audio=False):
        super().__init__()
        self.fixture_origin = None
        self.service_url = APPLE_MUSIC_URL
        if fixture_url:
            parsed = urlsplit(fixture_url)
            if parsed.scheme != "http" or parsed.hostname != "127.0.0.1" or parsed.port is None:
                raise ValueError("El fixture sólo puede servirse desde loopback.")
            self.fixture_origin = f"http://127.0.0.1:{parsed.port}"
            self.service_url = fixture_url
        self.setWindowTitle("q_AMusik")
        self.setWindowIcon(QtGui.QIcon.fromTheme("io.github.qrod.qAMusik"))
        self.resize(1280, 880)
        self.setMinimumSize(960, 720)
        self.closing = False
        self.container = self.foreign = None
        self.browser = self.profile = None
        self.popups = []
        self.local_playing = False
        self.active_source = "library"
        self.web_loaded = False
        self.stack = QtWidgets.QStackedWidget()
        self.setCentralWidget(self.stack)
        self.loading = QtWidgets.QLabel("Cargando tu biblioteca…")
        self.loading.setAlignment(enum(QtCore.Qt, "AlignmentFlag", "AlignCenter"))
        self.local_index = self.stack.addWidget(self.loading)
        self.web_panel = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(self.web_panel)
        layout.setContentsMargins(0, 0, 0, 0)
        toolbar = QtWidgets.QHBoxLayout()
        toolbar.setContentsMargins(16, 10, 16, 10)
        back = QtWidgets.QPushButton("Mi biblioteca")
        back.clicked.connect(self.show_library)
        toolbar.addWidget(back)
        toolbar.addSpacing(16)
        toolbar.addWidget(QtWidgets.QLabel("Apple Music"))
        toolbar.addStretch(1)
        self.web_status = QtWidgets.QLabel("")
        toolbar.addWidget(self.web_status)
        reload_button = QtWidgets.QPushButton("Recargar")
        reload_button.clicked.connect(self.reload_web)
        toolbar.addWidget(reload_button)
        layout.addLayout(toolbar)
        self.drm_note = QtWidgets.QLabel("Para canciones completas se necesita Widevine compatible, por ejemplo el incluido en Google Chrome instalado. Consulta la guía de instalación.")
        self.drm_note.setWordWrap(True)
        self.drm_note.setContentsMargins(16, 8, 16, 8)
        self.drm_note.setVisible(not any(Path(path).is_file() for path in CDM_PATHS))
        layout.addWidget(self.drm_note)
        self.browser_layout = layout
        self.web_index = self.stack.addWidget(self.web_panel)
        parent_socket, child_socket = socket.socketpair()
        self.channel = parent_socket
        self.channel.setblocking(False)
        self.buffer = b""
        environment = dict(os.environ)
        environment.update(Q_AMUSIK_EMBEDDED="1", Q_AMUSIK_CONTROL_FD=str(child_socket.fileno()), GDK_BACKEND="x11")
        if test_audio:
            environment["Q_AMUSIK_TEST_AUDIO"] = "1"
        self.child = subprocess.Popen([sys.executable, "-m", "q_amusik"],
                                      cwd=str(Path(__file__).resolve().parent.parent),
                                      env=environment, pass_fds=(child_socket.fileno(),),
                                      stdout=subprocess.DEVNULL)
        child_socket.close()
        self.notifier = QtCore.QSocketNotifier(self.channel.fileno(), enum(QtCore.QSocketNotifier, "Type", "Read"), self)
        self.notifier.activated.connect(self.read_child)
        QtCore.QTimer.singleShot(20000, self.check_startup)

    def send_command(self, command):
        if not self.closing:
            try:
                self.channel.sendall((json.dumps({"command": command}) + "\n").encode())
            except OSError:
                self.check_startup()

    def read_child(self, *_):
        try:
            data = self.channel.recv(4096)
        except BlockingIOError:
            return
        except OSError:
            data = b""
        if not data:
            self.notifier.setEnabled(False)
            self.loading.setText("La biblioteca local se cerró. Reinicia q_AMusik para recuperarla.")
            return
        self.buffer += data
        if len(self.buffer) > 8192:
            self.notifier.setEnabled(False)
            return
        while b"\n" in self.buffer:
            line, self.buffer = self.buffer.split(b"\n", 1)
            try:
                event = json.loads(line)
            except (ValueError, UnicodeError):
                continue
            if not isinstance(event, dict):
                continue
            kind = event.get("event")
            if kind == "ready" and self.container is None:
                xid = event.get("xid")
                if type(xid) is not int or not 0 < xid < 2**32:
                    continue
                self.foreign = QtGui.QWindow.fromWinId(xid)
                if self.foreign is None:
                    continue
                self.container = QtWidgets.QWidget.createWindowContainer(self.foreign)
                self.container.setMinimumSize(960, 680)
                self.container.setFocusPolicy(enum(QtCore.Qt, "FocusPolicy", "StrongFocus"))
                self.stack.removeWidget(self.loading)
                self.local_index = self.stack.insertWidget(0, self.container)
                self.web_index = self.stack.indexOf(self.web_panel)
                self.stack.setCurrentIndex(self.local_index)
            elif kind == "apple":
                self.show_apple()
            elif kind == "playing":
                self.local_playing = event.get("value") is True
                if self.active_source == "apple":
                    if self.local_playing:
                        self.send_command("pause")
                    if self.browser is not None:
                        self.set_web_muted(self.local_playing)
                elif self.local_playing:
                    self.silence_web()
            elif kind == "theme":
                self.apply_theme(event.get("dark") is True)

    def check_startup(self):
        if self.container is None and not self.closing:
            self.loading.setText("No se pudo abrir la biblioteca. Comprueba las dependencias GTK y que X11/XWayland esté disponible.")

    def apply_theme(self, dark):
        background, foreground, surface = ("#1e1e20", "#f4f4f5", "#28282c") if dark else ("#ffffff", "#242426", "#f3f2f5")
        self.setStyleSheet(f"QMainWindow, QStackedWidget, QWidget {{ background: {background}; color: {foreground}; font-size: 13px; }} QPushButton {{ background: {surface}; border: 0; border-radius: 6px; padding: 8px 14px; }} QPushButton:hover {{ background: {'#414147' if dark else '#e3e1e7'}; }} QPushButton:focus {{ border: 2px solid #cf3453; }}")

    def ensure_browser(self):
        if self.browser is not None:
            return
        root = data_directory()
        storage, cache = root / "apple-profile", root / "apple-cache"
        storage.mkdir(mode=0o700, exist_ok=True)
        cache.mkdir(mode=0o700, exist_ok=True)
        self.profile = Web.QWebEngineProfile("AppleMusic", self)
        self.profile.setPersistentStoragePath(str(storage))
        self.profile.setCachePath(str(cache))
        self.profile.setPersistentCookiesPolicy(enum(Web.QWebEngineProfile, "PersistentCookiesPolicy", "AllowPersistentCookies"))
        self.profile.downloadRequested.connect(lambda download: download.cancel())
        try:
            from PyQt6.QtWebEngineWidgets import QWebEngineView
        except ImportError:
            from PyQt5.QtWebEngineWidgets import QWebEngineView
        self.browser = QWebEngineView(self.web_panel)
        self.browser.setPage(ApplePage(self.profile, self, self.browser))
        self.browser.loadFinished.connect(self.loaded)
        self.browser.loadStarted.connect(lambda: self.web_status.setText("Conectando con Apple…"))
        self.browser_layout.addWidget(self.browser, 1)
        self.browser.setUrl(QtCore.QUrl(self.service_url))

    def show_apple(self):
        self.active_source = "apple"
        self.send_command("pause")
        self.ensure_browser()
        self.set_web_muted(self.local_playing)
        self.stack.setCurrentIndex(self.web_index)

    def silence_web(self):
        for page in self.web_pages():
            page.setAudioMuted(True)
            page.runJavaScript("document.querySelectorAll('audio, video').forEach(media => media.pause());")

    def web_pages(self):
        pages = [self.browser.page()] if self.browser is not None else []
        return pages + [popup.web_view.page() for popup in self.popups]

    def set_web_muted(self, muted):
        for page in self.web_pages():
            page.setAudioMuted(muted)

    def show_library(self):
        self.active_source = "library"
        self.silence_web()
        for popup in list(self.popups):
            popup.close()
        self.stack.setCurrentIndex(self.local_index)
        self.send_command("library")
        if self.container is not None:
            self.container.setFocus()

    def reload_web(self):
        if self.browser is not None:
            self.browser.setUrl(QtCore.QUrl(self.service_url))

    def loaded(self, success):
        self.web_loaded = bool(success)
        self.web_status.setText("Reproductor integrado" if success else "No se pudo cargar. Comprueba tu conexión y pulsa Recargar.")

    def create_auth_window(self):
        if len(self.popups) >= 3 or self.closing or self.active_source != "apple":
            return None
        try:
            from PyQt6.QtWebEngineWidgets import QWebEngineView
        except ImportError:
            from PyQt5.QtWebEngineWidgets import QWebEngineView
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle("Acceso de Apple · q_AMusik")
        dialog.resize(600, 760)
        layout = QtWidgets.QVBoxLayout(dialog)
        identity = QtWidgets.QLabel("Ventana de acceso · q_AMusik")
        layout.addWidget(identity)
        view = QWebEngineView(dialog)
        dialog.web_view = view
        dialog.web_loaded = False
        view.loadFinished.connect(lambda success: setattr(dialog, "web_loaded", success))
        page = ApplePage(self.profile, self, view)
        view.setPage(page)
        page.setAudioMuted(self.active_source != "apple" or self.local_playing)
        view.urlChanged.connect(lambda url: identity.setText(url.host() or "Acceso de Apple"))
        page.windowCloseRequested.connect(dialog.close)
        layout.addWidget(view)
        self.popups.append(dialog)
        dialog.finished.connect(lambda *_: self.popups.remove(dialog) if dialog in self.popups else None)
        dialog.setAttribute(enum(QtCore.Qt, "WidgetAttribute", "WA_DeleteOnClose"))
        dialog.show()
        return page

    def closeEvent(self, event):
        self.silence_web()
        self.send_command("shutdown")
        self.closing = True
        self.notifier.setEnabled(False)
        self.channel.close()
        try:
            self.child.wait(timeout=3)
        except subprocess.TimeoutExpired:
            self.child.terminate()
            try:
                self.child.wait(timeout=2)
            except subprocess.TimeoutExpired:
                self.child.kill()
                self.child.wait()
        for popup in list(self.popups):
            popup.close()
        if self.browser is not None:
            self.browser.deleteLater()
            QtCore.QCoreApplication.sendPostedEvents(None, enum(QtCore.QEvent, "Type", "DeferredDelete"))
            self.browser = None
            self.profile.deleteLater()
            QtCore.QCoreApplication.sendPostedEvents(None, enum(QtCore.QEvent, "Type", "DeferredDelete"))
            self.profile = None
        event.accept()


def main():
    parser = argparse.ArgumentParser(description="q_AMusik · biblioteca local y Apple Music integrado")
    parser.add_argument("--version", action="version", version=__version__)
    parser.parse_args()
    if os.geteuid() == 0:
        raise SystemExit("Ejecuta q_AMusik con tu usuario, sin sudo.")
    if not os.environ.get("DISPLAY"):
        raise SystemExit("Se necesita X11 o XWayland para alojar la biblioteca GTK.")
    os.environ["QT_QPA_PLATFORM"] = "xcb"
    for candidate in CDM_PATHS:
        if Path(candidate).is_file():
            flags = os.environ.get("QTWEBENGINE_CHROMIUM_FLAGS", "")
            os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = flags + " --widevine-path=" + candidate
            break
    QtCore.QCoreApplication.setAttribute(enum(QtCore.Qt, "ApplicationAttribute", "AA_ShareOpenGLContexts"))
    app = QtWidgets.QApplication([sys.argv[0]])
    app.setApplicationName("q_AMusik")
    app.setDesktopFileName("io.github.qrod.qAMusik")
    lock = QtCore.QLockFile(str(data_directory() / "desktop.lock"))
    lock.setStaleLockTime(0)
    if not lock.tryLock(0):
        QtWidgets.QMessageBox.information(None, "q_AMusik", "q_AMusik ya está abierto. Vuelve a su ventana.")
        return 0
    window = DesktopWindow()
    window.show()
    try:
        return app.exec() if hasattr(app, "exec") else app.exec_()
    finally:
        lock.unlock()
