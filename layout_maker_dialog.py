# -*- coding: utf-8 -*-
"""
layout_maker_dialog.py  –  kompatibel mit QGIS 3 (PyQt5) und QGIS 4 (PyQt6)
"""

import os
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QIcon, QPixmap
from qgis.PyQt.QtWidgets import (
    QDialog, QFrame, QHBoxLayout, QLabel,
    QPushButton, QVBoxLayout,
)
from .faltmarken_script import add_a4_raster_faltmarken
from .layout_template_script import create_layout_from_template, create_layout_from_extent


_MAIN_STYLE = """
QDialog {
    background-color: #f5f5f5;
    font-family: "Segoe UI", "Helvetica Neue", Arial, sans-serif;
    font-size: 9pt;
}
QLabel#title {
    font-size: 13pt;
    font-weight: bold;
    color: #2c5f6e;
}
QLabel#subtitle {
    font-size: 8pt;
    color: #888888;
}
QFrame#card {
    background-color: #ffffff;
    border: 1px solid #d8d8d8;
    border-radius: 8px;
}
QFrame#divider {
    color: #d8d8d8;
}
QLabel#desc {
    font-size: 8pt;
    color: #666666;
}
"""

_BTN_PRIMARY = (
    "QPushButton {"
    "  background-color: #2c5f6e; color: white; border: none;"
    "  border-radius: 6px; padding: 10px 20px;"
    "  font-size: 10pt; font-weight: bold; min-height: 36px;"
    "}"
    "QPushButton:hover  { background-color: #3d8fa0; }"
    "QPushButton:pressed{ background-color: #1f4a58; }"
)

_BTN_SECONDARY = (
    "QPushButton {"
    "  background-color: #ffffff; color: #2c5f6e;"
    "  border: 2px solid #2c5f6e; border-radius: 6px;"
    "  padding: 10px 20px; font-size: 10pt; font-weight: bold; min-height: 36px;"
    "}"
    "QPushButton:hover  { background-color: #e6f2f4; }"
    "QPushButton:pressed{ background-color: #c9e4e8; }"
)

_BTN_TERTIARY = (
    "QPushButton {"
    "  background-color: #f0f7f9; color: #2c5f6e;"
    "  border: 1px solid #a8cdd4; border-radius: 6px;"
    "  padding: 10px 20px; font-size: 10pt; font-weight: bold; min-height: 36px;"
    "}"
    "QPushButton:hover  { background-color: #d8eef2; border-color: #2c5f6e; }"
    "QPushButton:pressed{ background-color: #c9e4e8; }"
)


def _make_divider():
    line = QFrame()
    line.setObjectName('divider')
    line.setFrameShape(QFrame.Shape.HLine)
    line.setFrameShadow(QFrame.Shadow.Sunken)
    return line


class LayoutMakerDialog(QDialog):

    def __init__(self, parent=None, iface=None, icon_path=None):
        super().__init__(parent)
        self.iface = iface
        self.icon_path = icon_path
        self._extent_dlg = None   # Referenz auf offenen Extent-Dialog
        self.setWindowTitle('Layout Maker')
        self.setMinimumWidth(420)
        self.setStyleSheet(_MAIN_STYLE)
        if icon_path and os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setSpacing(14)
        root.setContentsMargins(20, 20, 20, 20)

        # ── Header ────────────────────────────────────────────────────
        header = QHBoxLayout()
        if self.icon_path and os.path.exists(self.icon_path):
            logo_lbl = QLabel()
            px = QPixmap(self.icon_path).scaled(
                48, 48,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            logo_lbl.setPixmap(px)
            logo_lbl.setFixedSize(52, 52)
            header.addWidget(logo_lbl)
        title_block = QVBoxLayout()
        title_lbl = QLabel('Layout Maker'); title_lbl.setObjectName('title')
        sub_lbl   = QLabel('QGIS Print-Layout Assistent'); sub_lbl.setObjectName('subtitle')
        title_block.addWidget(title_lbl); title_block.addWidget(sub_lbl)
        header.addLayout(title_block); header.addStretch()
        root.addLayout(header)
        root.addWidget(_make_divider())

        # ── Karte 1 ───────────────────────────────────────────────────
        card1 = QFrame(); card1.setObjectName('card')
        c1 = QVBoxLayout(card1); c1.setSpacing(6); c1.setContentsMargins(14, 12, 14, 12)
        lbl1 = QLabel('① Faltmarken hinzufügen')
        lbl1.setStyleSheet('font-weight: bold; font-size: 10pt; color: #2c5f6e;')
        desc1 = QLabel('Setzt Faltmarken im A4-Raster auf ein bestehendes Print-Layout.\nDas Layout muss bereits im Projekt vorhanden sein.')
        desc1.setObjectName('desc'); desc1.setWordWrap(True)
        btn1 = QPushButton('  Faltmarken setzen …'); btn1.setStyleSheet(_BTN_PRIMARY)
        btn1.clicked.connect(self._run_faltmarken)
        c1.addWidget(lbl1); c1.addWidget(desc1); c1.addSpacing(4); c1.addWidget(btn1)
        root.addWidget(card1)

        # ── Karte 2 ───────────────────────────────────────────────────
        card2 = QFrame(); card2.setObjectName('card')
        c2 = QVBoxLayout(card2); c2.setSpacing(6); c2.setContentsMargins(14, 12, 14, 12)
        lbl2 = QLabel('② Layout aus Vorlage erstellen')
        lbl2.setStyleSheet('font-weight: bold; font-size: 10pt; color: #2c5f6e;')
        desc2 = QLabel('Importiert eine .qpt-Vorlagendatei, positioniert den Plankopf\nund fügt automatisch Faltmarken hinzu.')
        desc2.setObjectName('desc'); desc2.setWordWrap(True)
        btn2 = QPushButton('  Layout aus Vorlage erstellen …'); btn2.setStyleSheet(_BTN_SECONDARY)
        btn2.clicked.connect(self._run_template)
        c2.addWidget(lbl2); c2.addWidget(desc2); c2.addSpacing(4); c2.addWidget(btn2)
        root.addWidget(card2)

        # ── Karte 3 ───────────────────────────────────────────────────
        card3 = QFrame(); card3.setObjectName('card')
        c3 = QVBoxLayout(card3); c3.setSpacing(6); c3.setContentsMargins(14, 12, 14, 12)
        lbl3 = QLabel('③ Plan aus Kartenausschnitt erstellen')
        lbl3.setStyleSheet('font-weight: bold; font-size: 10pt; color: #2c5f6e;')
        desc3 = QLabel(
            'Ausschnitt auf der Karte aufziehen, Massstab eingeben –\n'
            'Plangrösse wird berechnet und Plan direkt erstellt.'
        )
        desc3.setObjectName('desc'); desc3.setWordWrap(True)
        btn3 = QPushButton('  Plan aus Kartenausschnitt …'); btn3.setStyleSheet(_BTN_TERTIARY)
        btn3.clicked.connect(self._run_from_extent)
        c3.addWidget(lbl3); c3.addWidget(desc3); c3.addSpacing(4); c3.addWidget(btn3)
        root.addWidget(card3)

        root.addStretch()

    def _run_faltmarken(self):
        add_a4_raster_faltmarken(self.iface, self)

    def _run_template(self):
        create_layout_from_template(self.iface, self)

    def _run_from_extent(self):
        # Hauptdialog verstecken → Canvas frei bedienbar
        self.hide()
        self._extent_dlg = create_layout_from_extent(self.iface, self)
        # Wenn Extent-Dialog geschlossen wird → Hauptdialog wieder zeigen
        if self._extent_dlg is not None:
            self._extent_dlg.finished.connect(self._on_extent_dlg_closed)

    def _on_extent_dlg_closed(self, _result):
        self._extent_dlg = None
        self.show()
        self.raise_()
        self.activateWindow()