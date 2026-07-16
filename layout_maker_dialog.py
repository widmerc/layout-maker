# -*- coding: utf-8 -*-
"""
layout_maker_dialog.py  –  kompatibel mit QGIS 3 (PyQt5) und QGIS 4 (PyQt6)
"""

import os
from qgis.PyQt.QtCore import QCoreApplication, QUrl, Qt
from qgis.PyQt.QtGui import QDesktopServices, QIcon, QPixmap
from qgis.PyQt.QtWidgets import (
    QDialog, QFrame, QHBoxLayout, QLabel,
    QPushButton, QVBoxLayout,
)
from .falzmarken_script import add_falzmarken, remove_falzmarken
from .plan_script import create_plan
from .dialogs import SettingsDialog
from .settings import set_falzmarken_raster


def tr(msg):
    # '@default': siehe Kommentar in dialogs.py.tr() — muss mit dem von
    # pylupdate5 für freie tr()-Aufrufe vergebenen Kontext übereinstimmen.
    return QCoreApplication.translate('@default', msg)


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
    "  border-radius: 6px; padding: 10px 16px;"
    "  font-size: 10pt; font-weight: bold; min-height: 36px;"
    "}"
    "QPushButton:hover  { background-color: #3d8fa0; }"
    "QPushButton:pressed{ background-color: #1f4a58; }"
)

_BTN_SECONDARY = (
    "QPushButton {"
    "  background-color: #ffffff; color: #2c5f6e;"
    "  border: 2px solid #2c5f6e; border-radius: 6px;"
    "  padding: 10px 16px; font-size: 10pt; font-weight: bold; min-height: 36px;"
    "}"
    "QPushButton:hover  { background-color: #e6f2f4; }"
    "QPushButton:pressed{ background-color: #c9e4e8; }"
)

_BTN_DESTRUCTIVE = (
    "QPushButton {"
    "  background-color: #ffffff; color: #a03030;"
    "  border: 2px solid #a03030; border-radius: 6px;"
    "  padding: 10px 16px; font-size: 10pt; font-weight: bold; min-height: 36px;"
    "}"
    "QPushButton:hover  { background-color: #fbeaea; }"
    "QPushButton:pressed{ background-color: #f2d0d0; }"
)

_BTN_ICON = (
    "QPushButton {"
    "  background-color: transparent; color: #2c5f6e;"
    "  border: 1px solid #a8cdd4; border-radius: 14px;"
    "  font-size: 10pt; font-weight: bold; min-width: 28px; max-width: 28px;"
    "  min-height: 28px; max-height: 28px;"
    "}"
    "QPushButton:hover  { background-color: #e6f2f4; }"
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
        self.plugin_dir = os.path.dirname(__file__)
        self._plan_dlg = None   # Referenz auf offenen Plan-Dialog
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
        title_lbl = QLabel(tr('Layout Maker')); title_lbl.setObjectName('title')
        sub_lbl   = QLabel(tr('QGIS Print-Layout Assistent')); sub_lbl.setObjectName('subtitle')
        title_block.addWidget(title_lbl); title_block.addWidget(sub_lbl)
        header.addLayout(title_block); header.addStretch()
        btn_settings = QPushButton('⚙')
        btn_settings.setStyleSheet(_BTN_ICON)
        btn_settings.setToolTip(tr('Einstellungen öffnen'))
        btn_settings.clicked.connect(self._open_settings)
        header.addWidget(btn_settings)
        btn_help = QPushButton('?')
        btn_help.setStyleSheet(_BTN_ICON)
        btn_help.setToolTip(tr('Hilfe öffnen'))
        btn_help.clicked.connect(self._open_help)
        header.addWidget(btn_help)
        root.addLayout(header)
        root.addWidget(_make_divider())

        # ── Karte 1: Falzmarken ──────────────────────────────────────
        card1 = QFrame(); card1.setObjectName('card')
        c1 = QVBoxLayout(card1); c1.setSpacing(6); c1.setContentsMargins(14, 12, 14, 12)
        lbl1 = QLabel('① ' + tr('Falzmarken'))
        lbl1.setStyleSheet('font-weight: bold; font-size: 10pt; color: #2c5f6e;')
        desc1 = QLabel(tr(
            'Setzt oder entfernt Falzmarken auf einem bestehenden Print-Layout.\n'
            'Das Layout muss bereits im Projekt vorhanden sein.'
        ))
        desc1.setObjectName('desc'); desc1.setWordWrap(True)
        btn1_row = QHBoxLayout(); btn1_row.setSpacing(8)
        btn1a = QPushButton(tr('Falzmarken hinzufügen …')); btn1a.setStyleSheet(_BTN_PRIMARY)
        btn1a.clicked.connect(self._run_falzmarken_add)
        btn1b = QPushButton(tr('Falzmarken entfernen …')); btn1b.setStyleSheet(_BTN_DESTRUCTIVE)
        btn1b.clicked.connect(self._run_falzmarken_remove)
        btn1_row.addWidget(btn1a); btn1_row.addWidget(btn1b)
        c1.addWidget(lbl1); c1.addWidget(desc1); c1.addSpacing(4); c1.addLayout(btn1_row)
        root.addWidget(card1)

        # ── Karte 2: Plan erstellen ───────────────────────────────────
        card2 = QFrame(); card2.setObjectName('card')
        c2 = QVBoxLayout(card2); c2.setSpacing(6); c2.setContentsMargins(14, 12, 14, 12)
        lbl2 = QLabel('② ' + tr('Plan erstellen'))
        lbl2.setStyleSheet('font-weight: bold; font-size: 10pt; color: #2c5f6e;')
        desc2 = QLabel(tr(
            'Neuer Plan wahlweise per Kartenausschnitt (aufziehen) oder mit\n'
            'vordefinierter Plangrösse, inkl. optionalem Plankopf und Falzmarken.'
        ))
        desc2.setObjectName('desc'); desc2.setWordWrap(True)
        btn2 = QPushButton('  ' + tr('Plan erstellen …')); btn2.setStyleSheet(_BTN_SECONDARY)
        btn2.clicked.connect(self._run_plan)
        c2.addWidget(lbl2); c2.addWidget(desc2); c2.addSpacing(4); c2.addWidget(btn2)
        root.addWidget(card2)

        root.addStretch()

    def _run_falzmarken_add(self):
        add_falzmarken(self.iface, self)

    def _run_falzmarken_remove(self):
        remove_falzmarken(self.iface, self)

    def _run_plan(self):
        # Hauptdialog verstecken → Canvas frei bedienbar (Ausschnitt aufziehen)
        self.hide()
        self._plan_dlg = create_plan(self.iface, self)
        # Wenn Plan-Dialog geschlossen wird → Hauptdialog wieder zeigen
        if self._plan_dlg is not None:
            self._plan_dlg.finished.connect(self._on_plan_dlg_closed)

    def _on_plan_dlg_closed(self, result):
        self._plan_dlg = None
        if result == QDialog.DialogCode.Accepted:
            # Plan wurde erfolgreich erstellt -> Layout Maker komplett schliessen.
            self.close()
        else:
            self.show()
            self.raise_()
            self.activateWindow()

    def _open_settings(self):
        dlg = SettingsDialog(self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            vals = dlg.get_values()
            set_falzmarken_raster(vals['raster_w'], vals['raster_h'])

    def _open_help(self):
        help_path = os.path.join(self.plugin_dir, 'help', 'help.html')
        if os.path.exists(help_path):
            QDesktopServices.openUrl(QUrl.fromLocalFile(help_path))
