# -*- coding: utf-8 -*-
import os
from qgis.PyQt.QtCore import QCoreApplication, QSettings, QTranslator
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction
from .layout_maker_dialog import LayoutMakerDialog


class LayoutMakerPlugin:

    def __init__(self, iface):
        self.iface = iface
        self.action = None
        self.dialog = None
        self.translator = None
        self.plugin_dir = os.path.dirname(__file__)
        self.icon_path = os.path.join(self.plugin_dir, 'icons', 'logo.png')

        locale = QSettings().value('locale/userLocale', 'en')[0:2]
        locale_path = os.path.join(
            self.plugin_dir, 'i18n', f'layout_maker_{locale}.qm'
        )
        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

    def tr(self, message):
        return QCoreApplication.translate('LayoutMaker', message)

    def initGui(self):
        self.action = QAction(
            QIcon(self.icon_path),
            self.tr('Layout Maker'),
            self.iface.mainWindow()
        )
        self.action.setObjectName('layoutMakerAction')
        self.action.setStatusTip(self.tr('Layout Maker öffnen'))
        self.action.triggered.connect(self.run)
        self.iface.addPluginToMenu('&Layout Maker', self.action)
        self.iface.addToolBarIcon(self.action)

    def unload(self):
        if self.action:
            self.iface.removePluginMenu('&Layout Maker', self.action)
            self.iface.removeToolBarIcon(self.action)
        if self.translator:
            QCoreApplication.removeTranslator(self.translator)

    def run(self):
        self.dialog = LayoutMakerDialog(
            self.iface.mainWindow(), self.iface, self.icon_path
        )
        self.dialog.exec()
