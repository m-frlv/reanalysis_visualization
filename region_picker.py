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
        self.__load_prepared_regions_data()
        self.__add_region_pickers()

    def __load_prepared_regions_data(self):
        f = open('regions.json')
        self.prepared_regions_data = json.load(f)

    def __transform_crs(self, extent):
        crs_src = QgsProject.instance().crs()
        crs_dest = QgsCoordinateReferenceSystem(4326)
        return QgsCoordinateTransform(crs_src, crs_dest, QgsProject.instance()).transformBoundingBox(extent)

    def __add_region_pickers(self):
        self.region_manual = QGroupBox()
        grid = QGridLayout()

        north_label = QLabel('Север')
        south_label = QLabel('Юг')
        west_label = QLabel('Запад')
        east_label = QLabel('Восток')

        north_input = QSpinBox(self)
        south_input = QSpinBox(self)
        west_nput = QSpinBox(self)
        east_input = QSpinBox(self)

        grid.addWidget(north_label, 1, 1)
        grid.addWidget(south_label, 5, 1)
        grid.addWidget(west_label, 3, 0)
        grid.addWidget(east_label, 3, 2)

        north_input.setRange(-90, 90)
        south_input.setRange(-90, 90)
        west_nput.setRange(-180, 180)
        east_input.setRange(-180, 180)

        grid.addWidget(north_input, 2, 1)
        grid.addWidget(south_input, 6, 1)
        grid.addWidget(west_nput, 4, 0)
        grid.addWidget(east_input, 4, 2)

        self.region_manual.setLayout(grid)
        self.region_prepared = QComboBox(self)
        self.region_prepared.addItems(self.prepared_regions_data.keys())
        self.addWidget(self.region_manual)
        self.addWidget(self.region_prepared)

    def get_region(self, type):
        if type == 'Задать границы вручную':
            return {
                'north': self.region_manual.layout().itemAtPosition(2, 1).widget().value(),
                'south': self.region_manual.layout().itemAtPosition(6, 1).widget().value(),
                'west': self.region_manual.layout().itemAtPosition(4, 0).widget().value(),
                'east': self.region_manual.layout().itemAtPosition(4, 2).widget().value()
            }

        elif type == 'Подготовленные регионы':
            return self.prepared_regions_data[self.region_prepared.currentText()]
        else:
            extent = iface.mapCanvas().extent()
            extent = self.__transform_crs(extent)
            return {
                'east': extent.xMaximum(),
                'west': extent.xMinimum(),
                'north': extent.yMaximum(),
                'south': extent.yMinimum(),
            }
