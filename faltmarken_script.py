# -*- coding: utf-8 -*-
from qgis.PyQt.QtCore import QCoreApplication, QPointF
from qgis.PyQt.QtGui import QColor, QPolygonF
from qgis.PyQt.QtWidgets import QDialog, QMessageBox
from qgis.core import (
    QgsLayoutItemPolyline,
    QgsLayoutPoint,
    QgsLayoutSize,
    QgsProject,
)

try:
    from qgis.core import QgsUnitTypes
    _MM = QgsUnitTypes.LayoutMillimeters
except AttributeError:
    from qgis.core import Qgis
    _MM = Qgis.LayoutUnit.Millimeters


def tr(msg):
    return QCoreApplication.translate('FaltmarkenScript', msg)


def _set_page_size(layout, width_mm, height_mm):
    page = layout.pageCollection().page(0)
    page.setPageSize(QgsLayoutSize(width_mm, height_mm, _MM))


def _add_line(layout, pen, x0, y0, x1, y1, item_id):
    from qgis.PyQt.QtCore import QPointF
    from qgis.PyQt.QtGui import QPolygonF

    poly = QPolygonF([QPointF(x0, y0), QPointF(x1, y1)])
    item = QgsLayoutItemPolyline(poly, layout)
    item.setPen(pen)
    item.setId(item_id)
    layout.addLayoutItem(item)
    # Position und Grösse werden automatisch aus dem Polygon abgeleitet


def draw_faltmarken(layout, mark_len=5.0, line_width=0.3):
    """
    Zeichnet Faltmarken im A4-Raster (210 x 297 mm).
    Das Raster beginnt IMMER bei (0, 0) – unabhaengig vom Plankopf.
    Muss NACH allfaelliger Seitengroessenanpassung aufgerufen werden.
    """
    from qgis.PyQt.QtGui import QPen

    page = layout.pageCollection().page(0)
    size = page.pageSize()
    W, H = size.width(), size.height()

    pen = QPen()
    pen.setColor(QColor(0, 0, 0))
    pen.setWidthF(line_width)

    # Vertikale Marken (oben + unten) alle 210 mm
    x, i = 0.0, 0
    while x <= W + 0.001:
        _add_line(layout, pen, x, 0.0,          x, mark_len,   f'fm_vt_{i}')
        _add_line(layout, pen, x, H - mark_len, x, H,          f'fm_vb_{i}')
        x += 210.0
        i += 1

    # Horizontale Marken (links + rechts) alle 297 mm
    y, j = 0.0, 0
    while y <= H + 0.001:
        _add_line(layout, pen, 0.0,          y, mark_len, y, f'fm_hl_{j}')
        _add_line(layout, pen, W - mark_len, y, W,        y, f'fm_hr_{j}')
        y += 297.0
        j += 1


def add_a4_raster_faltmarken(iface, parent=None):
    from .dialogs import FaltmarkenDialog

    manager = QgsProject.instance().layoutManager()
    layouts = manager.layouts()
    if not layouts:
        QMessageBox.warning(parent, tr('Layout Maker'),
                            tr('Es sind keine Layouts vorhanden.'))
        return

    dlg = FaltmarkenDialog([l.name() for l in layouts], parent)
    if dlg.exec() != QDialog.DialogCode.Accepted:
        return

    vals   = dlg.get_values()
    layout = next((l for l in layouts if l.name() == vals['layout_name']), None)
    if layout is None:
        QMessageBox.warning(parent, tr('Layout Maker'),
                            tr('Layout nicht gefunden.'))
        return

    if vals['change_size']:
        _set_page_size(layout, vals['page_width'], vals['page_height'])

    draw_faltmarken(layout, vals['mark_len'], vals['line_width'])
    QMessageBox.information(
        parent, tr('Layout Maker'),
        tr('Faltmarken wurden auf \u201e{0}\u201c gesetzt.').format(layout.name())
    )