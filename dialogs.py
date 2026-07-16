# -*- coding: utf-8 -*-
"""
dialogs.py  –  kompatibel mit QGIS 3 (PyQt5) und QGIS 4 (PyQt6)
"""

import os
from qgis.PyQt.QtCore import QCoreApplication, Qt
from qgis.PyQt.QtWidgets import (
    QButtonGroup, QCheckBox, QDialog, QDialogButtonBox,
    QDoubleSpinBox, QFileDialog, QFormLayout, QGroupBox,
    QHBoxLayout, QLabel, QLineEdit, QComboBox, QPushButton,
    QRadioButton, QSizePolicy, QSpinBox, QVBoxLayout, QFrame, QWidget,
)
from .settings import get_falzmarken_raster, set_falzmarken_raster


def tr(msg):
    # Kontext '@default': pylupdate5 kann bei freien Funktionen (kein
    # self.tr()) den Kontext nicht ermitteln und ordnet alles '@default'
    # zu — das muss hier exakt gespiegelt werden, sonst finden .qm-Dateien
    # die Übersetzung zur Laufzeit nicht (falscher Kontext = keine Treffer).
    return QCoreApplication.translate('@default', msg)


# ─────────────────────────────────────────────────────────────────────────────
#  Stil
# ─────────────────────────────────────────────────────────────────────────────

_STYLE = """
QDialog {
    background-color: #f5f5f5;
    font-family: "Segoe UI", "Helvetica Neue", Arial, sans-serif;
    font-size: 9pt;
}
QGroupBox {
    font-weight: bold; font-size: 9pt;
    border: 1px solid #d0d0d0; border-radius: 6px;
    margin-top: 10px; padding: 8px 10px 6px 10px;
    background-color: #ffffff;
}
QGroupBox::title {
    subcontrol-origin: margin; subcontrol-position: top left;
    padding: 0 6px; color: #2c5f6e;
}
QGroupBox:disabled { background-color: #f8f8f8; }
QLabel          { color: #333333; }
QLabel#header   { font-size: 11pt; font-weight: bold; color: #2c5f6e; }
QLabel#desc     { font-size: 8pt;  color: #666666; }
QLabel#info     { font-size: 8pt;  color: #888888; font-style: italic; }
QLineEdit, QComboBox, QDoubleSpinBox, QSpinBox {
    border: 1px solid #c8c8c8; border-radius: 4px;
    padding: 4px 8px; background-color: #ffffff;
    min-height: 22px; selection-background-color: #3d8fa0;
}
QLineEdit:focus, QComboBox:focus, QDoubleSpinBox:focus, QSpinBox:focus {
    border: 1px solid #3d8fa0;
}
QLineEdit:read-only      { background-color: #f0f0f0; color: #555; }
QDoubleSpinBox:disabled,
QSpinBox:disabled,
QComboBox:disabled        { background-color: #f0f0f0; color: #aaa; }
QPushButton {
    border: 1px solid #c8c8c8; border-radius: 4px;
    padding: 5px 14px; background-color: #f0f0f0; min-height: 24px;
}
QPushButton:hover   { background-color: #e0eef1; border-color: #3d8fa0; }
QPushButton#browse  { padding: 4px 10px; min-width: 100px; font-size: 8pt; }
QFrame#divider      { color: #d0d0d0; }
QCheckBox           { spacing: 6px; }
QRadioButton        { spacing: 4px; }
"""

_BTN_OK = (
    "QPushButton { background-color:#2c5f6e; color:white; border:1px solid #1f4a58;"
    " border-radius:4px; padding:5px 20px; font-weight:bold;"
    " min-height:26px; min-width:80px; }"
    "QPushButton:hover   { background-color:#3d8fa0; }"
    "QPushButton:pressed { background-color:#1f4a58; }"
    "QPushButton:disabled{ background-color:#a0b8be; border-color:#8aacb3; }"
)
_BTN_CANCEL = "QPushButton { min-height:26px; min-width:80px; }"

_BTN_DRAW = (
    "QPushButton { background-color:#e8f4f7; color:#1f4a58;"
    " border:2px solid #3d8fa0; border-radius:4px;"
    " padding:5px 14px; min-height:26px; font-weight:bold; }"
    "QPushButton:hover   { background-color:#c5e3eb; }"
    "QPushButton:pressed { background-color:#a8d5e0; }"
    "QPushButton:checked { background-color:#2c5f6e; color:white; border-color:#1f4a58; }"
)


# ─────────────────────────────────────────────────────────────────────────────
#  Kleine Helfer
# ─────────────────────────────────────────────────────────────────────────────

def _divider():
    f = QFrame(); f.setObjectName('divider')
    f.setFrameShape(QFrame.Shape.HLine)
    f.setFrameShadow(QFrame.Shadow.Sunken)
    return f


def _spinbox(value, lo, hi, decimals, suffix=' mm'):
    sb = QDoubleSpinBox()
    sb.setDecimals(decimals); sb.setMinimum(lo)
    sb.setMaximum(hi); sb.setValue(value); sb.setSuffix(suffix)
    sb.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
    return sb


def _bbox(parent_dlg, auto_accept=True):
    """
    QDialogButtonBox (OK/Abbrechen), PyQt6-sicher.

    auto_accept=False: der OK-Klick schliesst den Dialog NICHT automatisch
    (kein self.accept()) — der Aufrufer muss selbst validieren und erst bei
    Erfolg accept() aufrufen. Nötig, wenn eine Aktion fehlschlagen kann
    (z. B. Layoutname existiert bereits) und die eingegebenen Werte dabei
    nicht verloren gehen sollen.
    """
    bb = QDialogButtonBox(
        QDialogButtonBox.StandardButton.Ok |
        QDialogButtonBox.StandardButton.Cancel
    )
    ok  = bb.button(QDialogButtonBox.StandardButton.Ok)
    cxl = bb.button(QDialogButtonBox.StandardButton.Cancel)
    ok.setStyleSheet(_BTN_OK);    ok.setText('OK')
    cxl.setStyleSheet(_BTN_CANCEL); cxl.setText('Abbrechen')
    if auto_accept:
        bb.accepted.connect(parent_dlg.accept)
    bb.rejected.connect(parent_dlg.reject)
    return bb, ok


# ─────────────────────────────────────────────────────────────────────────────
#  Wiederverwendbare Bausteine (früher in jedem Dialog dupliziert)
# ─────────────────────────────────────────────────────────────────────────────

ANCHORS = ['oben links', 'oben rechts', 'unten links', 'unten rechts']


def _anchor_combo(default='oben links'):
    """
    Anker-Auswahl. Angezeigt wird eine übersetzte Beschriftung, intern
    verwendet (item-data, über currentData() auslesen!) bleibt immer der
    fixe deutsche Schlüssel aus ANCHORS — davon hängt die ganze Platzierungs-
    logik ab (Zeichenketten-Vergleiche wie 'links' in anchor), unabhängig
    von der UI-Sprache.
    """
    labels = {
        'oben links':   tr('oben links'),
        'oben rechts':  tr('oben rechts'),
        'unten links':  tr('unten links'),
        'unten rechts': tr('unten rechts'),
    }
    combo = QComboBox()
    for key in ANCHORS:
        combo.addItem(labels[key], key)
    idx = combo.findData(default)
    combo.setCurrentIndex(idx if idx >= 0 else 0)
    return combo


def _falzmarken_group(width_min=0.01, extra_row=None):
    """Gruppe 'Falzmarken-Parameter' (Markenlänge + Strichstärke)."""
    grp = QGroupBox(tr('Falzmarken-Parameter'))
    f = QFormLayout(grp)
    f.setLabelAlignment(Qt.AlignmentFlag.AlignRight); f.setSpacing(8)
    spin_len = _spinbox(6.0, 0.5, 20.0, 1)
    f.addRow(tr('Markenlänge:'), spin_len)
    spin_w = _spinbox(0.25, width_min, 5.0, 2)
    f.addRow(tr('Strichstärke:'), spin_w)
    if extra_row is not None:
        f.addRow('', extra_row)
    return grp, spin_len, spin_w


def _border_group():
    """Checkbare Gruppe 'Rahmen' (Strichstärke Rahmen)."""
    grp = QGroupBox(tr('Rahmen'))
    grp.setCheckable(True); grp.setChecked(True)
    f = QFormLayout(grp)
    f.setLabelAlignment(Qt.AlignmentFlag.AlignRight); f.setSpacing(8)
    spin_border = _spinbox(0.5, 0.01, 5.0, 2)
    f.addRow(tr('Strichstärke Rahmen:'), spin_border)
    return grp, spin_border


# ─────────────────────────────────────────────────────────────────────────────
#  PageSizeWidget
# ─────────────────────────────────────────────────────────────────────────────

_PAGE_SIZES = {
    'A0':                (841.0,  1189.0),
    'A1':                (594.0,   841.0),
    'A2':                (420.0,   594.0),
    'A3':                (297.0,   420.0),
    'A4':                (210.0,   297.0),
    'Benutzerdefiniert': (None,    None ),
}


class PageSizeWidget(QWidget):
    def __init__(self, default_format='A3', default_landscape=True, parent=None):
        super().__init__(parent)
        self._build(default_format, default_landscape)

    def _build(self, def_fmt, def_land):
        layout = QVBoxLayout(self)
        layout.setSpacing(6)
        layout.setContentsMargins(0, 0, 0, 0)

        row1 = QHBoxLayout()
        row1.setSpacing(8)
        self.combo_format = QComboBox()
        # A0–A4 sind international genormte Bezeichnungen (keine Übersetzung
        # nötig); 'Benutzerdefiniert' ist ein deutsches Wort und wird daher
        # übersetzt angezeigt — intern (item-data, currentData()) bleibt der
        # feste Schlüssel aus _PAGE_SIZES, egal welche UI-Sprache aktiv ist.
        for key in _PAGE_SIZES:
            label = tr('Benutzerdefiniert') if key == 'Benutzerdefiniert' else key
            self.combo_format.addItem(label, key)
        idx = self.combo_format.findData(def_fmt)
        self.combo_format.setCurrentIndex(idx if idx >= 0 else 0)
        self.combo_format.setMinimumWidth(140)
        row1.addWidget(self.combo_format)
        self.radio_portrait  = QRadioButton(tr('Hochformat'))
        self.radio_landscape = QRadioButton(tr('Querformat'))
        grp = QButtonGroup(self)
        grp.addButton(self.radio_portrait)
        grp.addButton(self.radio_landscape)
        (self.radio_landscape if def_land else self.radio_portrait).setChecked(True)
        row1.addWidget(self.radio_portrait)
        row1.addWidget(self.radio_landscape)
        row1.addStretch()
        layout.addLayout(row1)

        row2 = QHBoxLayout()
        row2.setSpacing(6)
        lbl_w = QLabel(tr('Breite:')); lbl_w.setFixedWidth(44)
        self.spin_w = _spinbox(0.0, 1.0, 10000.0, 1); self.spin_w.setFixedWidth(90)
        lbl_h = QLabel(tr('Höhe:'));  lbl_h.setFixedWidth(38)
        self.spin_h = _spinbox(0.0, 1.0, 10000.0, 1); self.spin_h.setFixedWidth(90)
        self.lbl_info = QLabel(); self.lbl_info.setObjectName('info')
        row2.addWidget(lbl_w); row2.addWidget(self.spin_w)
        row2.addSpacing(6)
        row2.addWidget(lbl_h); row2.addWidget(self.spin_h)
        row2.addSpacing(6)
        row2.addWidget(self.lbl_info)
        row2.addStretch()
        layout.addLayout(row2)

        self.combo_format.currentIndexChanged.connect(self._on_format_changed)
        self.radio_portrait.toggled.connect(self._on_orientation_changed)
        self.radio_landscape.toggled.connect(self._on_orientation_changed)
        self.spin_w.valueChanged.connect(self._on_custom_changed)
        self.spin_h.valueChanged.connect(self._on_custom_changed)
        self._on_format_changed()

    def _is_custom(self):
        return self.combo_format.currentData() == 'Benutzerdefiniert'

    def _on_format_changed(self, _index=None):
        custom = self._is_custom()
        self.radio_portrait.setEnabled(not custom)
        self.radio_landscape.setEnabled(not custom)
        self.spin_w.setReadOnly(not custom)
        self.spin_h.setReadOnly(not custom)
        if not custom:
            self._fill_from_format()
            self.lbl_info.setText('')
        else:
            self.lbl_info.setText(tr('Werte direkt eingeben'))

    def _on_orientation_changed(self, _checked):
        if not self._is_custom():
            self._fill_from_format()

    def _on_custom_changed(self):
        if self._is_custom():
            self.lbl_info.setText(
                f'{self.spin_w.value():.1f} × {self.spin_h.value():.1f} mm'
            )

    def _fill_from_format(self):
        fmt = self.combo_format.currentData()
        w0, h0 = _PAGE_SIZES[fmt]
        if w0 is None:
            return
        if self.radio_landscape.isChecked():
            w, h = max(w0, h0), min(w0, h0)
        else:
            w, h = min(w0, h0), max(w0, h0)
        for sb in (self.spin_w, self.spin_h):
            sb.blockSignals(True)
        self.spin_w.setValue(w)
        self.spin_h.setValue(h)
        for sb in (self.spin_w, self.spin_h):
            sb.blockSignals(False)
        self.lbl_info.setText(f'{w:.0f} × {h:.0f} mm')

    def get_size_mm(self):
        return self.spin_w.value(), self.spin_h.value()

    def set_enabled(self, enabled: bool):
        for child in (self.combo_format, self.radio_portrait,
                      self.radio_landscape, self.spin_w, self.spin_h):
            child.setEnabled(enabled)


def _match_format(width_mm, height_mm):
    """Findet den passenden _PAGE_SIZES-Eintrag (+ Orientierung) zu einer
    mm-Grösse, oder 'Benutzerdefiniert' falls kein Standardformat passt."""
    for name, (fw, fh) in _PAGE_SIZES.items():
        if fw is None:
            continue
        if (round(width_mm) == round(fw) and round(height_mm) == round(fh)) or \
           (round(width_mm) == round(fh) and round(height_mm) == round(fw)):
            return name, width_mm >= height_mm
    return 'Benutzerdefiniert', width_mm >= height_mm


# ─────────────────────────────────────────────────────────────────────────────
#  SettingsDialog
# ─────────────────────────────────────────────────────────────────────────────

class SettingsDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(tr('Einstellungen'))
        self.setMinimumWidth(400)
        self.setStyleSheet(_STYLE)
        self._build()

    def _build(self):
        root = QVBoxLayout(self)
        root.setSpacing(12); root.setContentsMargins(16, 16, 16, 16)

        hdr = QLabel(tr('Layout Maker – Einstellungen'))
        hdr.setObjectName('header'); root.addWidget(hdr)
        root.addWidget(_divider())

        grp = QGroupBox(tr('Falzmarken-Raster'))
        v = QVBoxLayout(grp); v.setSpacing(6)
        note = QLabel(tr(
            'Rastergrösse, nach der die Falzmarken auf der Seite verteilt\n'
            'werden (Standard: A4, 210 × 297 mm).'
        ))
        note.setObjectName('desc'); note.setWordWrap(True)
        v.addWidget(note)

        cur_w, cur_h = get_falzmarken_raster()
        fmt, landscape = _match_format(cur_w, cur_h)
        self.raster_size_w = PageSizeWidget(fmt, landscape)
        if fmt == 'Benutzerdefiniert':
            self.raster_size_w.spin_w.setValue(cur_w)
            self.raster_size_w.spin_h.setValue(cur_h)
        v.addWidget(self.raster_size_w)
        root.addWidget(grp)

        bb, _ = _bbox(self)
        root.addWidget(bb)

    def get_values(self):
        w, h = self.raster_size_w.get_size_mm()
        return {'raster_w': w, 'raster_h': h}


# ─────────────────────────────────────────────────────────────────────────────
#  FalzmarkenDialog
# ─────────────────────────────────────────────────────────────────────────────

class FalzmarkenDialog(QDialog):

    def __init__(self, layout_names, parent=None):
        super().__init__(parent)
        self.setWindowTitle(tr('Falzmarken hinzufügen'))
        self.setMinimumWidth(440)
        self.setStyleSheet(_STYLE)
        self._build(layout_names)

    def _build(self, names):
        root = QVBoxLayout(self)
        root.setSpacing(12); root.setContentsMargins(16, 16, 16, 16)

        hdr = QLabel(tr('Falzmarken auf Layout setzen'))
        hdr.setObjectName('header'); root.addWidget(hdr)
        root.addWidget(_divider())

        grp1 = QGroupBox(tr('Ziel-Layout'))
        f1 = QFormLayout(grp1)
        f1.setLabelAlignment(Qt.AlignmentFlag.AlignRight); f1.setSpacing(8)
        self.combo = QComboBox(); self.combo.addItems(names)
        f1.addRow(tr('Layout:'), self.combo)
        root.addWidget(grp1)

        grp_anchor = QGroupBox(tr('Plankopf-Position'))
        f_anchor = QFormLayout(grp_anchor)
        f_anchor.setLabelAlignment(Qt.AlignmentFlag.AlignRight); f_anchor.setSpacing(8)
        self.combo_anchor = _anchor_combo('oben links')
        f_anchor.addRow(tr('Plankopf-Position:'), self.combo_anchor)
        root.addWidget(grp_anchor)

        self.chk_remove = QCheckBox(tr('Bestehende Falzmarken (fm_*) vorher löschen'))
        self.chk_remove.setChecked(True)
        grp3, self.spin_len, self.spin_w = _falzmarken_group(
            width_min=0.01, extra_row=self.chk_remove)
        root.addWidget(grp3)

        grp4, self.spin_border = _border_group()
        self._grp_border = grp4
        root.addWidget(grp4)

        bb = QDialogButtonBox()
        btn_set = bb.addButton(tr('Falzmarken setzen'), QDialogButtonBox.ButtonRole.AcceptRole)
        btn_set.setStyleSheet(_BTN_OK)
        btn_cancel = bb.addButton(QDialogButtonBox.StandardButton.Cancel)
        btn_cancel.setText(tr('Abbrechen'))
        btn_set.clicked.connect(self.accept)
        btn_cancel.clicked.connect(self.reject)
        root.addWidget(bb)

    def get_values(self):
        return {
            'layout_name':  self.combo.currentText(),
            'anchor':       self.combo_anchor.currentData(),
            'mark_len':     self.spin_len.value(),
            'line_width':   self.spin_w.value(),
            'remove_old':   self.chk_remove.isChecked(),
            'add_border':   self._grp_border.isChecked(),
            'border_width': self.spin_border.value(),
        }


# ─────────────────────────────────────────────────────────────────────────────
#  RemoveFalzmarkenDialog  –  eigener, schlanker Dialog fürs blosse Entfernen
# ─────────────────────────────────────────────────────────────────────────────

class RemoveFalzmarkenDialog(QDialog):

    def __init__(self, layout_names, parent=None):
        super().__init__(parent)
        self.setWindowTitle(tr('Falzmarken entfernen'))
        self.setMinimumWidth(360)
        self.setStyleSheet(_STYLE)
        self._build(layout_names)

    def _build(self, names):
        root = QVBoxLayout(self)
        root.setSpacing(12); root.setContentsMargins(16, 16, 16, 16)

        hdr = QLabel(tr('Falzmarken von Layout entfernen'))
        hdr.setObjectName('header'); root.addWidget(hdr)
        root.addWidget(_divider())

        grp1 = QGroupBox(tr('Ziel-Layout'))
        f1 = QFormLayout(grp1)
        f1.setLabelAlignment(Qt.AlignmentFlag.AlignRight); f1.setSpacing(8)
        self.combo = QComboBox(); self.combo.addItems(names)
        f1.addRow(tr('Layout:'), self.combo)
        root.addWidget(grp1)

        note = QLabel(tr('Entfernt alle vorhandenen Falzmarken (fm_*) vom gewählten Layout.'))
        note.setObjectName('desc'); note.setWordWrap(True)
        root.addWidget(note)

        bb, _ = _bbox(self)
        root.addWidget(bb)

    def get_layout_name(self):
        return self.combo.currentText()


# ─────────────────────────────────────────────────────────────────────────────
#  PlanDialog  –  Plan erstellen (Kartenausschnitt aufziehen ODER vordefinierte
#  Plangrösse, mit optionalem Plankopf) — vereint die früheren Dialoge
#  „Layout aus Vorlage“ und „Plan aus Kartenausschnitt“.
# ─────────────────────────────────────────────────────────────────────────────

class PlanDialog(QDialog):
    """
    Nicht-modaler Dialog (wegen des Karten-Aufzieh-Tools). Öffnet sich mit
    show(); der Aufrufer reagiert auf das accepted-Signal.
    """

    def __init__(self, iface, parent=None):
        super().__init__(parent)
        self.iface       = iface
        self._map_tool   = None
        self._prev_tool  = None
        self.setWindowTitle(tr('Plan erstellen'))
        self.setMinimumWidth(500)
        self.setStyleSheet(_STYLE)
        self.setWindowFlags(
            Qt.WindowType.Window |
            Qt.WindowType.WindowCloseButtonHint |
            Qt.WindowType.WindowStaysOnTopHint
        )
        self._build()
        self._load_current_extent()

    def _build(self):
        root = QVBoxLayout(self)
        root.setSpacing(12); root.setContentsMargins(16, 16, 16, 16)

        hdr = QLabel(tr('Neuen Plan erstellen'))
        hdr.setObjectName('header'); hdr.setWordWrap(True)
        root.addWidget(hdr)
        root.addWidget(_divider())

        # ── Kartenfläche: Aufziehen ODER vordefinierte Grösse ──────────
        grp_area = QGroupBox(tr('Kartenfläche'))
        v_area = QVBoxLayout(grp_area); v_area.setSpacing(8)

        row_mode = QHBoxLayout()
        self.radio_draw  = QRadioButton(tr('Ausschnitt auf Karte aufziehen'))
        self.radio_fixed = QRadioButton(tr('Vordefinierte Plangrösse'))
        self.radio_draw.setChecked(True)
        mode_grp = QButtonGroup(self)
        mode_grp.addButton(self.radio_draw)
        mode_grp.addButton(self.radio_fixed)
        row_mode.addWidget(self.radio_draw)
        row_mode.addWidget(self.radio_fixed)
        row_mode.addStretch()
        v_area.addLayout(row_mode)

        # -- Variante A: Ausschnitt aufziehen --
        self._draw_widget = QWidget()
        dv = QVBoxLayout(self._draw_widget); dv.setContentsMargins(0, 0, 0, 0); dv.setSpacing(8)

        self.btn_draw = QPushButton(tr('⤵  Ausschnitt auf Karte aufziehen'))
        self.btn_draw.setStyleSheet(_BTN_DRAW)
        self.btn_draw.setToolTip(tr(
            'Dialog wird temporär ausgeblendet.\n'
            'Auf der Karte ein Rechteck aufziehen (Linksklick + Ziehen).\n'
            'ESC bricht ab.'
        ))
        self.btn_draw.clicked.connect(self._start_draw)
        dv.addWidget(self.btn_draw)

        f_ext = QFormLayout(); f_ext.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        f_ext.setSpacing(6)

        self.spin_xmin = _spinbox(0.0, -1e9, 1e9, 4, ' m'); self.spin_xmin.setMaximumWidth(180)
        self.spin_xmax = _spinbox(0.0, -1e9, 1e9, 4, ' m'); self.spin_xmax.setMaximumWidth(180)
        self.spin_ymin = _spinbox(0.0, -1e9, 1e9, 4, ' m'); self.spin_ymin.setMaximumWidth(180)
        self.spin_ymax = _spinbox(0.0, -1e9, 1e9, 4, ' m'); self.spin_ymax.setMaximumWidth(180)

        row_x = QHBoxLayout()
        row_x.addWidget(QLabel('X min:')); row_x.addWidget(self.spin_xmin)
        row_x.addSpacing(8)
        row_x.addWidget(QLabel('X max:')); row_x.addWidget(self.spin_xmax)
        row_x.addStretch()

        row_y = QHBoxLayout()
        row_y.addWidget(QLabel('Y min:')); row_y.addWidget(self.spin_ymin)
        row_y.addSpacing(8)
        row_y.addWidget(QLabel('Y max:')); row_y.addWidget(self.spin_ymax)
        row_y.addStretch()

        f_ext.addRow(row_x)
        f_ext.addRow(row_y)

        btn_reload = QPushButton(tr('⟳  Aktuellen Ausschnitt übernehmen'))
        btn_reload.setToolTip(tr('Setzt die Koordinaten auf den jetzt sichtbaren Ausschnitt.'))
        btn_reload.clicked.connect(self._load_current_extent)
        f_ext.addRow('', btn_reload)

        dv.addLayout(f_ext)
        v_area.addWidget(self._draw_widget)

        # -- Variante B: vordefinierte Plangrösse --
        self._fixed_widget = QWidget()
        fv = QVBoxLayout(self._fixed_widget); fv.setContentsMargins(0, 0, 0, 0)
        self.page_size_w = PageSizeWidget('A3', True)
        fv.addWidget(self.page_size_w)
        v_area.addWidget(self._fixed_widget)

        root.addWidget(grp_area)

        # ── Massstab & berechnete Grösse ────────────────────────────────
        grp_scale = QGroupBox(tr('Massstab'))
        f_scale = QFormLayout(grp_scale)
        f_scale.setLabelAlignment(Qt.AlignmentFlag.AlignRight); f_scale.setSpacing(8)

        scale_row = QHBoxLayout()
        scale_row.addWidget(QLabel('1 :'))
        self.spin_scale = QSpinBox()
        self.spin_scale.setMinimum(1)
        self.spin_scale.setMaximum(1000000)
        self.spin_scale.setValue(1000)
        self.spin_scale.setSingleStep(500)
        self.spin_scale.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        scale_row.addWidget(self.spin_scale)
        scale_row.addStretch()
        f_scale.addRow(tr('Massstab:'), scale_row)

        self.lbl_size_result = QLabel('–')
        self.lbl_size_result.setObjectName('info')
        self._lbl_size_row_label = QLabel(tr('Plangrösse (berechnet):'))
        f_scale.addRow(self._lbl_size_row_label, self.lbl_size_result)
        root.addWidget(grp_scale)

        # ── Layout-Einstellungen ──────────────────────────────────────
        grp_lay = QGroupBox(tr('Layout-Einstellungen'))
        f_lay = QFormLayout(grp_lay)
        f_lay.setLabelAlignment(Qt.AlignmentFlag.AlignRight); f_lay.setSpacing(8)
        self.edit_name = QLineEdit()
        self.edit_name.setPlaceholderText(tr('z. B.  Plan_1000'))
        self.edit_name.setText(tr('Neuer Plan'))
        f_lay.addRow(tr('Layoutname:'), self.edit_name)
        self.combo_anchor = _anchor_combo('oben links')
        f_lay.addRow(tr('Plankopf-Position:'), self.combo_anchor)
        root.addWidget(grp_lay)

        # ── Plankopf-Vorlage (optional) ───────────────────────────────
        grp_tpl = QGroupBox(tr('Plankopf-Vorlage (.qpt) – optional'))
        grp_tpl.setCheckable(True); grp_tpl.setChecked(False)
        self._grp_tpl = grp_tpl
        v_tpl = QVBoxLayout(grp_tpl); v_tpl.setSpacing(4)
        note_tpl = QLabel(tr(
            'Der Plankopf ist nur das Kopf-/Stempelfeld (kein eigenes Kartenbild).\n'
            'Er wird an der gewählten Plankopf-Position angehängt, die Kartenfläche\n'
            'füllt automatisch den restlichen Platz auf der Seite.'
        ))
        note_tpl.setObjectName('desc'); note_tpl.setWordWrap(True)
        v_tpl.addWidget(note_tpl)
        row_tpl = QHBoxLayout()
        self.edit_tpl_path = QLineEdit()
        self.edit_tpl_path.setPlaceholderText(tr('Pfad zur .qpt-Datei …'))
        self.edit_tpl_path.setReadOnly(True)
        btn_tpl = QPushButton(tr('Durchsuchen …')); btn_tpl.setObjectName('browse')
        btn_tpl.clicked.connect(self._browse_template)
        row_tpl.addWidget(self.edit_tpl_path); row_tpl.addWidget(btn_tpl)
        v_tpl.addLayout(row_tpl)
        root.addWidget(grp_tpl)

        # ── Falzmarken ─────────────────────────────────────────────────
        grp_fm, self.spin_len, self.spin_lw = _falzmarken_group(width_min=0.05)
        root.addWidget(grp_fm)

        # ── Rahmen ────────────────────────────────────────────────────
        grp_brd, self.spin_border = _border_group()
        self._grp_border = grp_brd
        root.addWidget(grp_brd)

        # ── OK / Abbrechen ─────────────────────────────────────────────
        # auto_accept=False: plan_script.py validiert (z. B. Layoutname frei?)
        # und schliesst den Dialog nur bei Erfolg — sonst blieben bei einem
        # Fehler alle eingegebenen Werte erhalten statt verloren zu gehen.
        bb, self._ok_btn = _bbox(self, auto_accept=False)
        root.addWidget(bb)

        # Modus-Umschaltung
        self.radio_draw.toggled.connect(self._on_mode_changed)
        self._on_mode_changed()

        # Live-Berechnung
        for sb in (self.spin_xmin, self.spin_xmax, self.spin_ymin, self.spin_ymax):
            sb.valueChanged.connect(self._update_size_label)
        self.spin_scale.valueChanged.connect(self._update_size_label)
        self.page_size_w.spin_w.valueChanged.connect(self._update_size_label)
        self.page_size_w.spin_h.valueChanged.connect(self._update_size_label)
        self._grp_tpl.toggled.connect(self._update_size_label)
        self.edit_name.textChanged.connect(self._validate)
        self._validate()
        self._update_size_label()

    # ── Modus: aufziehen vs. vordefinierte Grösse ──────────────────────

    def _on_mode_changed(self, _checked=None):
        draw = self.radio_draw.isChecked()
        self._draw_widget.setVisible(draw)
        self._fixed_widget.setVisible(not draw)
        self._update_size_label()

    # ── Aufzieh-Logik ────────────────────────────────────────────────

    def _start_draw(self):
        """Dialog minimieren, Map-Tool aktivieren."""
        from .extent_tool import ExtentMapTool
        canvas = self.iface.mapCanvas()
        self._prev_tool = canvas.mapTool()
        self._map_tool  = ExtentMapTool(canvas)
        self._map_tool.extent_selected.connect(self._on_extent_selected)
        self._map_tool.cancelled.connect(self._on_draw_cancelled)
        self.hide()
        canvas.setMapTool(self._map_tool)
        self.iface.mainWindow().statusBar().showMessage(
            tr('Ausschnitt aufziehen: Linksklick + Ziehen. ESC = Abbruch.'), 0
        )

    def _on_extent_selected(self, rect):
        self.iface.mainWindow().statusBar().clearMessage()
        self._restore_tool()
        for sb in (self.spin_xmin, self.spin_xmax, self.spin_ymin, self.spin_ymax):
            sb.blockSignals(True)
        self.spin_xmin.setValue(rect.xMinimum())
        self.spin_xmax.setValue(rect.xMaximum())
        self.spin_ymin.setValue(rect.yMinimum())
        self.spin_ymax.setValue(rect.yMaximum())
        for sb in (self.spin_xmin, self.spin_xmax, self.spin_ymin, self.spin_ymax):
            sb.blockSignals(False)
        self._update_size_label()
        self.show()
        self.raise_()
        self.activateWindow()

    def _on_draw_cancelled(self):
        self.iface.mainWindow().statusBar().clearMessage()
        self._restore_tool()
        self.show()
        self.raise_()
        self.activateWindow()

    def _restore_tool(self):
        canvas = self.iface.mapCanvas()
        if self._prev_tool is not None:
            canvas.setMapTool(self._prev_tool)
        else:
            canvas.unsetMapTool(self._map_tool)
        self._map_tool = None

    # ── Hilfsmethoden ───────────────────────────────────────────────

    def _load_current_extent(self):
        try:
            ext = self.iface.mapCanvas().extent()
            for sb in (self.spin_xmin, self.spin_xmax, self.spin_ymin, self.spin_ymax):
                sb.blockSignals(True)
            self.spin_xmin.setValue(ext.xMinimum())
            self.spin_xmax.setValue(ext.xMaximum())
            self.spin_ymin.setValue(ext.yMinimum())
            self.spin_ymax.setValue(ext.yMaximum())
            for sb in (self.spin_xmin, self.spin_xmax, self.spin_ymin, self.spin_ymax):
                sb.blockSignals(False)
            self._update_size_label()
        except Exception:
            pass

    def _update_size_label(self):
        scale = self.spin_scale.value()
        if self.radio_draw.isChecked():
            self._lbl_size_row_label.setText(tr('Plangrösse (berechnet):'))
            dx = self.spin_xmax.value() - self.spin_xmin.value()
            dy = self.spin_ymax.value() - self.spin_ymin.value()
            if dx <= 0 or dy <= 0 or scale <= 0:
                self.lbl_size_result.setText(tr('– (ungültiger Ausschnitt)'))
                return
            w_mm = (dx / scale) * 1000.0
            h_mm = (dy / scale) * 1000.0
            self.lbl_size_result.setText(f'{w_mm:.1f} × {h_mm:.1f} mm')
        else:
            self._lbl_size_row_label.setText(tr('Kartenausschnitt (berechnet):'))
            w_mm, h_mm = self.page_size_w.get_size_mm()
            if w_mm <= 0 or h_mm <= 0 or scale <= 0:
                self.lbl_size_result.setText(tr('– (ungültige Plangrösse)'))
                return
            if self._grp_tpl.isChecked():
                # Plankopf-Spaltenbreite ist hier noch unbekannt (Vorlage wird
                # erst beim Erstellen geladen) -> keine falsch genaue Zahl zeigen.
                self.lbl_size_result.setText(
                    tr('– (abhängig von Plankopf-Breite, wird beim Erstellen berechnet)'))
                return
            dx = (w_mm / 1000.0) * scale
            dy = (h_mm / 1000.0) * scale
            self.lbl_size_result.setText(f'ca. {dx:.0f} × {dy:.0f} m')

    def _browse_template(self):
        path, _ = QFileDialog.getOpenFileName(
            self, tr('Plankopf-Vorlage auswählen'), '', 'QGIS Template (*.qpt)')
        if path:
            self.edit_tpl_path.setText(path)

    def _validate(self):
        self._ok_btn.setEnabled(bool(self.edit_name.text().strip()))

    def get_values(self):
        use_template = self._grp_tpl.isChecked()
        draw_mode = self.radio_draw.isChecked()
        page_w_mm, page_h_mm = self.page_size_w.get_size_mm()
        return {
            'mode':           'draw' if draw_mode else 'fixed',
            'layout_name':    self.edit_name.text().strip(),
            'xmin':           self.spin_xmin.value(),
            'xmax':           self.spin_xmax.value(),
            'ymin':           self.spin_ymin.value(),
            'ymax':           self.spin_ymax.value(),
            'scale':          self.spin_scale.value(),
            'page_width_mm':  page_w_mm,
            'page_height_mm': page_h_mm,
            'anchor':         self.combo_anchor.currentData(),
            'use_template':   use_template,
            'template_path':  self.edit_tpl_path.text().strip() if use_template else '',
            'mark_len':       self.spin_len.value(),
            'line_width':     self.spin_lw.value(),
            'add_border':     self._grp_border.isChecked(),
            'border_width':   self.spin_border.value(),
        }

    def closeEvent(self, event):
        """Sicherstellen, dass Map-Tool deaktiviert wird wenn Dialog geschlossen."""
        if self._map_tool is not None:
            self._restore_tool()
        super().closeEvent(event)
