# -*- coding: utf-8 -*-
# TODO: РАЗБИТЬ НА ОТДЕЛЬНЫЕ КЛАССЫ!!!
import os

from qgis.PyQt import uic
from qgis.PyQt import QtWidgets
from qgis.utils import iface
from qgis.core import QgsVectorLayer, QgsProject, QgsCoordinateReferenceSystem, QgsCoordinateTransform
from .lead_time_list_box import LeadTimeListBox

import sys
from PyQt5.QtWidgets import (QWidget, QLabel, QLineEdit,
                             QTextEdit, QGridLayout, QApplication,
                             QComboBox, QGroupBox, QStackedWidget, QDateEdit,
                             QSpinBox, QDialogButtonBox, QListView, QPushButton)

from PyQt5.QtCore import QDate
from PyQt5.QtGui import QStandardItemModel, QStandardItem

import json


class ReanalysisVisualizationDialog(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        self._loadDataModels()
        self._loadPreparedRegionsData()
        self.initUI()

    def _onModelsChecked(self, text):
        self.layout().removeWidget(self.parameters)
        self.layout().removeWidget(self.time)

        self.parameters.deleteLater()
        self.parameters = QComboBox(self)
        self.parameters.addItems(self._getVariables(text))
        self.time.deleteLater()
        self.time = QComboBox(self)
        self.time.addItems(self._getTimes(text))
        self.time.activated[str].connect(self._onTimeChecked)

        self._onTimeChecked(self._onTimeChecked)
        self.layout().addWidget(self.parameters, 3, 1)
        self.layout().addWidget(self.time, 5, 1)

    def _onTimeChecked(self, text):
        self.layout().removeWidget(self.leadTimeListBox)
        self.leadTimeListBox = LeadTimeListBox(
            self._getLeadTimes(self.models.currentText()))
        self.layout().addWidget(self.leadTimeListBox, 6, 1)
        self._getRegion()

    def _loadDataModels(self):
        f = open('method_x_varoffs.json')
        self._dataModels = json.load(f)

    def _loadPreparedRegionsData(self):
        f = open('regions.json')
        self.preparedRegionsData = json.load(f)

    def _getVariables(self, model):
        return self._dataModels[model]['varoffs'].keys()

    def _getTimes(self, model):
        return self._dataModels[model]['leadTimes'].keys()

    def _getLeadTimes(self, model):
        return self._dataModels[model]['leadTimes'][self.time.currentText()]

    def _getRegion(self):
        type = self.regionType.currentText()
        if type == 'Задать границы вручную':
            return {
                'east': self.regionManual.layout().itemAtPosition(2, 1).widget().value(),
                'west': self.regionManual.layout().itemAtPosition(6, 1).widget().value(),
                'north': self.regionManual.layout().itemAtPosition(4, 0).widget().value(),
                'south': self.regionManual.layout().itemAtPosition(4, 2).widget().value()
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

    def _onRegionTypeChecked(self):
        type = self.regionType.currentText()
        if type == 'Задать границы вручную':
            self.regionPicker.setCurrentIndex(0)
            self.regionPicker.show()
        elif type == 'Подготовленные регионы':
            self.regionPicker.setCurrentIndex(1)
            self.regionPrepared.setFixedHeight(
                self.models.frameGeometry().height())
            self.regionPicker.show()
        else:
            self.regionPicker.hide()

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

    def accept(self):
        self.done(1)

    def _transformCrs(self, extent):
        crsSrc = QgsProject.instance().crs()
        crsDest = QgsCoordinateReferenceSystem(4326)
        return QgsCoordinateTransform(crsSrc, crsDest, QgsProject.instance()).transformBoundingBox(extent)

    def prepareFormData(self):
        drawStyle = self.drawStyle.currentText()
        model = self._dataModels[self.models.currentText()]['id']
        parameter = self.parameters.currentText()

        extent = iface.mapCanvas().extent()
        extent = self._transformCrs(extent)

        params = self._getRegion()
        params['dateIni'] = self.dayIni.date().toString(
            'yyyy-MM-dd') + 'T' + self.time.currentText().zfill(2) + ':00'
        params['leadTimes'] = self.leadTimeListBox.getValues()
        params['methodId'] = model

        variables = [self._dataModels[self.models.currentText()]
                     ['varoffs'][parameter]]

        return params, variables, drawStyle

    def initUI(self):
        self.drawStyle = QComboBox(self)
        self.drawStyleLabel = QLabel('Cтиль отрисовки')
        self.drawStyle.addItems(
            ['Изолинии', 'Контур с подписями'])

        self.modelsLabel = QLabel('Модель')
        self.models = QComboBox(self)
        self.models.addItems(self._dataModels.keys())
        self.models.activated[str].connect(self._onModelsChecked)

        self.parametersLabel = QLabel('Параметр')
        self.parameters = QComboBox(self)
        self.parameters.addItems(self._getVariables(self.models.currentText()))

        self.dayIni = QDateEdit(self)
        self.dayIni.setCalendarPopup(True)
        self.dayIni.setDate(QDate.currentDate().addDays(-1))
        self.dayIniLabel = QLabel('Дата')

        self.time = QComboBox(self)
        self.timeLabel = QLabel('Время')
        self.time.addItems(self._getTimes(self.models.currentText()))
        self.time.activated[str].connect(self._onTimeChecked)

        self._addRegionPickers()
        self.regionTypeLabel = QLabel('Регион')
        self.regionType = QComboBox(self)
        self.regionType.addItems(
            ['Видимая область', 'Задать границы вручную', 'Подготовленные регионы'])
        self.regionType.activated[str].connect(self._onRegionTypeChecked)

        self.regionPicker = QStackedWidget(self)
        self.regionPicker.addWidget(self.regionManual)
        self.regionPicker.addWidget(self.regionPrepared)

        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok
                                          | QDialogButtonBox.Cancel)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.leadTimeLabel = QLabel('Заблаговременность')
        self.leadTimeListBox = LeadTimeListBox(
            self._getLeadTimes(self.models.currentText()))

        grid = QGridLayout()
        grid.setSpacing(10)

        grid.addWidget(self.drawStyleLabel, 1, 0)
        grid.addWidget(self.drawStyle, 1, 1)

        grid.addWidget(self.modelsLabel, 2, 0)
        grid.addWidget(self.models, 2, 1)

        grid.addWidget(self.parametersLabel, 3, 0)
        grid.addWidget(self.parameters, 3, 1)

        grid.addWidget(self.dayIniLabel, 4, 0)
        grid.addWidget(self.dayIni, 4, 1)

        grid.addWidget(self.timeLabel, 5, 0)
        grid.addWidget(self.time, 5, 1)

        grid.addWidget(self.leadTimeLabel, 6, 0)
        grid.addWidget(self.leadTimeListBox, 6, 1)

        grid.addWidget(self.regionTypeLabel, 7, 0)
        grid.addWidget(self.regionType, 7, 1)
        grid.addWidget(self.regionPicker, 8, 0, 1, 2)
        self.regionPicker.hide()

        grid.addWidget(self.buttonBox, 9, 0, 1, 2)

        self.setLayout(grid)

        self.setGeometry(300, 300, 350, 300)
        self.setWindowTitle('Visualization')
        self.show()
