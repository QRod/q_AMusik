"""Qt de la distribución: Qt 6 en Ubuntu 24.04; Qt 5 en Ubuntu 22.04."""

try:
    from PyQt6 import QtCore, QtGui, QtWidgets, QtWebEngineCore as Web
except ImportError:
    from PyQt5 import QtCore, QtGui, QtWidgets, QtWebEngineWidgets as Web


def enum(scope, group, name):
    return getattr(getattr(scope, group, scope), name)
