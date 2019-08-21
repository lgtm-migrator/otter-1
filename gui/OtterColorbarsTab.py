#!/usr/bin/env python2

from PyQt5.QtCore import Qt, QModelIndex
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QTreeView, QMenu
from PyQt5.QtGui import QStandardItem, QBrush, QColor
from OtterObjectsTab import OtterObjectsTab

class OtterColorbarsTab(OtterObjectsTab):

    PARAMS_AXIS = OtterObjectsTab.PARAMS_AXIS + [
        { 'name': 'result', 'value': None, 'hint': 'The name of the viewport with a result', 'req': True },
    ]

    PARAMS = [
        { 'name': 'location', 'value': None, 'hint': 'Location of the color bar [left, right, top, bottom]', 'req': False },
        { 'name': 'origin', 'value': [0, 0], 'hint': 'The position of the color bar', 'req': False },
        { 'name': 'viewport', 'value': [0, 0, 1, 1], 'hint': 'The viewport', 'req': False },
        { 'name': 'layer', 'value': 1, 'hint': 'The layer where the color bar is drawn', 'req': False },
        { 'name': 'width', 'value': 0, 'hint': 'The width of the color bar', 'req': True },
        { 'name': 'length', 'value': 0, 'hint': 'The length of the color bar', 'req': True },
        { 'name': 'axis1', 'group': True, 'childs': PARAMS_AXIS, 'hint': 'Primary axis' },
        { 'name': 'axis2', 'group': True, 'childs': PARAMS_AXIS, 'hint': 'Secondary axis' }
    ]

    def __init__(self, parent, chigger_window):
        super(OtterColorbarsTab, self).__init__(parent, chigger_window)

    def name(self):
        return "CBs"

    def buildAddButton(self):
        btn = QPushButton("Add", self)
        btn.clicked.connect(self.onAdd)
        return btn

    def onAdd(self):
        item = self.addGroup(self.PARAMS)

    def toText(self):
        str = ""
        str += "colorbars = [\n"
        str += "]\n"

        return str
