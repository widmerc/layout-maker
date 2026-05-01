# -*- coding: utf-8 -*-
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
from .faltmarken_script import draw_faltmarken, _set_page_size, _MM


def tr(msg):
    return QCoreApplication.translate('LayoutTemplateScript', msg)


def _template_bounds(items):
    max_x = max_y = 0.0
    for item in items:
        pos = item.positionWithUnits()
        sz  = item.sizeWithUnits()
        max_x = max(max_x, pos.x() + sz.width())
        max_y = max(max_y, pos.y() + sz.height())
    return max_x, max_y


def _move_items(items, page_w, page_h, tpl_w, tpl_h, anchor):
    if   anchor == 'oben links':   dx, dy = 0.0,            0.0
    elif anchor == 'oben rechts':  dx, dy = page_w - tpl_w, 0.0
    elif anchor == 'unten links':  dx, dy = 0.0,            page_h - tpl_h
    else:                          dx, dy = page_w - tpl_w, page_h - tpl_h

    for item in items:
        pos = item.positionWithUnits()
        item.attemptMove(QgsLayoutPoint(pos.x() + dx, pos.y() + dy, _MM))


def create_layout_from_template(iface, parent=None):
    from .dialogs import TemplateDialog

    dlg = TemplateDialog(parent)
    if dlg.exec() != dlg.DialogCode.Accepted:
        return

    vals          = dlg.get_values()
    template_path = vals['template_path']
    layout_name   = vals['layout_name']
    anchor        = vals['anchor']
    override_size = vals['override_size']
    page_w        = vals['page_width']
    page_h        = vals['page_height']
    mark_len      = vals['mark_len']
    line_width    = vals['line_width']
    add_border    = vals['add_border']
    border_width  = vals['border_width']

    project = QgsProject.instance()
    manager = project.layoutManager()

    if layout_name in [l.name() for l in manager.layouts()]:
        QMessageBox.warning(parent, tr('Layout Maker'),
            tr('Der Layoutname \u201e{0}\u201c existiert bereits.').format(layout_name))
        return

    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except OSError as e:
        QMessageBox.critical(parent, tr('Layout Maker'),
            tr('Vorlage konnte nicht gelesen werden:\n{0}').format(str(e)))
        return

    doc = QDomDocument()
    doc.setContent(content)

    layout = QgsPrintLayout(project)
    layout.initializeDefaults()
    layout.setName(layout_name)
    QgsExpressionContextUtils.setLayoutVariable(layout, 'Titel', layout_name)

    items, ok = layout.loadFromTemplate(doc, QgsReadWriteContext(), False)
    if not ok:
        QMessageBox.warning(parent, tr('Layout Maker'),
                            tr('Vorlage konnte nicht geladen werden.'))
        return

    if override_size and page_w and page_h:
        _set_page_size(layout, page_w, page_h)

    page   = layout.pageCollection().page(0)
    page_w = page.pageSize().width()
    page_h = page.pageSize().height()

    tpl_w, tpl_h = _template_bounds(items)
    _move_items(items, page_w, page_h, tpl_w, tpl_h, anchor)

    draw_faltmarken(
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
    QMessageBox.information(parent, tr('Layout Maker'),
        tr('Neues Layout \u201e{0}\u201c wurde erstellt.').format(layout_name))


# ─────────────────────────────────────────────────────────────────────────────
#  Plan aus Kartenausschnitt
# ─────────────────────────────────────────────────────────────────────────────

def create_layout_from_extent(iface, parent=None):
    """
    Öffnet den MapExtentDialog nicht-modal. Die eigentliche Layout-Erstellung
    wird ausgelöst wenn der Nutzer OK drückt (accepted-Signal).
    Der Dialog verwaltet den Rubber-Band-Tool selbst.
    """
    from .dialogs import MapExtentDialog

    dlg = MapExtentDialog(iface, parent)

    def _on_accepted():
        vals         = dlg.get_values()
        layout_name  = vals['layout_name']
        xmin, xmax   = vals['xmin'],  vals['xmax']
        ymin, ymax   = vals['ymin'],  vals['ymax']
        scale        = vals['scale']
        map_w_mm     = vals['map_width_mm']
        map_h_mm     = vals['map_height_mm']
        anchor       = vals['anchor']
        use_template = vals['use_template']
        tpl_path     = vals['template_path']
        mark_len     = vals['mark_len']
        line_width   = vals['line_width']
        add_border   = vals['add_border']
        border_width = vals['border_width']

        if map_w_mm <= 0 or map_h_mm <= 0:
            QMessageBox.warning(dlg, tr('Layout Maker'),
                tr('Ungültiger Ausschnitt: Breite und Höhe müssen > 0 sein.'))
            return

        project = QgsProject.instance()
        manager = project.layoutManager()

        if layout_name in [l.name() for l in manager.layouts()]:
            QMessageBox.warning(dlg, tr('Layout Maker'),
                tr('Der Layoutname \u201e{0}\u201c existiert bereits.').format(layout_name))
            return

        layout = QgsPrintLayout(project)
        layout.initializeDefaults()
        layout.setName(layout_name)
        QgsExpressionContextUtils.setLayoutVariable(layout, 'Titel', layout_name)
        QgsExpressionContextUtils.setLayoutVariable(layout, 'Massstab', str(scale))

        # 1. Plankopf aus Vorlage laden (optional)
        tpl_w = tpl_h = 0.0
        tpl_items = []
        if use_template and tpl_path:
            try:
                with open(tpl_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                doc = QDomDocument()
                doc.setContent(content)
                tpl_items, ok = layout.loadFromTemplate(doc, QgsReadWriteContext(), False)
                if ok and tpl_items:
                    tpl_w, tpl_h = _template_bounds(tpl_items)
            except Exception as e:
                QMessageBox.warning(dlg, tr('Layout Maker'),
                    tr('Vorlage konnte nicht geladen werden:\n{0}').format(str(e)))
                tpl_items = []

        # 2. Seitengrösse = Kartenfläche + Plankopf
        if anchor in ('unten rechts', 'unten links', 'oben rechts', 'oben links'):
            page_w = max(map_w_mm, tpl_w) if tpl_items else map_w_mm
            page_h = map_h_mm + tpl_h
        else:
            page_w = map_w_mm
            page_h = map_h_mm

        _set_page_size(layout, page_w, page_h)

        # 3. Plankopf positionieren
        if tpl_items:
            _move_items(tpl_items, page_w, page_h, tpl_w, tpl_h, anchor)

        # 4. Karten-Item erstellen
        map_y = tpl_h if anchor in ('oben rechts', 'oben links') else 0.0
        map_item = QgsLayoutItemMap(layout)
        map_item.setRect(QRectF(0, 0, map_w_mm, map_h_mm))
        layout.addLayoutItem(map_item)
        map_item.attemptMove(QgsLayoutPoint(0.0, map_y, _MM))
        map_item.attemptResize(QgsLayoutSize(map_w_mm, map_h_mm, _MM))
        crs = iface.mapCanvas().mapSettings().destinationCrs()
        map_item.setCrs(crs)
        map_item.setExtent(QgsRectangle(xmin, ymin, xmax, ymax))
        map_item.setScale(scale)
        map_item.setId('map_main')

        # 5. Faltmarken
        draw_faltmarken(
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
                'Plan \u201e{0}\u201c wurde erstellt.\n'
                'Kartenfläche: {1:.0f} \u00d7 {2:.0f} mm  |  Massstab 1:{3}'
            ).format(layout_name, map_w_mm, map_h_mm, scale))
        dlg.close()

    dlg.accepted.connect(_on_accepted)
    dlg.show()
    dlg.raise_()
    dlg.activateWindow()
