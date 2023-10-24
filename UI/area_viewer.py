# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'area_viewer.ui'
#
# Created by: PyQt5 UI code generator 5.15.7
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(851, 509)
        self.horizontalLayout = QtWidgets.QHBoxLayout(Form)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.frame_2 = QtWidgets.QFrame(Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame_2.sizePolicy().hasHeightForWidth())
        self.frame_2.setSizePolicy(sizePolicy)
        self.frame_2.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_2.setObjectName("frame_2")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.frame_2)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label_area_name = QtWidgets.QLabel(self.frame_2)
        font = QtGui.QFont()
        font.setPointSize(16)
        self.label_area_name.setFont(font)
        self.label_area_name.setText("")
        self.label_area_name.setObjectName("label_area_name")
        self.verticalLayout.addWidget(self.label_area_name)
        self.frame = QtWidgets.QFrame(self.frame_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame.sizePolicy().hasHeightForWidth())
        self.frame.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(8)
        self.frame.setFont(font)
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.formLayout = QtWidgets.QFormLayout(self.frame)
        self.formLayout.setObjectName("formLayout")
        self.label = QtWidgets.QLabel(self.frame)
        self.label.setObjectName("label")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label)
        self.comboBox_channel = QtWidgets.QComboBox(self.frame)
        self.comboBox_channel.setObjectName("comboBox_channel")
        self.comboBox_channel.addItem("")
        self.comboBox_channel.addItem("")
        self.comboBox_channel.addItem("")
        self.comboBox_channel.addItem("")
        self.comboBox_channel.addItem("")
        self.comboBox_channel.addItem("")
        self.comboBox_channel.addItem("")
        self.comboBox_channel.addItem("")
        self.comboBox_channel.addItem("")
        self.comboBox_channel.addItem("")
        self.comboBox_channel.addItem("")
        self.comboBox_channel.addItem("")
        self.comboBox_channel.addItem("")
        self.comboBox_channel.addItem("")
        self.comboBox_channel.addItem("")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.comboBox_channel)
        self.label_2 = QtWidgets.QLabel(self.frame)
        self.label_2.setObjectName("label_2")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_2)
        self.comboBox_sensor = QtWidgets.QComboBox(self.frame)
        self.comboBox_sensor.setObjectName("comboBox_sensor")
        self.comboBox_sensor.addItem("")
        self.comboBox_sensor.addItem("")
        self.comboBox_sensor.addItem("")
        self.comboBox_sensor.addItem("")
        self.comboBox_sensor.addItem("")
        self.comboBox_sensor.addItem("")
        self.comboBox_sensor.addItem("")
        self.comboBox_sensor.addItem("")
        self.comboBox_sensor.addItem("")
        self.comboBox_sensor.addItem("")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.comboBox_sensor)
        self.pushButton = QtWidgets.QPushButton(self.frame)
        self.pushButton.setObjectName("pushButton")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.pushButton)
        self.label_4 = QtWidgets.QLabel(self.frame)
        self.label_4.setObjectName("label_4")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.LabelRole, self.label_4)
        self.label_5 = QtWidgets.QLabel(self.frame)
        self.label_5.setObjectName("label_5")
        self.formLayout.setWidget(5, QtWidgets.QFormLayout.LabelRole, self.label_5)
        self.label_area_avg = QtWidgets.QLabel(self.frame)
        self.label_area_avg.setText("")
        self.label_area_avg.setObjectName("label_area_avg")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.FieldRole, self.label_area_avg)
        self.label_sensor_avg_dev = QtWidgets.QLabel(self.frame)
        self.label_sensor_avg_dev.setText("")
        self.label_sensor_avg_dev.setObjectName("label_sensor_avg_dev")
        self.formLayout.setWidget(5, QtWidgets.QFormLayout.FieldRole, self.label_sensor_avg_dev)
        self.verticalLayout.addWidget(self.frame)
        self.horizontalLayout.addWidget(self.frame_2)
        self.frame_3 = QtWidgets.QFrame(Form)
        self.frame_3.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_3.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_3.setObjectName("frame_3")
        self.gridLayout = QtWidgets.QGridLayout(self.frame_3)
        self.gridLayout.setObjectName("gridLayout")
        self.label_col_avg = ImageLabel(self.frame_3)
        self.label_col_avg.setObjectName("label_col_avg")
        self.gridLayout.addWidget(self.label_col_avg, 0, 0, 1, 1)
        self.label_sensor_deviation = ImageLabel(self.frame_3)
        self.label_sensor_deviation.setObjectName("label_sensor_deviation")
        self.gridLayout.addWidget(self.label_sensor_deviation, 0, 1, 1, 1)
        self.label_spectre = ImageLabel(self.frame_3)
        self.label_spectre.setObjectName("label_spectre")
        self.gridLayout.addWidget(self.label_spectre, 1, 0, 1, 1)
        self.horizontalLayout.addWidget(self.frame_3)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.label.setText(_translate("Form", "Канал"))
        self.comboBox_channel.setItemText(0, _translate("Form", "5"))
        self.comboBox_channel.setItemText(1, _translate("Form", "6"))
        self.comboBox_channel.setItemText(2, _translate("Form", "7"))
        self.comboBox_channel.setItemText(3, _translate("Form", "8"))
        self.comboBox_channel.setItemText(4, _translate("Form", "9"))
        self.comboBox_channel.setItemText(5, _translate("Form", "10"))
        self.comboBox_channel.setItemText(6, _translate("Form", "11"))
        self.comboBox_channel.setItemText(7, _translate("Form", "12"))
        self.comboBox_channel.setItemText(8, _translate("Form", "13"))
        self.comboBox_channel.setItemText(9, _translate("Form", "14"))
        self.comboBox_channel.setItemText(10, _translate("Form", "15"))
        self.comboBox_channel.setItemText(11, _translate("Form", "16"))
        self.comboBox_channel.setItemText(12, _translate("Form", "17"))
        self.comboBox_channel.setItemText(13, _translate("Form", "18"))
        self.comboBox_channel.setItemText(14, _translate("Form", "19"))
        self.label_2.setText(_translate("Form", "Датчик"))
        self.comboBox_sensor.setItemText(0, _translate("Form", "0"))
        self.comboBox_sensor.setItemText(1, _translate("Form", "1"))
        self.comboBox_sensor.setItemText(2, _translate("Form", "2"))
        self.comboBox_sensor.setItemText(3, _translate("Form", "3"))
        self.comboBox_sensor.setItemText(4, _translate("Form", "4"))
        self.comboBox_sensor.setItemText(5, _translate("Form", "5"))
        self.comboBox_sensor.setItemText(6, _translate("Form", "6"))
        self.comboBox_sensor.setItemText(7, _translate("Form", "7"))
        self.comboBox_sensor.setItemText(8, _translate("Form", "8"))
        self.comboBox_sensor.setItemText(9, _translate("Form", "9"))
        self.pushButton.setText(_translate("Form", "Создать графики"))
        self.label_4.setText(_translate("Form", "Среднее области:"))
        self.label_5.setText(_translate("Form", "Отклонение датчика:"))
        self.label_col_avg.setText(_translate("Form", "Изображение тут"))
        self.label_sensor_deviation.setText(_translate("Form", "Изображение тут"))
        self.label_spectre.setText(_translate("Form", "Изображение тут"))
from ImageLabel import ImageLabel
