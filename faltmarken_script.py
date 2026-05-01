# -*- coding: utf-8 -*-
"""
faltmarken_script.py  –  kompatibel mit QGIS 3 (PyQt5) und QGIS 4 (PyQt6)

Strichstärke wird korrekt in mm gesetzt via QgsSimpleLineSymbolLayer,
da QPen.setWidthF() Qt-Pixel (nicht mm) verwendet.

Hinweis: Der «Ursprung»-Parameter wurde entfernt. Der Ursprung ergibt sich
immer automatisch aus der Plankopf-Position (anchor), die dem draw_faltmarken-
Aufruf übergeben wird.
"""

from qgis.PyQt.QtCore import QCoreApplication, QPointF
from qgis.PyQt.QtGui import QPolygonF, QColor
from qgis.PyQt.QtWidgets import QDialog, QMessageBox
from qgis.core import (
    QgsLayoutItemPolyline,
    QgsLayoutItem,
    QgsLayoutSize,
    QgsLineSymbol,
    QgsSimpleLineSymbolLayer,
    QgsProject,
)

try:
    from qgis.core import QgsUnitTypes
    _MM  = QgsUnitTypes.LayoutMillimeters
    _SMM = QgsUnitTypes.RenderMillimeters
except AttributeError:
    from qgis.core import Qgis
    _MM  = Qgis.LayoutUnit.Millimeters
    _SMM = Qgis.RenderUnit.Millimeters


def tr(msg):
    return QCoreApplication.translate('FaltmarkenScript', msg)


# ── Anker → (from_right, from_bottom) ────────────────────────────────────────
# Der Ursprung der Faltmarken wird immer aus der Plankopf-Position abgeleitet:
# Plankopf unten rechts  → Faltmarken-Ursprung unten rechts
# Plankopf oben links    → Faltmarken-Ursprung oben links  ... usw.

_ANCHOR_TO_ORIGIN = {
    'oben links':   (False, False),
    'oben rechts':  (True,  False),
    'unten links':  (False, True),
    'unten rechts': (True,  True),
}

# Rückwärtskompatibilität: ORIGIN_LABELS wird nicht mehr im Dialog verwendet,
# bleibt aber als leere Liste erhalten damit alte Importe nicht brechen.
ORIGIN_LABELS = []


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


def _make_symbol(width_mm, color=QColor(0, 0, 0)):
    sl = QgsSimpleLineSymbolLayer(color)
    sl.setWidth(width_mm)
    sl.setWidthUnit(_SMM)
    sym = QgsLineSymbol()
    sym.changeSymbolLayer(0, sl)
    return sym


def _line(layout, symbol, x0, y0, x1, y1, item_id):
    item = QgsLayoutItemPolyline(
        QPolygonF([QPointF(x0, y0), QPointF(x1, y1)]), layout
    )
    item.setSymbol(symbol.clone())
    item.setId(item_id)
    item.setLocked(True)
    layout.addLayoutItem(item)
    item.setZValue(1000)


def _close_layout_designer(layout):
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
    anchor='unten rechts',
    remove_old=True,
    add_border=True,
    border_width=0.5,
):
    """
    Setzt Falt-/Schnittmarken im A4-Raster (210 mm x 297 mm).

    Parameters
    ----------
    layout       : QgsPrintLayout
    mark_len     : Länge jeder Marke in mm
    line_width   : Strichstärke Faltmarken in mm
    anchor       : Plankopf-Position – 'oben links' | 'oben rechts' |
                   'unten links' | 'unten rechts'  (bestimmt den Ursprung)
    remove_old   : Bestehende fm_*-Items vorher löschen
    add_border   : Rahmen um das Layout zeichnen
    border_width : Strichstärke Rahmen in mm
    """
    page = layout.pageCollection().page(0)
    W    = page.pageSize().width()
    H    = page.pageSize().height()
    r, b = _ANCHOR_TO_ORIGIN.get(anchor, (True, True))

    if remove_old:
        _remove_fm_items(layout)

    sym = _make_symbol(line_width)
    xs  = list(_frange(W, 0.0, -210.0) if r else _frange(0.0, W, 210.0))
    ys  = list(_frange(H, 0.0, -297.0) if b else _frange(0.0, H, 297.0))

    for i, x in enumerate(xs):
        _line(layout, sym, x, 0,          x, mark_len,  f'fm_vt_{i}')
        _line(layout, sym, x, H-mark_len, x, H,         f'fm_vb_{i}')

    for j, y in enumerate(ys):
        _line(layout, sym, 0,          y, mark_len, y,  f'fm_hl_{j}')
        _line(layout, sym, W-mark_len, y, W,        y,  f'fm_hr_{j}')

    if add_border:
        bw   = border_width if border_width > 0 else 0.5
        bsym = _make_symbol(bw)
        _line(layout, bsym, 0, 0, W, 0,  'fm_border_t')
        _line(layout, bsym, W, 0, W, H,  'fm_border_r')
        _line(layout, bsym, W, H, 0, H,  'fm_border_b')
        _line(layout, bsym, 0, H, 0, 0,  'fm_border_l')


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

    # Anchor aus Layout-Items ableiten falls möglich (Fallback: unten rechts)
    draw_faltmarken(
        layout,
        mark_len     = vals['mark_len'],
        line_width   = vals['line_width'],
        anchor       = 'unten rechts',
        remove_old   = vals['remove_old'],
        add_border   = vals['add_border'],
        border_width = vals['border_width'],
    )

    QMessageBox.information(
        parent, tr('Layout Maker'),
        tr('Faltmarken wurden auf \u201e{0}\u201c gesetzt.').format(layout.name())
    )
