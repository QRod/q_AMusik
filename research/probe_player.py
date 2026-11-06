"""Diagnóstico aislado de un motor interno; no es reproducción de Apple Music.

No inicia sesión, no usa tokens, no solicita licencias ni conserva un perfil.
Ejecutar con el Python de Ubuntu bajo Xvfb o un escritorio, usando --qt 5/6.
"""

import argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import sys
import threading

SCRIPT = b"""
(async () => {
  const audio = document.createElement('audio');
  const result = {
    secureContext: window.isSecureContext,
    userAgent: navigator.userAgent,
    aac: audio.canPlayType('audio/mp4; codecs="mp4a.40.2"'),
    eme: typeof navigator.requestMediaKeySystemAccess === 'function',
    widevine: false,
    reason: null
  };
  if (result.eme) {
    try {
      await navigator.requestMediaKeySystemAccess('com.widevine.alpha', [{
        initDataTypes: ['cenc'],
        audioCapabilities: [{
          contentType: 'audio/mp4; codecs="mp4a.40.2"',
          robustness: 'SW_SECURE_CRYPTO'
        }],
        distinctiveIdentifier: 'not-allowed',
        persistentState: 'not-allowed',
        sessionTypes: ['temporary']
      }]);
      result.widevine = true;
    } catch (error) {
      result.reason = error.name;
    }
  } else {
    result.reason = 'EMEUnavailable';
  }
  window.qAMusikProbe = JSON.stringify(result);
})();
"""
PAGE = b'<!doctype html><meta charset="utf-8"><title>q_AMusik capability probe</title><script src="/probe.js" defer></script>'


class ProbeServer(BaseHTTPRequestHandler):
    def do_GET(self):
        resources = {"/": (PAGE, "text/html; charset=utf-8"),
                     "/probe.js": (SCRIPT, "text/javascript; charset=utf-8")}
        resource = resources.get(self.path)
        if resource is None:
            self.send_error(404)
            return
        payload, content_type = resource
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Security-Policy", "default-src 'none'; script-src 'self'; base-uri 'none'; frame-ancestors 'none'")
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, *_):
        pass


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--qt", choices=("5", "6"), required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    # La documentación oficial permite usar un CDM de una instalación existente.
    # No se descarga, copia, modifica ni redistribuye el módulo.
    cdm = Path("/opt/google/chrome/WidevineCdm/_platform_specific/linux_x64/libwidevinecdm.so")
    if cdm.is_file():
        existing = os.environ.get("QTWEBENGINE_CHROMIUM_FLAGS", "")
        os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = existing + " --widevine-path=" + str(cdm)
    if args.qt == "6":
        from PyQt6.QtCore import QCoreApplication, Qt, QTimer, QUrl, QT_VERSION_STR
        from PyQt6.QtWidgets import QApplication
        from PyQt6.QtWebEngineCore import QWebEnginePage, QWebEngineProfile
        attribute = Qt.ApplicationAttribute.AA_ShareOpenGLContexts
    else:
        from PyQt5.QtCore import QCoreApplication, Qt, QTimer, QUrl, QT_VERSION_STR
        from PyQt5.QtWidgets import QApplication
        from PyQt5.QtWebEngineWidgets import QWebEnginePage, QWebEngineProfile
        attribute = Qt.AA_ShareOpenGLContexts
    QCoreApplication.setAttribute(attribute)
    app = QApplication([sys.argv[0]])
    profile = QWebEngineProfile(app)  # Sin storageName: perfil off-the-record.
    assert profile.isOffTheRecord()
    page = QWebEnginePage(profile, app)
    report = {
        "purpose": "capability probe, not Apple Music playback",
        "qt": QT_VERSION_STR,
        "offTheRecord": True,
        "chromeCdmFilePresent": cdm.is_file(),
        "sandboxDisabledByProbe": False,
        "effectiveSandboxState": "not-measured",
        "appleAccountUsed": False,
        "licenseRequested": False,
    }
    server = ThreadingHTTPServer(("127.0.0.1", 0), ProbeServer)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    pending = False
    finished = False

    def write_result(result):
        nonlocal finished
        if finished:
            return
        finished = True
        report.update(result)
        report["prerequisitesAdvertised"] = bool(result.get("widevine") and result.get("aac"))
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2) + "\n")
        print(json.dumps(report, indent=2), flush=True)
        app.exit(2 if result.get("reason") == "ProbeTimeout" else 0)

    def receive(value):
        nonlocal pending
        pending = False
        if value and not finished:
            result = json.loads(value)
            if isinstance(result, dict):
                write_result(result)

    def poll():
        nonlocal pending
        if not pending and not finished:
            pending = True
            page.runJavaScript("window.qAMusikProbe || null", receive)

    timer = QTimer(app)
    timer.timeout.connect(poll)
    timer.start(250)
    QTimer.singleShot(30000, lambda: write_result({"reason": "ProbeTimeout"}))
    page.load(QUrl(f"http://127.0.0.1:{server.server_port}/"))
    try:
        status = app.exec() if args.qt == "6" else app.exec_()
    finally:
        timer.stop()
        server.shutdown()
        server.server_close()
        thread.join(2)
        del page
        del profile
    return status


if __name__ == "__main__":
    raise SystemExit(main())
