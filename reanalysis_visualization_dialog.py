# -*- coding: utf-8 -*-
import os

from qgis.PyQt import uic
from qgis.PyQt import QtWidgets
from qgis.utils import iface
from qgis.core import QgsVectorLayer, QgsProject, QgsCoordinateReferenceSystem, QgsCoordinateTransform
from .lead_time_list_box import LeadTimeListBox
from .region_picker import RegionPicker

import sys
from PyQt5.QtWidgets import (QWidget, QLabel, QLineEdit,
                             QTextEdit, QGridLayout, QApplication,
                             QComboBox, QGroupBox, QStackedWidget, QDateEdit,
                             QSpinBox, QDialogButtonBox, QListView, QPushButton, QCheckBox)

from PyQt5.QtCore import QDate
from PyQt5.QtGui import QStandardItemModel, QStandardItem

import json


class ReanalysisVisualizationDialog(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        self.__load_data_models()
        self.initUI()

    def __on_models_checked(self, text):
        self.layout().removeWidget(self.parameters)
        self.layout().removeWidget(self.time)

        self.parameters.deleteLater()
        self.parameters = QComboBox(self)
        self.parameters.addItems(self.__get_variables(text))
        self.time.deleteLater()
        self.time = QComboBox(self)
        self.time.addItems(self.__get_times(text))
        self.time.activated[str].connect(self.__on_time_checked)

        self.__on_time_checked(self.__on_time_checked)
        self.layout().addWidget(self.parameters, 3, 1)
        self.layout().addWidget(self.time, 5, 1)

    def __on_time_checked(self, text):
        self.layout().removeWidget(self.lead_time_list_box)
        self.lead_time_list_box = LeadTimeListBox(
            self.__get_lead_times(self.models.currentText()))
        self.layout().addWidget(self.lead_time_list_box, 6, 1)

    def __load_data_models(self):
        f = open('method_x_varoffs.json')
        self.__data_models = json.load(f)

    def __get_variables(self, model):
        return self.__data_models[model]['varoffs'].keys()

    def __get_times(self, model):
        return self.__data_models[model]['leadTimes'].keys()

    def __get_lead_times(self, model):
        return self.__data_models[model]['leadTimes'][self.time.currentText()]

    def __on_region_type_checked(self):
        type = self.region_type.currentText()
        if type == 'Задать границы вручную':
            self.region_picker.setCurrentIndex(0)
            self.region_picker.show()
        elif type == 'Подготовленные регионы':
            self.region_picker.setCurrentIndex(1)
            self.region_picker.region_prepared.setFixedHeight(
                self.models.frameGeometry().height())
            self.region_picker.show()
        else:
            self.region_picker.hide()

    def accept(self):
        self.done(1)

    def prepare_form_data(self):
        draw_style = self.draw_style.currentText()
        model = self.__data_models[self.models.currentText()]['id']
        parameter = self.parameters.currentText()

        params = self.region_picker.get_region(self.region_type.currentText())
        params['dateIni'] = self.day_ini.date().toString(
            'yyyy-MM-dd') + 'T' + self.time.currentText().zfill(2) + ':00'
        params['leadTimes'] = self.lead_time_list_box.get_values()
        params['methodId'] = model

        variables = [self.__data_models[self.models.currentText()]
                     ['varoffs'][parameter]]

        slideshow = self.slideshow.checkState()

        return params, variables, draw_style, slideshow

    def initUI(self):
        self.draw_style = QComboBox(self)
        self.draw_style_label = QLabel('Cтиль отрисовки')
        self.draw_style.addItems(
            ['Изолинии', 'Контур с подписями'])

        self.models_label = QLabel('Модель')
        self.models = QComboBox(self)
        self.models.addItems(self.__data_models.keys())
        self.models.activated[str].connect(self.__on_models_checked)

        self.parameters_label = QLabel('Параметр')
        self.parameters = QComboBox(self)
        self.parameters.addItems(
            self.__get_variables(self.models.currentText()))

        self.day_ini = QDateEdit(self)
        self.day_ini.setCalendarPopup(True)
        self.day_ini.setDate(QDate.currentDate().addDays(-1))
        self.day_ini_label = QLabel('Дата')

        self.time = QComboBox(self)
        self.time_label = QLabel('Время')
        self.time.addItems(self.__get_times(self.models.currentText()))
        self.time.activated[str].connect(self.__on_time_checked)

        self.region_type_label = QLabel('Регион')
        self.region_type = QComboBox(self)
        self.region_type.addItems(
            ['Видимая область', 'Задать границы вручную', 'Подготовленные регионы'])
        self.region_type.activated[str].connect(self.__on_region_type_checked)

        self.region_picker = RegionPicker()

        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok
                                           | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        self.lead_time_label = QLabel('Заблаговременность')
        self.lead_time_list_box = LeadTimeListBox(
            self.__get_lead_times(self.models.currentText()))

        self.slideshow = QCheckBox('Показать слайд-шоу', self)

        grid = QGridLayout()
        grid.setSpacing(10)

        grid.addWidget(self.draw_style_label, 1, 0)
        grid.addWidget(self.draw_style, 1, 1)

        grid.addWidget(self.models_label, 2, 0)
        grid.addWidget(self.models, 2, 1)

        grid.addWidget(self.parameters_label, 3, 0)
        grid.addWidget(self.parameters, 3, 1)

        grid.addWidget(self.day_ini_label, 4, 0)
        grid.addWidget(self.day_ini, 4, 1)

        grid.addWidget(self.time_label, 5, 0)
        grid.addWidget(self.time, 5, 1)

        grid.addWidget(self.lead_time_label, 6, 0)
        grid.addWidget(self.lead_time_list_box, 6, 1)

        grid.addWidget(self.region_type_label, 7, 0)
        grid.addWidget(self.region_type, 7, 1)
        grid.addWidget(self.region_picker, 8, 0, 1, 2)
        self.region_picker.hide()

        grid.addWidget(self.slideshow, 9, 0, 1, 2)
        grid.addWidget(self.button_box, 10, 0, 1, 2)

        self.setLayout(grid)

        self.setGeometry(300, 300, 350, 300)
        self.setWindowTitle('Visualization')
        self.show()
