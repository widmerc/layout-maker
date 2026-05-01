# -*- coding: utf-8 -*-
from .layout_maker import LayoutMakerPlugin


def classFactory(iface):
    return LayoutMakerPlugin(iface)
