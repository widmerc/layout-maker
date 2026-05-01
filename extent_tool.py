# -*- coding: utf-8 -*-
"""
extent_tool.py  –  Wrapper um QgsMapToolExtent.
Kompatibel mit QGIS 3 (PyQt5) und QGIS 4 (PyQt6).
"""

from qgis.PyQt.QtCore import Qt, pyqtSignal
from qgis.gui import QgsMapToolExtent


class ExtentMapTool(QgsMapToolExtent):
    """
    Dünner Wrapper um QgsMapToolExtent.
    Emittiert extent_selected (QgsRectangle) nach Aufziehen,
    oder cancelled bei ESC.
    """

    extent_selected = pyqtSignal(object)   # QgsRectangle
    cancelled       = pyqtSignal()

    def __init__(self, canvas):
        super().__init__(canvas)
        self._canvas = canvas
        self.setCursor(Qt.CursorShape.CrossCursor)

    def canvasReleaseEvent(self, event):
        super().canvasReleaseEvent(event)
        ext = self.extent()
        if ext and ext.width() > 0 and ext.height() > 0:
            self._canvas.unsetMapTool(self)
            self.extent_selected.emit(ext)
        else:
            self.cancelled.emit()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self._canvas.unsetMapTool(self)
            self.cancelled.emit()
        else:
            super().keyPressEvent(event)

    def deactivate(self):
        super().deactivate()
