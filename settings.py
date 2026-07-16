# -*- coding: utf-8 -*-
"""
settings.py  –  persistente Layout-Maker-Einstellungen (QSettings).
"""

from qgis.PyQt.QtCore import QSettings

_GROUP = 'LayoutMaker'
_DEFAULT_RASTER_W = 210.0   # A4
_DEFAULT_RASTER_H = 297.0


def get_falzmarken_raster():
    """Aktuell konfigurierte Falzmarken-Rastergrösse (Breite, Höhe) in mm."""
    s = QSettings()
    w = float(s.value(f'{_GROUP}/raster_w', _DEFAULT_RASTER_W))
    h = float(s.value(f'{_GROUP}/raster_h', _DEFAULT_RASTER_H))
    if w <= 0 or h <= 0:
        return _DEFAULT_RASTER_W, _DEFAULT_RASTER_H
    return w, h


def set_falzmarken_raster(width_mm, height_mm):
    s = QSettings()
    s.setValue(f'{_GROUP}/raster_w', width_mm)
    s.setValue(f'{_GROUP}/raster_h', height_mm)
