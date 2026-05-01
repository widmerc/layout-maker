# -*- coding: utf-8 -*-
"""
extent_tool.py  –  QgsMapTool zum Aufziehen eines Rechtecks auf dem Canvas.
Kompatibel mit QGIS 3 (PyQt5) und QGIS 4 (PyQt6).
"""

from qgis.PyQt.QtCore import Qt, pyqtSignal
from qgis.PyQt.QtGui import QColor
from qgis.core import QgsRectangle
from qgis.gui import QgsMapTool, QgsRubberBand

try:
    from qgis.core import QgsWkbTypes
    _POLYGON = QgsWkbTypes.PolygonGeometry
except (ImportError, AttributeError):
    try:
        from qgis.core import Qgis
        _POLYGON = Qgis.GeometryType.Polygon
    except Exception:
        _POLYGON = 2  # Fallback


class RectangleMapTool(QgsMapTool):
    """
    Map-Tool: Nutzer zieht auf dem Canvas ein Rechteck auf.
    Nach Loslassen der Maus wird das Signal `extent_selected` mit dem
    QgsRectangle emittiert und das Tool deaktiviert sich selbst.
    """

    extent_selected = pyqtSignal(object)   # QgsRectangle
    cancelled       = pyqtSignal()

    def __init__(self, canvas):
        super().__init__(canvas)
        self._canvas    = canvas
        self._rubber    = None
        self._start_pt  = None
        self._drawing   = False
        self.setCursor(Qt.CursorShape.CrossCursor)

    # ── interne Hilfsmethoden ──────────────────────────────────────────

    def _init_rubber(self):
        self._rubber = QgsRubberBand(self._canvas, _POLYGON)
        self._rubber.setColor(QColor(0, 120, 215, 60))
        self._rubber.setStrokeColor(QColor(0, 100, 180, 200))
        self._rubber.setWidth(2)
        self._rubber.setLineStyle(Qt.PenStyle.DashLine)

    def _update_rubber(self, start, end):
        if self._rubber is None:
            return
        self._rubber.reset(_POLYGON)
        from qgis.PyQt.QtCore import QgsRectangle as _  # unused – we use raw coords
        from qgis.core import QgsPointXY
        pts = [
            QgsPointXY(start.x(), start.y()),
            QgsPointXY(end.x(),   start.y()),
            QgsPointXY(end.x(),   end.y()),
            QgsPointXY(start.x(), end.y()),
        ]
        for i, p in enumerate(pts):
            self._rubber.addPoint(p, i == len(pts) - 1)

    def _remove_rubber(self):
        if self._rubber is not None:
            self._rubber.reset()
            self._canvas.scene().removeItem(self._rubber)
            self._rubber = None

    # ── QgsMapTool Events ───────────────────────────────────────────

    def canvasPressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._start_pt = self.toMapCoordinates(event.pos())
            self._drawing  = True
            self._init_rubber()

    def canvasMoveEvent(self, event):
        if self._drawing and self._start_pt is not None:
            cur = self.toMapCoordinates(event.pos())
            self._update_rubber(self._start_pt, cur)

    def canvasReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self._drawing:
            end = self.toMapCoordinates(event.pos())
            self._remove_rubber()
            self._drawing = False

            xmin = min(self._start_pt.x(), end.x())
            xmax = max(self._start_pt.x(), end.x())
            ymin = min(self._start_pt.y(), end.y())
            ymax = max(self._start_pt.y(), end.y())

            if abs(xmax - xmin) < 1e-6 or abs(ymax - ymin) < 1e-6:
                # Zu kleiner Bereich – ignorieren
                return

            rect = QgsRectangle(xmin, ymin, xmax, ymax)
            self._canvas.unsetMapTool(self)
            self.extent_selected.emit(rect)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self._remove_rubber()
            self._drawing = False
            self._canvas.unsetMapTool(self)
            self.cancelled.emit()

    def deactivate(self):
        self._remove_rubber()
        super().deactivate()
