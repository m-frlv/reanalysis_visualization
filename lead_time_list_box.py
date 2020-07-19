import os

from qgis.PyQt import uic
from qgis.PyQt import QtWidgets
from qgis.utils import iface
from qgis.core import QgsVectorLayer, QgsProject, QgsCoordinateReferenceSystem, QgsCoordinateTransform

import sys
from PyQt5.QtWidgets import (QWidget, QLabel, QLineEdit,
                             QTextEdit, QGridLayout, QApplication,
                             QComboBox, QGroupBox, QStackedWidget, QDateEdit,
                             QSpinBox, QDialogButtonBox, QListView, QPushButton)

from PyQt5.QtCore import QDate
from PyQt5.QtGui import QStandardItemModel, QStandardItem

import json


class LeadTimeListBox(QGroupBox):
    def __init__(self, allowedLeadTimes):
        super().__init__()
        self.allowedLeadTimes = allowedLeadTimes

        self.leadTimeList = QListView()
        self.model = QStandardItemModel(self.leadTimeList)
        self.leadTimeList.setModel(self.model)
        self.leadTimeInput = QSpinBox()

        self.leadTimeInput.setRange(
            allowedLeadTimes['min'], allowedLeadTimes['max'])
        self.leadTimeInput.setSingleStep(allowedLeadTimes['step'])
        self.leadTimeInput.valueChanged.connect(
            self._roundValueBetweenStep)
        self.addLeadTimeButton = QPushButton("+", self)
        self.addLeadTimeButton.clicked.connect(self.addLeadTime)
        self.deleteLeadTimeButton = QPushButton("-", self)
        self.deleteLeadTimeButton.clicked.connect(self.deleteLeadTime)

        grid = QGridLayout()
        grid.addWidget(self.leadTimeInput, 0, 0, 1, 2)
        grid.addWidget(self.addLeadTimeButton, 1, 0)
        grid.addWidget(self.deleteLeadTimeButton, 1, 1)
        grid.addWidget(self.leadTimeList, 2, 0, 1, 2)
        self.setLayout(grid)

    def addLeadTime(self):
        leadTime = self.leadTimeInput.value()
        item = QStandardItem(str(leadTime))
        self.model.appendRow(item)

    def deleteLeadTime(self):
        indexes = self.leadTimeList.selectionModel().selectedIndexes()
        for i in indexes:
            self.model.removeRow(i.row())

    def _roundValueBetweenStep(self, value):
        self.leadTimeInput.setValue(
            (value // self.allowedLeadTimes['step'] * self.allowedLeadTimes['step']))

    def getValues(self):
        leadTimes = []
        for index in range(self.model.rowCount()):
            item = self.model.item(index)
            leadTimes.append(int(item.text()))
        return leadTimes
