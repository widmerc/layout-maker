# -*- coding: utf-8 -*-
from qgis.PyQt.QtCore import QCoreApplication
from qgis.PyQt.QtWidgets import QDialog, QMessageBox
from qgis.PyQt.QtXml import QDomDocument
from qgis.core import (
    QgsExpressionContextUtils,
    QgsLayoutPoint,
    QgsPrintLayout,
    QgsProject,
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
    if dlg.exec() != QDialog.DialogCode.Accepted:
        return

    vals          = dlg.get_values()
    template_path = vals['template_path']
    layout_name   = vals['layout_name']
    anchor        = vals['anchor']
    page_w        = vals['page_width']
    page_h        = vals['page_height']
    origin_index  = vals['origin_index']
    mark_len      = vals['mark_len']
    line_width    = vals['line_width']
    remove_old    = vals['remove_old']
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

    # 1. Seitengroesse setzen (VOR dem Verschieben der Elemente)
    _set_page_size(layout, page_w, page_h)

    # 2. Plankopf an gewaehlte Ecke verschieben
    tpl_w, tpl_h = _template_bounds(items)
    _move_items(items, page_w, page_h, tpl_w, tpl_h, anchor)

    # 3. Faltmarken mit allen neuen Parametern
    draw_faltmarken(
        layout,
        mark_len     = mark_len,
        line_width   = line_width,
        origin_index = origin_index,
        remove_old   = remove_old,
        add_border   = add_border,
        border_width = border_width,
    )

    manager.addLayout(layout)
    iface.openLayoutDesigner(layout)
    QMessageBox.information(parent, tr('Layout Maker'),
        tr('Neues Layout \u201e{0}\u201c wurde erstellt.').format(layout_name))
