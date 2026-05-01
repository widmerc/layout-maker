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


def tr(msg):
    return QCoreApplication.translate('LayoutMakerDialogs', msg)


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


def _bbox(parent_dlg):
    """QDialogButtonBox (OK/Abbrechen), PyQt6-sicher. Gibt (bbox, ok_btn) zurück."""
    bb = QDialogButtonBox(
        QDialogButtonBox.StandardButton.Ok |
        QDialogButtonBox.StandardButton.Cancel
    )
    ok  = bb.button(QDialogButtonBox.StandardButton.Ok)
    cxl = bb.button(QDialogButtonBox.StandardButton.Cancel)
    ok.setStyleSheet(_BTN_OK);    ok.setText('OK')
    cxl.setStyleSheet(_BTN_CANCEL); cxl.setText('Abbrechen')
    bb.accepted.connect(parent_dlg.accept)
    bb.rejected.connect(parent_dlg.reject)
    return bb, ok


# ─────────────────────────────────────────────────────────────────────────────
#  PageSizeWidget – wiederverwendbare Seitenformat-Auswahl
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
    """
    Kompaktes Widget zur Seitenformat-Auswahl.
    Liefert get_size_mm() → (breite_mm, hoehe_mm).
    """

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
        self.combo_format.addItems(list(_PAGE_SIZES.keys()))
        self.combo_format.setCurrentText(def_fmt)
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

        self.combo_format.currentTextChanged.connect(self._on_format_changed)
        self.radio_portrait.toggled.connect(self._on_orientation_changed)
        self.radio_landscape.toggled.connect(self._on_orientation_changed)
        self.spin_w.valueChanged.connect(self._on_custom_changed)
        self.spin_h.valueChanged.connect(self._on_custom_changed)
        self._on_format_changed(def_fmt)

    def _is_custom(self):
        return self.combo_format.currentText() == 'Benutzerdefiniert'

    def _on_format_changed(self, fmt):
        custom = (fmt == 'Benutzerdefiniert')
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
        fmt = self.combo_format.currentText()
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


# ─────────────────────────────────────────────────────────────────────────────
#  FaltmarkenDialog
#  Hinweis: «Ursprung» entfernt – er wird immer von der Plankopf-Position
#            abgeleitet (Plankopf unten rechts → Ursprung unten rechts).
# ─────────────────────────────────────────────────────────────────────────────

class FaltmarkenDialog(QDialog):
    """
    Layout-Auswahl + optionale Seitengrössenänderung + Faltmarken-Parameter.
    Der Ursprung ergibt sich immer aus der Position des Plankopfs und wird
    nicht mehr separat abgefragt.
    """

    def __init__(self, layout_names, parent=None):
        super().__init__(parent)
        self.setWindowTitle(tr('Faltmarken hinzufügen'))
        self.setMinimumWidth(440)
        self.setStyleSheet(_STYLE)
        self._build(layout_names)

    def _build(self, names):
        root = QVBoxLayout(self)
        root.setSpacing(12); root.setContentsMargins(16, 16, 16, 16)

        hdr = QLabel(tr('Faltmarken auf Layout setzen'))
        hdr.setObjectName('header'); root.addWidget(hdr)
        root.addWidget(_divider())

        # Ziel-Layout
        grp1 = QGroupBox(tr('Ziel-Layout'))
        f1 = QFormLayout(grp1)
        f1.setLabelAlignment(Qt.AlignmentFlag.AlignRight); f1.setSpacing(8)
        self.combo = QComboBox(); self.combo.addItems(names)
        f1.addRow(tr('Layout:'), self.combo)
        root.addWidget(grp1)

        # Seitengrösse (optional, einklappbar)
        grp2 = QGroupBox(tr('Seitengrösse überschreiben'))
        grp2.setCheckable(True); grp2.setChecked(False)
        self._grp_page = grp2
        v2 = QVBoxLayout(grp2); v2.setSpacing(4)
        note = QLabel(tr('Überschreibt die aktuelle Seitengrösse des Layouts.'))
        note.setObjectName('desc'); note.setWordWrap(True)
        v2.addWidget(note)
        self.page_size_w = PageSizeWidget('A3', True)
        v2.addWidget(self.page_size_w)
        root.addWidget(grp2)

        # Faltmarken-Parameter (ohne Ursprung-ComboBox)
        grp3 = QGroupBox(tr('Faltmarken-Parameter'))
        f3 = QFormLayout(grp3)
        f3.setLabelAlignment(Qt.AlignmentFlag.AlignRight); f3.setSpacing(8)

        self.spin_len = _spinbox(6.0, 0.5, 20.0, 1)
        self.spin_len.setToolTip(tr('Länge jeder Faltmarke in mm'))
        f3.addRow(tr('Markenlänge:'), self.spin_len)

        self.spin_w = _spinbox(0.25, 0.01, 5.0, 2)
        self.spin_w.setToolTip(tr('Strichstärke in mm'))
        f3.addRow(tr('Strichstärke:'), self.spin_w)

        self.chk_remove = QCheckBox(tr('Bestehende Faltmarken (fm_*) vorher löschen'))
        self.chk_remove.setChecked(True)
        f3.addRow('', self.chk_remove)

        root.addWidget(grp3)

        # Rahmen
        grp4 = QGroupBox(tr('Rahmen'))
        grp4.setCheckable(True); grp4.setChecked(True)
        self._grp_border = grp4
        f4 = QFormLayout(grp4)
        f4.setLabelAlignment(Qt.AlignmentFlag.AlignRight); f4.setSpacing(8)
        self.spin_border = _spinbox(0.5, 0.01, 5.0, 2)
        self.spin_border.setToolTip(tr('Strichstärke des Rahmens in mm'))
        f4.addRow(tr('Strichstärke Rahmen:'), self.spin_border)
        root.addWidget(grp4)

        bb, _ = _bbox(self); root.addWidget(bb)

    def get_values(self):
        change_size = self._grp_page.isChecked()
        w, h = self.page_size_w.get_size_mm() if change_size else (None, None)
        return {
            'layout_name':  self.combo.currentText(),
            'change_size':  change_size,
            'page_width':   w,
            'page_height':  h,
            'mark_len':     self.spin_len.value(),
            'line_width':   self.spin_w.value(),
            'remove_old':   self.chk_remove.isChecked(),
            'add_border':   self._grp_border.isChecked(),
            'border_width': self.spin_border.value(),
        }


# ─────────────────────────────────────────────────────────────────────────────
#  TemplateDialog
# ─────────────────────────────────────────────────────────────────────────────

class TemplateDialog(QDialog):
    """
    Vorlagendatei · Layoutname · Seitengrösse (optional) · Plankopf-Position ·
    Faltmarken-Parameter – alles in einem Formular.
    """

    ANCHORS = ['oben links', 'oben rechts', 'unten links', 'unten rechts']

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(tr('Layout aus Vorlage erstellen'))
        self.setMinimumWidth(460)
        self.setStyleSheet(_STYLE)
        self._build()

    def _build(self):
        root = QVBoxLayout(self)
        root.setSpacing(12); root.setContentsMargins(16, 16, 16, 16)

        hdr = QLabel(tr('Neues Layout aus Vorlage (.qpt) erstellen'))
        hdr.setObjectName('header'); hdr.setWordWrap(True)
        root.addWidget(hdr); root.addWidget(_divider())

        # Vorlage
        grp1 = QGroupBox(tr('Vorlagendatei'))
        f1 = QFormLayout(grp1)
        f1.setLabelAlignment(Qt.AlignmentFlag.AlignRight); f1.setSpacing(8)
        row = QHBoxLayout()
        self.edit_path = QLineEdit()
        self.edit_path.setPlaceholderText(tr('Pfad zur .qpt-Datei …'))
        self.edit_path.setReadOnly(True)
        btn = QPushButton(tr('Durchsuchen …')); btn.setObjectName('browse')
        btn.clicked.connect(self._browse)
        row.addWidget(self.edit_path); row.addWidget(btn)
        f1.addRow(tr('Vorlage:'), row)
        root.addWidget(grp1)

        # Layout-Einstellungen
        grp2 = QGroupBox(tr('Layout-Einstellungen'))
        f2 = QFormLayout(grp2)
        f2.setLabelAlignment(Qt.AlignmentFlag.AlignRight); f2.setSpacing(8)
        self.edit_name = QLineEdit()
        self.edit_name.setPlaceholderText(tr('z. B.  Karte_Projekt_01'))
        self.edit_name.setText(tr('Neues Layout'))
        f2.addRow(tr('Layoutname:'), self.edit_name)
        self.combo_anchor = QComboBox()
        self.combo_anchor.addItems(self.ANCHORS)
        self.combo_anchor.setCurrentText('unten rechts')
        self.combo_anchor.setToolTip(tr('Position des Plankopfs auf der Seite'))
        f2.addRow(tr('Plankopf-Position:'), self.combo_anchor)
        root.addWidget(grp2)

        # Seitengrösse (einklappbar)
        grp3 = QGroupBox(tr('Seitengrösse überschreiben'))
        grp3.setCheckable(True)
        grp3.setChecked(False)
        self._grp_page = grp3
        v3 = QVBoxLayout(grp3); v3.setSpacing(4)
        note = QLabel(tr(
            'Wenn aktiv, wird das Seitenformat der Vorlage überschrieben.\n'
            'Wenn inaktiv, wird das Format der .qpt-Datei verwendet.'
        ))
        note.setObjectName('desc'); note.setWordWrap(True)
        v3.addWidget(note)
        self.page_size_w = PageSizeWidget('A3', True)
        v3.addWidget(self.page_size_w)
        root.addWidget(grp3)

        # Faltmarken
        grp4 = QGroupBox(tr('Faltmarken-Parameter'))
        f4 = QFormLayout(grp4)
        f4.setLabelAlignment(Qt.AlignmentFlag.AlignRight); f4.setSpacing(8)

        self.spin_len = _spinbox(6.0, 0.5, 20.0, 1)
        self.spin_len.setToolTip(tr('Länge jeder Faltmarke in mm'))
        f4.addRow(tr('Markenlänge:'), self.spin_len)

        self.spin_w = _spinbox(0.25, 0.05, 5.0, 2)
        self.spin_w.setToolTip(tr('Strichstärke in mm'))
        f4.addRow(tr('Strichstärke:'), self.spin_w)

        root.addWidget(grp4)

        # Rahmen
        grp5 = QGroupBox(tr('Rahmen'))
        grp5.setCheckable(True); grp5.setChecked(True)
        self._grp_border = grp5
        f5 = QFormLayout(grp5)
        f5.setLabelAlignment(Qt.AlignmentFlag.AlignRight); f5.setSpacing(8)
        self.spin_border = _spinbox(0.5, 0.01, 5.0, 2)
        self.spin_border.setToolTip(tr('Strichstärke des Rahmens in mm'))
        f5.addRow(tr('Strichstärke Rahmen:'), self.spin_border)
        root.addWidget(grp5)

        bb, self._ok_btn = _bbox(self)
        self._ok_btn.setEnabled(False)
        self.edit_path.textChanged.connect(self._validate)
        self.edit_name.textChanged.connect(self._validate)
        root.addWidget(bb)

    def _browse(self):
        path, _ = QFileDialog.getOpenFileName(
            self, tr('Vorlage auswählen'), '', 'QGIS Template (*.qpt)')
        if path:
            self.edit_path.setText(path)

    def _validate(self):
        self._ok_btn.setEnabled(
            bool(self.edit_path.text().strip()) and
            bool(self.edit_name.text().strip()))

    def get_values(self):
        override_size = self._grp_page.isChecked()
        if override_size:
            w, h = self.page_size_w.get_size_mm()
        else:
            w, h = None, None
        return {
            'template_path':  self.edit_path.text().strip(),
            'layout_name':    self.edit_name.text().strip(),
            'anchor':         self.combo_anchor.currentText(),
            'override_size':  override_size,
            'page_width':     w,
            'page_height':    h,
            'mark_len':       self.spin_len.value(),
            'line_width':     self.spin_w.value(),
            'add_border':     self._grp_border.isChecked(),
            'border_width':   self.spin_border.value(),
        }


# ─────────────────────────────────────────────────────────────────────────────
#  MapExtentDialog  –  Plan aus Kartenausschnitt erstellen
# ─────────────────────────────────────────────────────────────────────────────

class MapExtentDialog(QDialog):
    """
    Erstellt einen Plan direkt aus dem aktuellen Kartenausschnitt:
      1. Extent aus QGIS-Hauptfenster übernehmen
      2. Massstab eingeben
      3. Plangrösse wird automatisch berechnet
      4. Plankopf-Vorlage wählen (optional)
      5. Plan wird direkt erstellt inkl. Faltmarken
    """

    ANCHORS = ['oben links', 'oben rechts', 'unten links', 'unten rechts']

    def __init__(self, iface, parent=None):
        super().__init__(parent)
        self.iface = iface
        self.setWindowTitle(tr('Plan aus Kartenausschnitt erstellen'))
        self.setMinimumWidth(500)
        self.setStyleSheet(_STYLE)
        self._build()
        self._load_current_extent()

    def _build(self):
        root = QVBoxLayout(self)
        root.setSpacing(12); root.setContentsMargins(16, 16, 16, 16)

        hdr = QLabel(tr('Neuen Plan aus aktuellem Kartenausschnitt erstellen'))
        hdr.setObjectName('header'); hdr.setWordWrap(True)
        root.addWidget(hdr)
        desc = QLabel(tr(
            'Der aktuelle Ausschnitt im Hauptfenster wird verwendet, um die '
            'Plangrösse beim gewünschten Massstab automatisch zu berechnen.'
        ))
        desc.setObjectName('desc'); desc.setWordWrap(True)
        root.addWidget(desc)
        root.addWidget(_divider())

        # ── Kartenausschnitt ──────────────────────────────────────────────
        grp_ext = QGroupBox(tr('Kartenausschnitt (Map Extent)'))
        f_ext = QFormLayout(grp_ext)
        f_ext.setLabelAlignment(Qt.AlignmentFlag.AlignRight); f_ext.setSpacing(8)

        self.spin_xmin = _spinbox(0.0, -1e9, 1e9, 4, ' m')
        self.spin_xmax = _spinbox(0.0, -1e9, 1e9, 4, ' m')
        self.spin_ymin = _spinbox(0.0, -1e9, 1e9, 4, ' m')
        self.spin_ymax = _spinbox(0.0, -1e9, 1e9, 4, ' m')
        for sb in (self.spin_xmin, self.spin_xmax, self.spin_ymin, self.spin_ymax):
            sb.setMaximumWidth(180)

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
        btn_reload.setToolTip(tr('Übernimmt den jetzt sichtbaren Ausschnitt aus dem Hauptfenster'))
        btn_reload.clicked.connect(self._load_current_extent)
        f_ext.addRow('', btn_reload)

        root.addWidget(grp_ext)

        # ── Massstab & berechnete Plangrösse ─────────────────────────────
        grp_scale = QGroupBox(tr('Massstab & berechnete Plangrösse'))
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
        f_scale.addRow(tr('Plangrösse (berechnet):'), self.lbl_size_result)

        root.addWidget(grp_scale)

        # ── Layout-Einstellungen ─────────────────────────────────────────
        grp_lay = QGroupBox(tr('Layout-Einstellungen'))
        f_lay = QFormLayout(grp_lay)
        f_lay.setLabelAlignment(Qt.AlignmentFlag.AlignRight); f_lay.setSpacing(8)

        self.edit_name = QLineEdit()
        self.edit_name.setPlaceholderText(tr('z. B.  Plan_1000'))
        self.edit_name.setText(tr('Neuer Plan'))
        f_lay.addRow(tr('Layoutname:'), self.edit_name)

        self.combo_anchor = QComboBox()
        self.combo_anchor.addItems(self.ANCHORS)
        self.combo_anchor.setCurrentText('unten rechts')
        self.combo_anchor.setToolTip(tr('Position des Plankopfs auf der Seite'))
        f_lay.addRow(tr('Plankopf-Position:'), self.combo_anchor)

        root.addWidget(grp_lay)

        # ── Plankopf-Vorlage (optional) ──────────────────────────────────
        grp_tpl = QGroupBox(tr('Plankopf-Vorlage (.qpt) – optional'))
        grp_tpl.setCheckable(True); grp_tpl.setChecked(False)
        self._grp_tpl = grp_tpl
        v_tpl = QVBoxLayout(grp_tpl); v_tpl.setSpacing(4)
        note_tpl = QLabel(tr(
            'Wenn aktiv, wird ein Plankopf aus der .qpt-Vorlage eingefügt.\n'
            'Die Seite wird um die Plankopfgrösse vergrössert.'
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

        # ── Faltmarken-Parameter ─────────────────────────────────────────
        grp_fm = QGroupBox(tr('Faltmarken-Parameter'))
        f_fm = QFormLayout(grp_fm)
        f_fm.setLabelAlignment(Qt.AlignmentFlag.AlignRight); f_fm.setSpacing(8)

        self.spin_len = _spinbox(6.0, 0.5, 20.0, 1)
        self.spin_len.setToolTip(tr('Länge jeder Faltmarke in mm'))
        f_fm.addRow(tr('Markenlänge:'), self.spin_len)

        self.spin_lw = _spinbox(0.25, 0.05, 5.0, 2)
        self.spin_lw.setToolTip(tr('Strichstärke in mm'))
        f_fm.addRow(tr('Strichstärke:'), self.spin_lw)

        root.addWidget(grp_fm)

        # ── Rahmen ───────────────────────────────────────────────────────
        grp_brd = QGroupBox(tr('Rahmen'))
        grp_brd.setCheckable(True); grp_brd.setChecked(True)
        self._grp_border = grp_brd
        f_brd = QFormLayout(grp_brd)
        f_brd.setLabelAlignment(Qt.AlignmentFlag.AlignRight); f_brd.setSpacing(8)
        self.spin_border = _spinbox(0.5, 0.01, 5.0, 2)
        self.spin_border.setToolTip(tr('Strichstärke des Rahmens in mm'))
        f_brd.addRow(tr('Strichstärke Rahmen:'), self.spin_border)
        root.addWidget(grp_brd)

        # ── Buttons ──────────────────────────────────────────────────────
        bb, self._ok_btn = _bbox(self)
        root.addWidget(bb)

        # Signale für Live-Berechnung
        for sb in (self.spin_xmin, self.spin_xmax, self.spin_ymin, self.spin_ymax):
            sb.valueChanged.connect(self._update_size_label)
        self.spin_scale.valueChanged.connect(self._update_size_label)
        self.edit_name.textChanged.connect(self._validate)
        self._validate()
        self._update_size_label()

    def _load_current_extent(self):
        """Übernimmt den aktuellen Kartenausschnitt aus dem QGIS-Hauptfenster."""
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
        """Berechnet Plangrösse in mm aus Extent + Massstab und zeigt sie an."""
        dx = self.spin_xmax.value() - self.spin_xmin.value()
        dy = self.spin_ymax.value() - self.spin_ymin.value()
        scale = self.spin_scale.value()
        if dx <= 0 or dy <= 0 or scale <= 0:
            self.lbl_size_result.setText(tr('– (ungültiger Ausschnitt oder Massstab)'))
            return
        # Karteneinheiten → mm: teile durch Massstab, mal 1000 (m→mm)
        w_mm = (dx / scale) * 1000.0
        h_mm = (dy / scale) * 1000.0
        self.lbl_size_result.setText(f'{w_mm:.1f} × {h_mm:.1f} mm')

    def _browse_template(self):
        path, _ = QFileDialog.getOpenFileName(
            self, tr('Plankopf-Vorlage auswählen'), '', 'QGIS Template (*.qpt)')
        if path:
            self.edit_tpl_path.setText(path)

    def _validate(self):
        self._ok_btn.setEnabled(bool(self.edit_name.text().strip()))

    def get_computed_size_mm(self):
        """Gibt (breite_mm, hoehe_mm) der Kartenfläche zurück."""
        dx = self.spin_xmax.value() - self.spin_xmin.value()
        dy = self.spin_ymax.value() - self.spin_ymin.value()
        scale = self.spin_scale.value()
        w_mm = (dx / scale) * 1000.0
        h_mm = (dy / scale) * 1000.0
        return w_mm, h_mm

    def get_values(self):
        w_mm, h_mm = self.get_computed_size_mm()
        use_template = self._grp_tpl.isChecked()
        return {
            'layout_name':    self.edit_name.text().strip(),
            'xmin':           self.spin_xmin.value(),
            'xmax':           self.spin_xmax.value(),
            'ymin':           self.spin_ymin.value(),
            'ymax':           self.spin_ymax.value(),
            'scale':          self.spin_scale.value(),
            'map_width_mm':   w_mm,
            'map_height_mm':  h_mm,
            'anchor':         self.combo_anchor.currentText(),
            'use_template':   use_template,
            'template_path':  self.edit_tpl_path.text().strip() if use_template else '',
            'mark_len':       self.spin_len.value(),
            'line_width':     self.spin_lw.value(),
            'add_border':     self._grp_border.isChecked(),
            'border_width':   self.spin_border.value(),
        }
