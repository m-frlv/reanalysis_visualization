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
    def __init__(self, allowed_lead_times):
        super().__init__()
        self.allowed_lead_times = allowed_lead_times

        self.lead_time_list = QListView()
        self.model = QStandardItemModel(self.lead_time_list)
        self.lead_time_list.setModel(self.model)
        self.lead_time_input = QSpinBox()

        self.lead_time_input.setRange(
            allowed_lead_times['min'], allowed_lead_times['max'])
        self.lead_time_input.setSingleStep(allowed_lead_times['step'])
        self.lead_time_input.valueChanged.connect(
            self.__round_value_between_step)
        self.add_lead_time_button = QPushButton("+", self)
        self.add_lead_time_button.clicked.connect(self.__add_lead_time)
        self.delete_lead_time_button = QPushButton("-", self)
        self.delete_lead_time_button.clicked.connect(self.__delete_lead_time)

        grid = QGridLayout()
        grid.addWidget(self.lead_time_input, 0, 0, 1, 2)
        grid.addWidget(self.add_lead_time_button, 1, 0)
        grid.addWidget(self.delete_lead_time_button, 1, 1)
        grid.addWidget(self.lead_time_list, 2, 0, 1, 2)
        self.setLayout(grid)

    def __add_lead_time(self):
        lead_time = self.lead_time_input.value()
        item = QStandardItem(str(lead_time))
        self.model.appendRow(item)

    def __delete_lead_time(self):
        indexes = self.lead_time_list.selectionModel().selectedIndexes()
        for i in indexes:
            self.model.removeRow(i.row())

    def __round_value_between_step(self, value):
        self.lead_time_input.setValue(
            (value // self.allowed_lead_times['step'] * self.allowed_lead_times['step']))

    def get_values(self):
        lead_times = []
        for index in range(self.model.rowCount()):
            item = self.model.item(index)
            lead_times.append(int(item.text()))
        return lead_times
