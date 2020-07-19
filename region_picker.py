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


class RegionPicker(QStackedWidget):
    def __init__(self):
        super().__init__()
        self._loadPreparedRegionsData()
        self._addRegionPickers()

    def _loadPreparedRegionsData(self):
        f = open('regions.json')
        self.preparedRegionsData = json.load(f)

    def _transformCrs(self, extent):
        crsSrc = QgsProject.instance().crs()
        crsDest = QgsCoordinateReferenceSystem(4326)
        return QgsCoordinateTransform(crsSrc, crsDest, QgsProject.instance()).transformBoundingBox(extent)

    def _addRegionPickers(self):
        self.regionManual = QGroupBox()
        grid = QGridLayout()

        northLabel = QLabel('Север')
        southLabel = QLabel('Юг')
        westLabel = QLabel('Запад')
        eastLabel = QLabel('Восток')

        northInput = QSpinBox(self)
        southInput = QSpinBox(self)
        westInput = QSpinBox(self)
        eastInput = QSpinBox(self)

        grid.addWidget(northLabel, 1, 1)
        grid.addWidget(southLabel, 5, 1)
        grid.addWidget(westLabel, 3, 0)
        grid.addWidget(eastLabel, 3, 2)

        northInput.setRange(-90, 90)
        southInput.setRange(-90, 90)
        westInput.setRange(-180, 180)
        eastInput.setRange(-180, 180)

        grid.addWidget(northInput, 2, 1)
        grid.addWidget(southInput, 6, 1)
        grid.addWidget(westInput, 4, 0)
        grid.addWidget(eastInput, 4, 2)

        self.regionManual.setLayout(grid)
        self.regionPrepared = QComboBox(self)
        self.regionPrepared.addItems(self.preparedRegionsData.keys())
        self.addWidget(self.regionManual)
        self.addWidget(self.regionPrepared)

    def getRegion(self, type):
        if type == 'Задать границы вручную':
            return {
                'north': self.regionManual.layout().itemAtPosition(2, 1).widget().value(),
                'south': self.regionManual.layout().itemAtPosition(6, 1).widget().value(),
                'west': self.regionManual.layout().itemAtPosition(4, 0).widget().value(),
                'east': self.regionManual.layout().itemAtPosition(4, 2).widget().value()
            }

        elif type == 'Подготовленные регионы':
            return self.preparedRegionsData[self.regionPrepared.currentText()]
        else:
            extent = iface.mapCanvas().extent()
            extent = self._transformCrs(extent)
            return {
                'east': extent.xMaximum(),
                'west': extent.xMinimum(),
                'north': extent.yMaximum(),
                'south': extent.yMinimum(),
            }
