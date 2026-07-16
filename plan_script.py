# -*- coding: utf-8 -*-
"""
plan_script.py  –  Plan erstellen: Kartenausschnitt aufziehen ODER vordefinierte
Plangrösse, mit optionalem Plankopf (Kopf-/Stempelfeld) aus einer .qpt-Vorlage.

Der Plankopf ist bewusst NUR ein Seitenfragment (kein eigenes Kartenbild):
er wird an der gewählten Ecke angehängt, die Kartenfläche füllt automatisch
den verbleibenden Platz auf der Seite.
"""

from qgis.PyQt.QtCore import QCoreApplication, QRectF
from qgis.PyQt.QtWidgets import QMessageBox
from qgis.PyQt.QtXml import QDomDocument
from qgis.core import (
    QgsExpressionContextUtils,
    QgsLayoutItemMap,
    QgsLayoutPoint,
    QgsLayoutSize,
    QgsPrintLayout,
    QgsProject,
    QgsRectangle,
    QgsReadWriteContext,
)
from .falzmarken_script import draw_falzmarken, _set_page_size, _MM


def tr(msg):
    # '@default': siehe Kommentar in dialogs.py.tr() — muss mit dem von
    # pylupdate5 für freie tr()-Aufrufe vergebenen Kontext übereinstimmen.
    return QCoreApplication.translate('@default', msg)


def _template_bounds(items):
    max_x = max_y = 0.0
    for item in items:
        pos = item.positionWithUnits()
        sz  = item.sizeWithUnits()
        max_x = max(max_x, pos.x() + sz.width())
        max_y = max(max_y, pos.y() + sz.height())
    return max_x, max_y


def _move_items(items, page_w, page_h, tpl_w, tpl_h, anchor):
    """
    Spalten-Modell: 'links'/'rechts' bestimmt die Spalte (volle Seitenhöhe),
    in der der Plankopf sitzt; 'oben'/'unten' bestimmt, wie der Plankopf-Inhalt
    innerhalb dieser Spalte ausgerichtet ist (er muss die Spalte nicht ganz
    ausfüllen). Die Karte füllt immer die jeweils andere Spalte.
    """
    dx = page_w - tpl_w if 'rechts' in anchor else 0.0
    dy = page_h - tpl_h if 'unten'  in anchor else 0.0

    for item in items:
        pos = item.positionWithUnits()
        item.attemptMove(QgsLayoutPoint(pos.x() + dx, pos.y() + dy, _MM))


def _load_plankopf(layout, tpl_path, parent_for_warning):
    """Lädt nur die Items der Plankopf-Vorlage (kein eigenes Seiten-Setup)."""
    tpl_w = tpl_h = 0.0
    tpl_items = []
    try:
        with open(tpl_path, 'r', encoding='utf-8') as f:
            content = f.read()
        doc = QDomDocument()
        doc.setContent(content)
        # clearExisting=False: nur Items übernehmen, unser frisches Layout
        # (Seitengrösse etc.) bleibt unangetastet.
        tpl_items, ok = layout.loadFromTemplate(doc, QgsReadWriteContext(), False)
        if ok and tpl_items:
            tpl_w, tpl_h = _template_bounds(tpl_items)
    except OSError as e:
        QMessageBox.warning(parent_for_warning, tr('Layout Maker'),
            tr('Plankopf-Vorlage konnte nicht geladen werden:\n{0}').format(str(e)))
        tpl_items = []
    return tpl_items, tpl_w, tpl_h


def create_plan(iface, parent=None):
    """
    Öffnet den PlanDialog nicht-modal (wegen des Karten-Aufzieh-Tools).
    Gibt den Dialog zurück, damit der Aufrufer auf finished reagieren kann.
    """
    from .dialogs import PlanDialog

    dlg = PlanDialog(iface, parent)

    def _on_ok_clicked():
        vals         = dlg.get_values()
        mode         = vals['mode']
        layout_name  = vals['layout_name']
        scale        = vals['scale']
        anchor       = vals['anchor']
        use_template = vals['use_template']
        tpl_path     = vals['template_path']
        mark_len     = vals['mark_len']
        line_width   = vals['line_width']
        add_border   = vals['add_border']
        border_width = vals['border_width']

        project = QgsProject.instance()
        manager = project.layoutManager()

        if layout_name in [l.name() for l in manager.layouts()]:
            QMessageBox.warning(dlg, tr('Layout Maker'),
                tr('Der Layoutname „{0}“ existiert bereits.').format(layout_name))
            return

        layout = QgsPrintLayout(project)
        layout.initializeDefaults()
        layout.setName(layout_name)
        QgsExpressionContextUtils.setLayoutVariable(layout, 'Titel', layout_name)
        QgsExpressionContextUtils.setLayoutVariable(layout, 'Massstab', str(scale))

        # 1. Plankopf aus Vorlage laden (optional) – nur Items, keine Seitendaten.
        tpl_items, tpl_w, tpl_h = ([], 0.0, 0.0)
        if use_template and tpl_path:
            tpl_items, tpl_w, tpl_h = _load_plankopf(layout, tpl_path, dlg)

        # 2. Kartenfläche + Seitengrösse ermitteln (je nach Modus).
        if mode == 'draw':
            xmin, xmax = vals['xmin'], vals['xmax']
            ymin, ymax = vals['ymin'], vals['ymax']
            dx, dy = xmax - xmin, ymax - ymin
            if dx <= 0 or dy <= 0 or scale <= 0:
                QMessageBox.warning(dlg, tr('Layout Maker'),
                    tr('Ungültiger Ausschnitt: Breite und Höhe müssen > 0 sein.'))
                return
            map_w_mm = (dx / scale) * 1000.0
            map_h_mm = (dy / scale) * 1000.0
            # Seite wächst seitlich um die Plankopf-Spalte (Karte behält ihre
            # Grösse); beide Spalten teilen sich die gleiche Seitenhöhe.
            page_w = map_w_mm + tpl_w
            page_h = max(map_h_mm, tpl_h)
        else:  # 'fixed' – vordefinierte Plangrösse
            page_w = vals['page_width_mm']
            page_h = vals['page_height_mm']
            if page_w <= 0 or page_h <= 0 or scale <= 0:
                QMessageBox.warning(dlg, tr('Layout Maker'),
                    tr('Ungültige Plangrösse.'))
                return
            # Karte füllt die Seite abzüglich der Plankopf-Spaltenbreite.
            map_w_mm = page_w - tpl_w
            map_h_mm = page_h
            if map_w_mm <= 0:
                QMessageBox.warning(dlg, tr('Layout Maker'),
                    tr('Der Plankopf ist zu breit für die gewählte Plangrösse.'))
                return
            # Kartenausschnitt: zentriert auf den Mittelpunkt des aktuellen
            # Kartenausschnitts, in der gewählten Grösse/Massstab.
            center = iface.mapCanvas().extent().center()
            real_w = (map_w_mm / 1000.0) * scale
            real_h = (map_h_mm / 1000.0) * scale
            xmin, xmax = center.x() - real_w / 2.0, center.x() + real_w / 2.0
            ymin, ymax = center.y() - real_h / 2.0, center.y() + real_h / 2.0

        _set_page_size(layout, page_w, page_h)

        # 3. Plankopf positionieren.
        if tpl_items:
            _move_items(tpl_items, page_w, page_h, tpl_w, tpl_h, anchor)

        # 4. Karten-Item erstellen; füllt die Spalte neben dem Plankopf.
        map_x = tpl_w if tpl_items and 'links' in anchor else 0.0
        map_item = QgsLayoutItemMap(layout)
        map_item.setRect(QRectF(0, 0, map_w_mm, map_h_mm))
        layout.addLayoutItem(map_item)
        map_item.attemptMove(QgsLayoutPoint(map_x, 0.0, _MM))
        map_item.attemptResize(QgsLayoutSize(map_w_mm, map_h_mm, _MM))
        crs = iface.mapCanvas().mapSettings().destinationCrs()
        map_item.setCrs(crs)
        map_item.setExtent(QgsRectangle(xmin, ymin, xmax, ymax))
        map_item.setScale(scale)
        map_item.setId('map_main')

        # 5. Falzmarken.
        draw_falzmarken(
            layout,
            mark_len     = mark_len,
            line_width   = line_width,
            anchor       = anchor,
            remove_old   = False,
            add_border   = add_border,
            border_width = border_width,
        )

        manager.addLayout(layout)
        iface.openLayoutDesigner(layout)
        QMessageBox.information(dlg, tr('Layout Maker'),
            tr(
                'Plan „{0}“ wurde erstellt.\n'
                'Kartenfläche: {1:.0f} × {2:.0f} mm  |  Massstab 1:{3}'
            ).format(layout_name, map_w_mm, map_h_mm, scale))
        # accept() statt close(): setzt den Dialog-Result auf "Accepted",
        # damit der Hauptdialog (layout_maker_dialog.py) zwischen "Plan
        # erfolgreich erstellt" und "Abbrechen" unterscheiden kann.
        dlg.accept()

    dlg._ok_btn.clicked.connect(_on_ok_clicked)
    dlg.show()
    dlg.raise_()
    dlg.activateWindow()
    return dlg   # Zurückgeben damit Hauptdialog auf finished reagieren kann
