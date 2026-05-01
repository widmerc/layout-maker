# -*- coding: utf-8 -*-
"""
faltmarken_script.py  –  kompatibel mit QGIS 3 (PyQt5) und QGIS 4 (PyQt6)

Integriert den AddA4RasterFaltmarken-Algorithmus direkt als Funktion:
  - Wählbarer Ursprung (Plankopf-Position)
  - Optionaler Rahmen
  - Löscht bestehende fm_*-Items (schliesst Layout-Designer vorher)
  - Alle Items gesperrt, Z-Value 1000
"""

from qgis.PyQt.QtCore import QCoreApplication, QPointF
from qgis.PyQt.QtGui import QPolygonF, QColor, QPen
from qgis.PyQt.QtWidgets import QDialog, QMessageBox
from qgis.core import (
    QgsLayoutItemPolyline,
    QgsLayoutItem,
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


# ── Ursprünge: (Label, from_right, from_bottom) ──────────────────────────────
_ORIGINS = [
    ('Oben links',   False, False),
    ('Oben rechts',  True,  False),
    ('Unten links',  False, True),
    ('Unten rechts', True,  True),
]
ORIGIN_LABELS = [o[0] for o in _ORIGINS]


# ── Hilfsfunktionen ───────────────────────────────────────────────────────────

def _frange(start, stop, step):
    v = start
    if step > 0:
        while v <= stop + 0.001:
            yield v
            v += step
    else:
        while v >= stop - 0.001:
            yield v
            v += step


def _line(layout, pen, x0, y0, x1, y1, item_id):
    item = QgsLayoutItemPolyline(
        QPolygonF([QPointF(x0, y0), QPointF(x1, y1)]), layout
    )
    item.setPen(pen)
    item.setId(item_id)
    item.setLocked(True)
    layout.addLayoutItem(item)
    item.setZValue(1000)


def _close_layout_designer(layout):
    """Schliesst den Layout-Designer falls er für dieses Layout offen ist."""
    try:
        from qgis.utils import iface
        for designer in iface.openLayoutDesigners():
            if designer.layout() == layout:
                designer.close()
                return True
    except Exception:
        pass
    return False


def _remove_fm_items(layout):
    """Entfernt alle Items mit Prefix fm_. Schliesst vorher den Designer."""
    _close_layout_designer(layout)
    to_remove = [
        item for item in layout.items()
        if isinstance(item, QgsLayoutItem) and item.id().startswith('fm_')
    ]
    for item in to_remove:
        layout.removeLayoutItem(item)


def _set_page_size(layout, width_mm, height_mm):
    page = layout.pageCollection().page(0)
    page.setPageSize(QgsLayoutSize(width_mm, height_mm, _MM))


# ── Kernfunktion ──────────────────────────────────────────────────────────────

def draw_faltmarken(
    layout,
    mark_len=6.0,
    line_width=0.25,
    origin_index=0,
    remove_old=True,
    add_border=True,
    border_width=0.5,
):
    """
    Setzt Falt-/Schnittmarken im A4-Raster (210 mm × 297 mm) über die
    gesamte Layoutgrösse.

    Parameters
    ----------
    layout       : QgsPrintLayout
    mark_len     : Länge jeder Marke in mm
    line_width   : Strichstärke Faltmarken in mm
    origin_index : 0=oben links, 1=oben rechts, 2=unten links, 3=unten rechts
    remove_old   : Bestehende fm_*-Items vorher löschen
    add_border   : Rahmen um das Layout zeichnen
    border_width : Strichstärke Rahmen in mm
    """
    page     = layout.pageCollection().page(0)
    W        = page.pageSize().width()
    H        = page.pageSize().height()
    _, r, b  = _ORIGINS[origin_index]

    if remove_old:
        _remove_fm_items(layout)

    pen = QPen(QColor(0, 0, 0))
    pen.setWidthF(line_width)

    xs = list(_frange(W, 0.0, -210.0) if r else _frange(0.0, W, 210.0))
    ys = list(_frange(H, 0.0, -297.0) if b else _frange(0.0, H, 297.0))

    for i, x in enumerate(xs):
        _line(layout, pen, x, 0,          x, mark_len,  f'fm_vt_{i}')
        _line(layout, pen, x, H-mark_len, x, H,         f'fm_vb_{i}')

    for j, y in enumerate(ys):
        _line(layout, pen, 0,          y, mark_len, y,  f'fm_hl_{j}')
        _line(layout, pen, W-mark_len, y, W,        y,  f'fm_hr_{j}')

    if add_border:
        bw = border_width if border_width > 0 else 0.5
        bp = QPen(QColor(0, 0, 0))
        bp.setWidthF(bw)
        _line(layout, bp, 0, 0, W, 0,  'fm_border_t')
        _line(layout, bp, W, 0, W, H,  'fm_border_r')
        _line(layout, bp, W, H, 0, H,  'fm_border_b')
        _line(layout, bp, 0, H, 0, 0,  'fm_border_l')


# ── Dialog-Einstiegspunkt ─────────────────────────────────────────────────────

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

    draw_faltmarken(
        layout,
        mark_len     = vals['mark_len'],
        line_width   = vals['line_width'],
        origin_index = vals['origin_index'],
        remove_old   = vals['remove_old'],
        add_border   = vals['add_border'],
        border_width = vals['border_width'],
    )

    QMessageBox.information(
        parent, tr('Layout Maker'),
        tr('Faltmarken wurden auf \u201e{0}\u201c gesetzt.').format(layout.name())
    )
