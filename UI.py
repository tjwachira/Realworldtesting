## UI/UX file
#UI.py

from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtWidgets import QScrollArea
from os.path import expanduser
import time, pathlib, config, paramiko
import testFunctions, att6000, apConn, testWorker, install_iperf, turntable

import os

from testFunctions import PortManager

attenuateChecked = False
global results 
results = {}
interval = 1
att = []
isLocked = 0


class Ui_MainWindow(object):
    def setupUi(self, MainWindow: QtWidgets.QMainWindow):
        self.test_started = 0
        self.config = config.config()
        self.config.read_ini('config.ini')

        MainWindow.setObjectName("MainWindow")
        MainWindow.setFixedSize(1200, 700)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.start_test = QtWidgets.QPushButton(self.centralwidget)
        self.start_test.setGeometry(QtCore.QRect(MainWindow.size().width() - 120, MainWindow.size().height() - 80, 95, 31))
        self.start_test.setObjectName("start_test")
        self.start_test.clicked.connect(self.test)

        self.host_ip_label = QtWidgets.QLabel(self.centralwidget)
        self.host_ip_label.setGeometry(QtCore.QRect(30, 30, 95, 20))
        self.host_ip_label.setObjectName("host_ip_label")

        self.host_ip_input = QtWidgets.QLineEdit(self.centralwidget)
        self.host_ip_input.setGeometry(QtCore.QRect(130, 30, 110, 20))
        self.host_ip_input.setObjectName("host_ip_input")
        self.host_ip_input.setText(self.config.getHostIP())

        self.table_ip_label = QtWidgets.QLabel(self.centralwidget)
        self.table_ip_label.setGeometry(QtCore.QRect(30, 70, 95, 20))
        self.table_ip_label.setObjectName("table_ip_label")

        self.table_ip_input = QtWidgets.QLineEdit(self.centralwidget)
        self.table_ip_input.setGeometry(QtCore.QRect(130, 70, 110, 20))
        self.table_ip_input.setObjectName("table_ip_input")
        self.table_ip_input.setText(self.config.getTurnTBIP())

        self.att_nb_label = QtWidgets.QLabel(self.centralwidget)
        self.att_nb_label.setGeometry(QtCore.QRect(260, 70, 95, 20))
        self.att_nb_label.setObjectName("att_nb_label")

        self.att_nb_input = QtWidgets.QLineEdit(self.centralwidget)
        self.att_nb_input.setGeometry(QtCore.QRect(370, 70, 160, 20))
        self.att_nb_input.setObjectName("att_nb_input")
        self.att_nb_input.setText(self.config.getNbAtts())

        self.stb_ip_label = QtWidgets.QLabel(self.centralwidget)
        self.stb_ip_label.setGeometry(QtCore.QRect(575, 30, 95, 20))
        self.stb_ip_label.setObjectName("box_ip_label")

        # Checkbox for multiple STB
        self.multiple_stb_check = QtWidgets.QCheckBox(self.centralwidget)
        self.multiple_stb_check.setObjectName("multiple_stb_check")
        self.multiple_stb_check.move(800, 30)
        self.multiple_stb_check.clicked.connect(self.enter_multiple_stb)

        self.box_ip_input = QtWidgets.QLineEdit(self.centralwidget)
        self.box_ip_input.setGeometry(QtCore.QRect(680, 30, 110, 20))
        self.box_ip_input.setObjectName("box_ip_input")
        self.box_ip_input.setText(self.config.getSTBIP())

        self.router_user_label = QtWidgets.QLabel(self.centralwidget)
        self.router_user_label.setGeometry(QtCore.QRect(955, 30, 95, 20))
        self.router_user_label.setObjectName("router_user_label")

        self.router_user_input = QtWidgets.QLineEdit(self.centralwidget)
        self.router_user_input.setGeometry(QtCore.QRect(1060, 30, 110, 20))
        self.router_user_input.setObjectName("router_user_input")
        self.router_user_input.setText(self.config.getAPUsername())

        self.AP_ip_label = QtWidgets.QLabel(self.centralwidget)
        self.AP_ip_label.setGeometry(QtCore.QRect(575, 70, 95, 20))
        self.AP_ip_label.setObjectName("AP_ip_label")

        self.AP_ip_input = QtWidgets.QLineEdit(self.centralwidget)
        self.AP_ip_input.setGeometry(QtCore.QRect(680, 70, 110, 20))
        self.AP_ip_input.setObjectName("AP_ip_input")
        self.AP_ip_input.setText(self.config.getAPIP())

        self.router_password_label = QtWidgets.QLabel(self.centralwidget)
        self.router_password_label.setGeometry(QtCore.QRect(955, 70, 95, 20))
        self.router_password_label.setObjectName("router_password_label")

        self.router_password_input = QtWidgets.QLineEdit(self.centralwidget)
        self.router_password_input.setEchoMode(QtWidgets.QLineEdit.Password)
        self.router_password_input.setGeometry(QtCore.QRect(1060, 70, 110, 20))
        self.router_password_input.setObjectName("router_password_input")
        self.router_password_input.setText(self.config.getAPPassword())
        
        self.bands_list = QtWidgets.QComboBox(self.centralwidget)
        self.bands_list.setGeometry(QtCore.QRect(110, 120, 180, 22))
        self.bands_list.setObjectName("bands_list")
        self.bands_list.addItem("")
        self.bands_list.addItem("")
        self.bands_list.addItem("")
        self.bands_list.addItem("")
        self.bands_list.currentTextChanged.connect(self.bw)
        self.bands_list.currentTextChanged.connect(self.channel_change)

        self.bands_label = QtWidgets.QLabel(self.centralwidget)
        self.bands_label.setGeometry(QtCore.QRect(30, 120, 95, 15))
        self.bands_label.setObjectName("bands_label")

        self.country_list = QtWidgets.QComboBox(self.centralwidget)
        self.country_list.setGeometry(QtCore.QRect(110, 160, 180, 22))
        self.country_list.setObjectName("country_list")
        self.country_list.addItem("")
        self.country_list.addItem("")
        self.country_list.currentTextChanged.connect(self.channel_change)

        self.country_label = QtWidgets.QLabel(self.centralwidget)
        self.country_label.setGeometry(QtCore.QRect(30, 160, 70, 15))
        self.country_label.setObjectName("country_label")

        self.bw_label = QtWidgets.QLabel(self.centralwidget)
        self.bw_label.setGeometry(QtCore.QRect(30, 200, 70, 15))
        self.bw_label.setObjectName("bw_label")

        self.bw_list = QtWidgets.QComboBox(self.centralwidget)
        self.bw_list.setGeometry(QtCore.QRect(110, 200, 110, 22))
        self.bw_list.setObjectName("bw_list")
        self.bw_list.activated.connect(self.channel_change)

        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(30, 535, 200, 40))
        self.label.setText("")
        self.label.setPixmap(QtGui.QPixmap("caldero_logo.png"))
        self.label.setScaledContents(True)
        self.label.setObjectName("label")

        self.label_layout = QtWidgets.QWidget(self.centralwidget)
        self.label_layout.setGeometry(QtCore.QRect(250, 200, 70, 15))
        self.label_layout.setObjectName("label_layout")

        self.new_label = QtWidgets.QGridLayout(self.label_layout)
        self.new_label.setContentsMargins(0, 0, 0, 0)
        self.new_label.setObjectName("new_label")

        self.label_layout1 = QtWidgets.QWidget(self.centralwidget)
        self.label_layout1.setGeometry(QtCore.QRect(250, 243, 70, 15))
        self.label_layout1.setObjectName("label_layout1")

        self.new_label1 = QtWidgets.QGridLayout(self.label_layout1)
        self.new_label1.setContentsMargins(0, 0, 0, 0)
        self.new_label1.setObjectName("new_label1")

        self.channels_label = QtWidgets.QLabel(self.centralwidget)
        self.channels_label.setGeometry(QtCore.QRect(510, 120, 81, 15))
        self.channels_label.setObjectName("channels_label")

        self.scrollArea = QScrollArea(self.centralwidget)
        self.scrollArea.setGeometry(550, 140, 550, 200)

        self.gridLayoutWidget = QtWidgets.QWidget(self.scrollArea)
        self.gridLayoutWidget.setContentsMargins(10, 5, 5, 5)
        self.gridLayoutWidget.setObjectName("gridLayoutWidget")

        self.scrollArea.setWidget(self.gridLayoutWidget)


        self.channel_group = QtWidgets.QGridLayout(self.gridLayoutWidget)
        self.channel_group.setContentsMargins(0, 0, 0, 0)
        self.channel_group.setObjectName("channel_group")
    
        self.test_duration = QtWidgets.QSpinBox(self.centralwidget)
        self.test_duration.setGeometry(QtCore.QRect(110, 240, 110, 22))
        self.test_duration.setObjectName("test_duration")
        self.test_duration.setValue(int(self.config.getTestDuration()))

        self.test_duration_label = QtWidgets.QLabel(self.centralwidget)
        self.test_duration_label.setGeometry(QtCore.QRect(30, 240, 70, 15))
        self.test_duration_label.setObjectName("test_duration_label")

        self.full_path = QtWidgets.QLineEdit(self.centralwidget)
        self.full_path.setGeometry(QtCore.QRect(130, 410, 261, 20))
        self.full_path.setObjectName("full_path")
        self.full_path.setText(str(pathlib.Path().parent.absolute()))

        self.set_directory = QtWidgets.QPushButton(self.centralwidget)
        self.set_directory.setGeometry(QtCore.QRect(400, 405, 110, 26))
        self.set_directory.setObjectName("set_directory")
        self.set_directory.clicked.connect(self.choose_directory)

        self.results_path_label = QtWidgets.QLabel(self.centralwidget)
        self.results_path_label.setGeometry(QtCore.QRect(30, 410, 110, 15))
        self.results_path_label.setObjectName("results_path_label")

        self.results_name_input = QtWidgets.QLineEdit(self.centralwidget)
        self.results_name_input.setGeometry(QtCore.QRect(150, 440, 300, 20))
        self.results_name_input.setObjectName("results_name_input")
        self.results_name_input.setText(self.config.getResultsFile())

        self.results_file_label = QtWidgets.QLabel(self.centralwidget)
        self.results_file_label.setGeometry(QtCore.QRect(30, 440, 95, 15))
        self.results_file_label.setObjectName("results_file_label")

        self.toggle_table = QtWidgets.QPushButton(self.centralwidget)
        self.toggle_table.setGeometry(QtCore.QRect(30, 490, 130, 22))
        self.toggle_table.clicked.connect(self.toggle_turntable)
        self.toggle_table.setObjectName("toggle_table")

        self.check_table = QtWidgets.QPushButton(self.centralwidget)
        self.check_table.setGeometry(QtCore.QRect(30, 520, 130, 22))
        self.check_table.clicked.connect(self.check_turntable)
        self.check_table.setObjectName("check_table")

        self.table_status = QtWidgets.QLabel(self.centralwidget)
        self.table_status.setGeometry(QtCore.QRect(180, 520, 200, 22))
        self.table_status.setObjectName("table_status")
        self.table_status.setText("")

        self.tx_power = QtWidgets.QSlider(self.centralwidget)
        self.tx_power.setGeometry(QtCore.QRect(110, 280, 110, 22))
        self.tx_power.setOrientation(QtCore.Qt.Horizontal)
        self.tx_power.setObjectName("tx_power")
        self.tx_power.setMaximum(127)
        self.tx_power.setMinimum(0)
        self.tx_power.setValue(self.config.getTXPower())
        self.tx_power.valueChanged.connect(self.power_display)

        self.tx_power_label = QtWidgets.QLabel(self.centralwidget)
        self.tx_power_label.setGeometry(QtCore.QRect(30, 280, 70, 15))
        self.tx_power_label.setObjectName("tx_power_label")

        self.tx_power_value = QtWidgets.QLabel(self.centralwidget)
        self.tx_power_value.setGeometry(QtCore.QRect(230, 280, 70, 15))
        self.tx_power_value.setObjectName("tx_power_value")
        self.tx_power_value.setText(str(self.tx_power.value() / 4) + " dBm")

        self.attenuate = QtWidgets.QCheckBox(self.centralwidget)
        self.attenuate.setObjectName("attenuate")
        self.attenuate.move(30, 320)
        self.attenuate.toggled.connect(self.power_display)

        self.att_label = QtWidgets.QLabel(self.centralwidget)
        self.att_label.setGeometry(QtCore.QRect(50, 318, 70, 22))
        self.att_label.setObjectName("att_label")
        self.att_label.setText("Attenuate?")

        self.att_start = QtWidgets.QLineEdit(self.centralwidget)
        self.att_start.setGeometry(QtCore.QRect(135, 320, 70, 22))
        self.att_start.setObjectName("att_start")
        self.att_start.setText('0')

        self.comma = QtWidgets.QLabel(self.centralwidget)
        self.comma.setGeometry(QtCore.QRect(210, 322, 3, 22))
        self.comma.setObjectName("comma")
        self.comma.setText(',')

        self.att_stop = QtWidgets.QLineEdit(self.centralwidget)
        self.att_stop.setGeometry(QtCore.QRect(225, 320, 70, 22))
        self.att_stop.setObjectName("att_stop")
        self.att_stop.setText('0')
        
        self.colon = QtWidgets.QLabel(self.centralwidget)
        self.colon.setGeometry(QtCore.QRect(300, 322, 3, 22))
        self.colon.setObjectName("comma")
        self.colon.setText(':')

        self.att_int = QtWidgets.QLineEdit(self.centralwidget)
        self.att_int.setGeometry(QtCore.QRect(310, 320, 70, 22))
        self.att_int.setObjectName("att_interval")
        self.att_int.setText('0')
        
        self.angle_interval_label = QtWidgets.QLabel(self.centralwidget)
        self.angle_interval_label.setGeometry(QtCore.QRect(30, 360, 95, 15))
        self.angle_interval_label.setObjectName("angle_interval_label")

        self.angle_interval = QtWidgets.QLineEdit(self.centralwidget)
        self.angle_interval.setGeometry(QtCore.QRect(130, 360, 70, 22))
        self.angle_interval.setObjectName("angle_interval")
        self.angle_interval.setText(str(self.config.getAngleInterval()))

        self.angle_override = QtWidgets.QCheckBox(self.centralwidget)
        self.angle_override.setObjectName("angle_override")
        self.angle_override.move(210, 362)

        self.override = QtWidgets.QLabel(self.centralwidget)
        self.override.setGeometry(QtCore.QRect(230, 360, 70, 22))
        self.override.setObjectName("override")
        self.override.setText("Override?")
        
        self.combo_layout = QtWidgets.QWidget(self.centralwidget)
        self.combo_layout.setGeometry(QtCore.QRect(330, 200, 110, 22))
        self.combo_layout.setObjectName("combo_layout")

        self.new_combo = QtWidgets.QGridLayout(self.combo_layout)
        self.new_combo.setContentsMargins(0, 0, 0, 0)
        self.new_combo.setObjectName("new_combo")

        self.combo_layout1 = QtWidgets.QWidget(self.centralwidget)
        self.combo_layout1.setGeometry(QtCore.QRect(330, 240, 110, 22))
        self.combo_layout1.setObjectName("combo_layout1")

        self.new_combo1 = QtWidgets.QGridLayout(self.combo_layout1)
        self.new_combo1.setContentsMargins(0, 0, 0, 0)
        self.new_combo1.setObjectName("new_combo1")

        self.test_progress = QtWidgets.QProgressBar(self.centralwidget)
        self.test_progress.setGeometry(QtCore.QRect(120, MainWindow.size().height() - 80, 651, 31))
        self.test_progress.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.test_progress.setAlignment(QtCore.Qt.AlignBottom | QtCore.Qt.AlignHCenter)
        self.test_progress.setProperty("value", 0)
        self.test_progress.setMaximum(100)
        self.test_progress.hide()
        self.test_progress.setObjectName("test_progress")

        self.build = QtWidgets.QCheckBox(self.centralwidget)
        self.build.move(1000, 405)
        self.build.setObjectName("build")
        self.build.toggled.connect(self.change_build)
        self.build.click()

        self.build_label = QtWidgets.QLabel(self.centralwidget)
        self.build_label.setGeometry(QtCore.QRect(1020, 400, 100, 22))
        self.build_label.setObjectName("build_label")

        self.version_label = QtWidgets.QLabel(self.centralwidget)
        self.version_label.setGeometry(QtCore.QRect(1000, 440, 100, 22))
        self.version_label.setObjectName("version_label")

        self.version = QtWidgets.QComboBox(self.centralwidget)
        self.version.setGeometry(QtCore.QRect(1040, 440, 100, 22))
        self.version.setObjectName("version")
        self.version.addItems(["Choose iPerf Version", "2", "3"])

        self.install = QtWidgets.QPushButton(self.centralwidget)
        self.install.setGeometry(QtCore.QRect(1000, 480, 100, 22))
        self.install.setObjectName("install_iperf")
        self.install.clicked.connect(self.installIperf)

        self.quitiperf = QtWidgets.QPushButton(self.centralwidget)
        self.quitiperf.setGeometry(QtCore.QRect(1000, 520, 100, 22))
        self.quitiperf.setObjectName("quit_iperf")
        self.quitiperf.clicked.connect(testFunctions.killIperf)

        self.Adv_settings_group = QtWidgets.QGroupBox(self.centralwidget)
        #self.Adv_settings_group.setGeometry(QtCore.QRect(600, 400, 381, 201))
        self.Adv_settings_group.setGeometry(QtCore.QRect(600, 400, 381, 201))
        self.Adv_settings_group.setAutoFillBackground(False)
        self.Adv_settings_group.setObjectName("Adv_settings_group")

        self.eth_1_label = QtWidgets.QLabel(self.Adv_settings_group)
        self.eth_1_label.setGeometry(QtCore.QRect(250, 30, 110, 20))
        self.eth_1_label.setObjectName("eth_1_label")

        self.eth_1 = QtWidgets.QSpinBox(self.Adv_settings_group)
        self.eth_1.setGeometry(QtCore.QRect(320, 30, 42, 22))
        self.eth_1.setObjectName("eth_1")
        self.eth_1.setValue(self.config.get24Port())

        self.eth_2_label = QtWidgets.QLabel(self.Adv_settings_group)
        self.eth_2_label.setGeometry(QtCore.QRect(130, 30, 110, 20))
        self.eth_2_label.setObjectName("eth_2_label")

        self.eth_2 = QtWidgets.QSpinBox(self.Adv_settings_group)
        self.eth_2.setGeometry(QtCore.QRect(200, 30, 42, 22))
        self.eth_2.setObjectName("eth_2")
        self.eth_2.setValue(self.config.get5Port())

    # wifi 6E
        self.eth_3_label = QtWidgets.QLabel(self.Adv_settings_group)
        self.eth_3_label.setGeometry(QtCore.QRect(10, 30, 110, 20))
        self.eth_3_label.setObjectName("eth_3_label")

        self.eth_3 = QtWidgets.QSpinBox(self.Adv_settings_group)
        self.eth_3.setGeometry(QtCore.QRect(80, 30, 42, 22))
        self.eth_3.setObjectName("eth_3")
        self.eth_3.setValue(self.config.get6Port())    

        self.gridLayoutWidget_2 = QtWidgets.QWidget(self.Adv_settings_group)
        self.gridLayoutWidget_2.setGeometry(QtCore.QRect(20, 90, 351, 80))
        self.gridLayoutWidget_2.setObjectName("gridLayoutWidget_2")

        self.test_options = QtWidgets.QGridLayout(self.gridLayoutWidget_2)
        self.test_options.setContentsMargins(0, 0, 0, 0)
        self.test_options.setObjectName("test_options")

        self.Rx = QtWidgets.QCheckBox(self.gridLayoutWidget_2)
        self.Rx.setObjectName("Rx")
        self.Rx.click()
        self.test_options.addWidget(self.Rx, 0, 0, 1, 1)

        self.Tx = QtWidgets.QCheckBox(self.gridLayoutWidget_2)
        self.Tx.setObjectName("Tx")
        self.Tx.click()
        self.test_options.addWidget(self.Tx, 1, 0, 1, 1)

        self.RSSI = QtWidgets.QCheckBox(self.gridLayoutWidget_2)
        self.RSSI.setObjectName("RSSI")
        self.RSSI.click()
        self.test_options.addWidget(self.RSSI, 0, 1, 1, 1)

        self.MCS = QtWidgets.QCheckBox(self.gridLayoutWidget_2)
        self.MCS.setObjectName("MCS")
        self.test_options.addWidget(self.MCS, 1, 1, 1, 1)

        self.RDK = QtWidgets.QCheckBox(self.gridLayoutWidget_2)
        self.RDK.setObjectName("RDK")
        #self.RDK.click()
        self.test_options.addWidget(self.RDK, 0, 2, 1, 1)

        self.PSC = QtWidgets.QCheckBox(self.gridLayoutWidget_2)
        self.PSC.setObjectName("PSC")
        self.test_options.addWidget(self.PSC, 1, 2, 1, 1)
        self.PSC.clicked.connect(self.channel_change)

        #checkbox for new test option - draft
        self.new_option = QtWidgets.QCheckBox(self.gridLayoutWidget_2)
        self.new_option.setObjectName("new_option")
        #self.new_option.click()
        self.test_options.addWidget(self.new_option, 2, 0, 1, 1)


        self.throughput = QtWidgets.QLabel(self.Adv_settings_group)
        self.throughput.setGeometry(QtCore.QRect(20, 70, 81, 15))
        self.throughput.setObjectName("throughput")

        self.others = QtWidgets.QLabel(self.Adv_settings_group)
        self.others.setGeometry(QtCore.QRect(190, 70, 81, 15))
        self.others.setObjectName("others")

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 792, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)

        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")

        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.actionSave_Measurement = QtWidgets.QAction(MainWindow)
        self.actionSave_Measurement.setObjectName("actionSave_Measurement")
        self.actionLoad_Measurement = QtWidgets.QAction(MainWindow)
        self.actionLoad_Measurement.setObjectName("actionLoad_Measurement")
        self.menuFile.addAction(self.actionSave_Measurement)
        self.menuFile.addAction(self.actionLoad_Measurement)
        self.menubar.addAction(self.menuFile.menuAction())
        
        self.table = None

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        # MainWindow.setWindowTitle(_translate("MainWindow", "ASUS RT-AX88U"))
        MainWindow.setWindowTitle(_translate("MainWindow", "Real World Test"))
        self.start_test.setText(_translate("MainWindow", "Start Test"))
        self.host_ip_label.setText(_translate("MainWindow", "Host IP"))
        self.table_ip_label.setText(_translate("MainWindow", "Turntable IP"))
        self.stb_ip_label.setText(_translate("MainWindow", "STB IP"))
        self.multiple_stb_check.setText(_translate("MainWindow", "Multiple STB")) # Multiple STB
        self.router_user_label.setText(_translate("MainWindow", "Username"))
        self.AP_ip_label.setText(_translate("MainWindow", "AP IP"))
        self.att_nb_label.setText(_translate("MainWindow", "No.  Attenuators"))
        self.router_password_label.setText(_translate("MainWindow", "Password"))
        self.bands_list.setItemText(0, _translate("MainWindow", "2.4 GHz"))
        self.bands_list.setItemText(1, _translate("MainWindow", "5 GHz"))
        self.bands_list.setItemText(2, _translate("MainWindow", "6 GHz"))
        self.bands_list.setItemText(3, _translate("MainWindow", "All"))
        self.bands_label.setText(_translate("MainWindow", "Bands"))
        self.country_list.setItemText(0, _translate("MainWindow", "United States - US"))
        self.country_list.setItemText(1, _translate("MainWindow", "Europe - EU"))
        self.country_label.setText(_translate("MainWindow", "Country"))
        self.bw_label.setText(_translate("MainWindow", "Bandwidth"))
        self.test_duration_label.setText(_translate("MainWindow", "Duration"))
        self.set_directory.setText(_translate("MainWindow", "Select Folder"))
        self.results_path_label.setText(_translate("MainWindow", "Save Results in"))
        self.results_file_label.setText(_translate("MainWindow", "Results File Name"))
        self.channels_label.setText(_translate("MainWindow", "Channels:"))
        self.tx_power_label.setText(_translate("MainWindow", "Tx Power"))

        self.angle_interval_label.setText(_translate("MainWindow", "Angle Interval"))

        self.toggle_table.setText(QtCore.QCoreApplication.translate("MainWindow", "Lock Table"))
        self.check_table.setText(QtCore.QCoreApplication.translate("MainWindow", "Check Table"))
        
        self.build_label.setText(_translate("MainWindow", "Engineering Build?"))
        self.version_label.setText(_translate("MainWindow", "iPerf v"))
        self.install.setText(_translate("MainWindow", "Load iPerf"))
        self.quitiperf.setText(_translate("MainWindow", "Kill iPerf"))

        self.eth_1_label.setText(_translate("MainWindow", " 2.4 GHz Port"))
        self.eth_2_label.setText(_translate("MainWindow", " 5.0 GHz Port"))
        self.eth_3_label.setText(_translate("MainWindow", " 6.0 GHz Port"))
        # self.test_log_label.setText(_translate("MainWindow", "Test Log:"))
        self.Rx.setText(_translate("MainWindow", "Rx"))
        self.Tx.setText(_translate("MainWindow", "Tx"))
        self.RSSI.setText(_translate("MainWindow", "RSSI"))
        self.MCS.setText(_translate("MainWindow", "MCS"))
        self.RDK.setText(_translate("MainWindow", "RDK"))
        self.PSC.setText(_translate("MainWindow", "PSC"))
        self.new_option.setText(_translate("MainWindow", "θ_CH_ATT")) # new option addition - draft
        self.throughput.setText(_translate("MainWindow", "Throughput"))
        self.others.setText(_translate("MainWindow", "Other Tests:"))
        self.Adv_settings_group.setTitle(_translate("MainWindow", "Advanced Settings"))
        self.menuFile.setTitle(_translate("MainWindow", "File"))
        self.actionSave_Measurement.setText(_translate("MainWindow", "Save Measurement"))
        self.actionLoad_Measurement.setText(_translate("MainWindow", "Load Measurement"))
    
    def choose_directory(self):
        directory = QtWidgets.QFileDialog.getExistingDirectory(
            None,
            "Open a folder",
            expanduser("~"),
            QtWidgets.QFileDialog.ShowDirsOnly
        )
        self.full_path.setText(directory)

    def installIperf(self):
        IPaddr = self.box_ip_input.text()
        isEng = self.build.isChecked()
        install_iperf.install_iperf(IPaddr, isEng)
    
    def change_build(self, iperfv): 
        path_1 = "/system/bin/iperf3"  
        path_2 = "/usr/bin/iperf"
        path_3 = "/vendor/bin/iperf"
        path_4 = ""
        
        # change path to the specific directory within the different STB path to *iperf*
        
        if (self.build.isChecked()):
            testFunctions.iperfPath = path_1
        else:
            testFunctions.iperfPath = "/data/iperf"

    def bw(self):
        self.bw_list.clear()
        country_text = self.country_list.currentText()
        band_text = self.bands_list.currentText()
        eth1 = self.eth_1.value()
        eth2 = self.eth_2.value()
        eth3 = self.eth_3.value()
        country_code, band = testFunctions.countryCode(country_text, band_text, eth1, eth2, eth3)
        test1 = self.new_combo.count()
        test2 = self.new_label.count()
        #test1 = self.new_combo1.count()
        #test2 = self.new_label1.count()
        print("test1", test1,"\n")
        print("test2", test2,"\n")

        if test1 > 0:
            for ch in reversed(range(test1)):
                self.new_combo.itemAt(ch).widget().setParent(None)
                self.new_combo1.itemAt(ch).widget().setParent(None)
        if test2 > 0:
            for ch in reversed(range(test2)):
                self.new_label.itemAt(ch).widget().setParent(None)
                self.new_label1.itemAt(ch).widget().setParent(None)
        if band == 0:

            self.bw_label.setText("2.4GHz BW:")
            self.bw_label.adjustSize()
            self.bw_list.addItems(["20", "40", "All"])

            self.bw_list2 = QtWidgets.QComboBox(self.combo_layout)
            self.new_combo.addWidget(self.bw_list2)
            self.bw_list2.setGeometry(QtCore.QRect(320, 200, 110, 22))
            self.bw_list2.setObjectName("bw_list2")
            self.bw_list2.addItems(["20", "40", "80", "All"])
            self.bw_list2.activated.connect(self.channel_change)

            self.bw_label2 = QtWidgets.QLabel(self.label_layout)
            self.new_label.addWidget(self.bw_label2)
            self.bw_label2.setGeometry(QtCore.QRect(250, 200, 70, 15))
            self.bw_label2.setObjectName("bw_label2")
            self.bw_label2.setText("5GHz BW:")
            self.bw_label2.adjustSize()

            self.bw_list3 = QtWidgets.QComboBox(self.combo_layout1)
            self.new_combo1.addWidget(self.bw_list3)
            self.bw_list3.setGeometry(QtCore.QRect(320, 200, 110, 22))
            self.bw_list3.setObjectName("bw_list3")
            self.bw_list3.addItems(["20", "40", "80", "160", "All"])
            self.bw_list3.activated.connect(self.channel_change)

            self.bw_label3 = QtWidgets.QLabel(self.label_layout1)
            self.new_label1.addWidget(self.bw_label3)
            self.bw_label3.setGeometry(QtCore.QRect(250, 200, 70, 15))
            self.bw_label3.setObjectName("bw_label3")
            self.bw_label3.setText("6GHz BW:")
            self.bw_label3.adjustSize()

        elif band == eth1:
            self.bw_label.setText("Channel BW:")
            self.bw_list.addItems(["20", "40", "All"])
        elif band == eth2:
            self.bw_label.setText("Channel BW:")
            self.bw_list.addItems(["20", "40", "80", "All"])
        else:
            self.bw_label.setText("Channel BW:")
            self.bw_list.addItems(["20", "40", "80", "160", "All"])

    def channel_change(self):
        test = self.channel_group.count()
        # print("\ntest3...", test) 
        H = 80
        if test > 0:
            for ch in reversed(range(test)):
                self.channel_group.itemAt(ch).widget().setParent(None)
                self.gridLayoutWidget.setGeometry(550, 140, 500, H)
                

        _translate = QtCore.QCoreApplication.translate
        country_text = self.country_list.currentText()
        band_text = self.bands_list.currentText()
        eth1 = self.eth_1.value()
        eth2 = self.eth_2.value()
        eth3 = self.eth_3.value()
        country_code, band = testFunctions.countryCode(country_text, band_text, eth1, eth2, eth3)
        bandwidth1_text = self.bw_list.currentText()
        PSC_check = self.PSC.checkState()
        if band == 0:
            bandwidth2_text = self.bw_list2.currentText()
            bandwidth3_text = self.bw_list3.currentText()
            channels_t = testFunctions.getChannels(band, country_code, bandwidth1_text, bandwidth2_text, bandwidth3_text, eth1, eth2, eth3, PSC_check)
        else:
            channels_t = testFunctions.getChannels(band, country_code, bandwidth1_text, bandwidth1_text, bandwidth1_text, eth1, eth2, eth3, PSC_check)
            
        col = 0
        row = 0

        for ch in channels_t:
            if ch == "36" or ch == "36/80":
                col = 0
                H = H + 20
                self.gridLayoutWidget.setGeometry(550, 140, 500, H)
                row = row + 1
            self.__dict__["ch_" + ch] = QtWidgets.QCheckBox(self.gridLayoutWidget)
            self.__dict__["ch_" + ch].setObjectName("ch_" + ch)
            self.channel_group.addWidget(self.__dict__["ch_" + ch], row, col, 1, 1)
            self.__dict__["ch_" + ch].setText(_translate("MainWindow", ch))
            parsed = ch.replace("l", "")
            parsed = parsed.replace("/80", "")
            if "6g" in parsed:
                self.__dict__["ch_" + ch].setStyleSheet("color: green;")
            elif parsed.isdigit and int(parsed) <= 13:
                self.__dict__["ch_" + ch].setStyleSheet("color: red;")
            else:
                self.__dict__["ch_" + ch].setStyleSheet("color: blue;")

            if col < 7:
                col = col + 1
            else:
                col = 0
                H = H + 20
                self.gridLayoutWidget.setGeometry(550, 140, 500, H)
                row = row + 1

    # Enter IPs for multiple STBs
    def enter_multiple_stb(self):
        dlg = QtWidgets.QInputDialog(self.centralwidget)
        dlg.setInputMode(QtWidgets.QInputDialog.TextInput)
        dlg.resize(400, 200)
        dlg.setWindowTitle("STB IPs")
        dlg.setLabelText("Input IPs for multiple STBs")
        ok = dlg.exec_()
        text = dlg.textValue()
        # text, ok = QtWidgets.QInputDialog.getText(self.centralwidget, "Input IPs for multiple STBs", "")
        if ok:
            self.stb_ip_list = [ip.strip() for ip in text.split(',')]
            print(self.stb_ip_list)
            invalid_ip_indexes = ""
            for i in range(len(self.stb_ip_list)):
                if apConn.validIPAddress(self.stb_ip_list[i]) is False:
                    if not invalid_ip_indexes:
                        invalid_ip_indexes += str(i)
                    else:
                        invalid_ip_indexes += ", " +str(i)
    
            if invalid_ip_indexes != "":
                print(invalid_ip_indexes)
                self.error_dialog = QtWidgets.QMessageBox()
                self.error_dialog.setText("IP at index(s) " + invalid_ip_indexes + " invalid.")
                self.error_dialog.setWindowTitle("Invalid Box IP")
                self.error_dialog.show()
                
    def power_display(self):
        error = 0
        test = 0
        global attenuateChecked

        if self.attenuate.isChecked() and not attenuateChecked:
            attenuateChecked = True
            error = att6000.conAtt(att, int(self.att_nb_input.text()))
            self.att_start.setText(str(self.config.getAttStart()))
            self.att_stop.setText(str(self.config.getAttStop()))
            self.att_int.setText(str(self.config.getAttInterval()))

            if not error and test:
                for i in range(0, 3200, 100):
                    att6000.setAtt(att,i/100)
                    time.sleep(1)
            elif test:
                att6000.setAtt(att, 0)
                time.sleep(1)

        elif not self.attenuate.isChecked() and attenuateChecked:
            self.att_int.setText('0')
            attenuateChecked = False
            att6000.disconAtt(att)
                    
        text = str(self.tx_power.value() / 4) + " dBm"
        self.tx_power_value.setText(text)
        
        if error:
            self.attenuate.setChecked(False)
            time.sleep(0.1)
            self.attenuate.update()
            print("\n[ATT] No attenuators connected...")   

    def update_table_status(self):
        if (self.table is not None):
            if (self.table.isLocked):
                self.toggle_table.setText(QtCore.QCoreApplication.translate("MainWindow", "Unlock Table"))
            else:
                self.toggle_table.setText(QtCore.QCoreApplication.translate("MainWindow", "Lock Table"))

    def toggle_turntable(self):
        if self.table is None:
            try:
                self.table = turntable.TurnTable(self.table_ip_input.text())
            except:
                print("Turntable will not work. Check RPi connectivity and try again.\n")
        
        if self.table is not None:
            if (self.table.isLocked):
                self.table.free()
            else:
                self.table.lock()
            self.update_table_status()
            # self.table.close()

    def check_turntable(self):
        if self.table is None:
            try:
                self.table = turntable.TurnTable(self.table_ip_input.text())
            except:
                print("Turntable will not work. Check RPi connectivity and try again.\n")
        
        if self.table is not None:
            try:
                status = self.table.current()
            except AttributeError:
                try:
                    self.table = turntable.TurnTable(self.table_ip_input.text())
                except:
                    print("Turntable will not work. Check RPi connectivity and try again.\n")
                
                status = self.table.current()

            self.table_status.setText(QtCore.QCoreApplication.translate("MainWindow", str(status)))
            # self.table.close()
    
    def update_status(self, n):
        current_worker = None

        # Check if we are in the multiple STB mode.
        if self.multiple_stb_check:
            # Make sure that 'workers' attribute exists in the current object and is not an empty list.
            if hasattr(self, 'workers') and self.workers:
                current_worker = self.workers[0]
        else:
            # Make sure that 'worker' attribute exists in the current object.
            if hasattr(self, 'worker'):
                current_worker = self.worker

        # Check if a worker was determined (either from 'workers' list or 'worker' attribute).
        if current_worker:
            current_worker.running = n
            if current_worker.running % 2:
                self.start_test.setText(QtCore.QCoreApplication.translate("MainWindow", "Pause Test"))
            elif current_worker.running == 0:
                self.start_test.setText(QtCore.QCoreApplication.translate("MainWindow", "Start Test"))
            else:
                self.start_test.setText(QtCore.QCoreApplication.translate("MainWindow", "Resume Test"))
        else:
            # This part will be executed if no worker was found.
            # You could potentially log an error or show a message to the user.
            pass

    def update_progress(self, n):
        self.test_progress.setValue(n)
 
    def test(self):
        port_manager = testFunctions.PortManager()
        multiple_stb_check = False
        try:
            if (self.worker is not None):
                self.test_started = 1
        except AttributeError as error:
            self.test_started = 0
        
        if (not self.test_started):
            laptop_ip = self.host_ip_input.text()
            box_ip = self.box_ip_input.text()
            router_ip = self.AP_ip_input.text()
            table_ip = self.table_ip_input.text()
            router_user = self.router_user_input.text()
            router_password = self.router_password_input.text()
            country_text = self.country_list.currentText()
            band_text = self.bands_list.currentText()
            if (not self.angle_override.isChecked()):
                angle_interval = self.angle_interval.text()
            else:
                angle_interval = str(-int(self.angle_interval.text()))
            bw_text = self.bw_list.currentText()
            eth1_value = self.eth_1.value()
            eth2_value = self.eth_2.value()
            eth3_value = self.eth_3.value()
            log_file = ""

            country_code, band = testFunctions.countryCode(country_text, band_text, eth1_value, eth2_value, eth3_value)
            file_directory = self.full_path.text()
            results_path = self.full_path.text() + "/Results"
            file_name = self.results_name_input.text()
            t = self.test_duration.value()
            power = self.tx_power.value()

            att_start = self.att_start.text()
            att_stop = self.att_stop.text()
            att_int = self.att_int.text()
            iperf = self.version.currentText()
            print("Iperf v", str(iperf))

            test_list = []
            # max_band, bandwidth, channels_t = setBandwidth(band, country_code)
            self.checkbox_list = self.gridLayoutWidget.findChildren(QtWidgets.QCheckBox)
            multiple_stb_check = self.multiple_stb_check.checkState()
            mcs_check = self.MCS.checkState()
            RDK_check = self.RDK.checkState()
            PSC_check = self.PSC.checkState()
            option_check = self.new_option.checkState()
            rssi_check = self.RSSI.checkState()
            Tx_check = self.Tx.checkState()
            Rx_check = self.Rx.checkState()

            for ch in self.checkbox_list:
                if ch.checkState():
                    test_list.append(ch.text())
            bw2_text = ""
            bw3_text = ""
            if band == 0:
                bw2_text = self.bw_list2.currentText()
                bw3_text = self.bw_list3.currentText()

            if self.check_inputs(laptop_ip, box_ip, router_ip, table_ip, test_list, multiple_stb_check) is True:
                print("Inputs ok. Starting test...\n")
                
                if not multiple_stb_check:
                    # Create QThread object
                    self.thread = QtCore.QThread()
                    
                    # Create worker object
                    port = port_manager.get_next_port()
                    self.worker = testWorker.testWorker(laptop_ip, box_ip, router_ip, table_ip, router_user, router_password, bw_text, bw2_text, bw3_text, eth1_value, eth2_value, eth3_value,
                                        country_code, band, file_directory, file_name, t, testWorker.interval, power, angle_interval, att_start, att_stop, att_int, test_list, log_file,
                                        Tx_check, Rx_check, rssi_check, mcs_check, RDK_check, PSC_check, option_check, results_path, att, self.table, iperf, port)
                    # Move worker to thread
                    self.worker.moveToThread(self.thread)

                    # Connect signals and slots
                    self.thread.started.connect(self.worker.run)
                    self.thread.finished.connect(self.thread.deleteLater)
                    self.worker.finished.connect(self.thread.quit)
                    self.worker.finished.connect(self.worker.deleteLater)
                    self.worker.progress.connect(self.update_progress)
                    self.test_progress.show()
                    
                    # Start thread
                    self.thread.start()
                    self.update_status(1)

                    # Final resets
                    # self.start_test.setEnabled(False)
                    self.thread.finished.connect(lambda: self.update_status(0))
                else:
                    # Create list of workers for multiple STBs
                    self.workers = []
                    self.threads = []
                    for i in range(len(self.stb_ip_list)):
                        print(f"Starting test for IP: {self.stb_ip_list[i]}")
                        
                        # Create QThread object
                        self.threads.append(QtCore.QThread())
                        
                        # Create worker objects
                        port = port_manager.get_next_port()
                        self.workers.append(testWorker.testWorker(laptop_ip, self.stb_ip_list[i], router_ip, table_ip, router_user, router_password, bw_text, bw2_text, bw3_text, eth1_value, eth2_value, eth3_value,
                                        country_code, band, file_directory, file_name, t, testWorker.interval, power, angle_interval, att_start, att_stop, att_int, test_list, log_file,
                                        Tx_check, Rx_check, rssi_check, mcs_check, RDK_check, PSC_check, option_check, results_path, att, self.table, iperf, port))
                        
                        self.workers[i].moveToThread(self.threads[i])
                        # 

                        self.threads[i].started.connect(self.workers[i].run)
                        self.threads[i].finished.connect(self.threads[i].deleteLater)
                        self.workers[i].finished.connect(self.threads[i].quit)
                        self.workers[i].finished.connect(self.workers[i].deleteLater)
                        self.workers[i].progress.connect(self.update_progress)
                        self.test_progress.show()

                        # Start thread
                        self.threads[i].start()
                        self.update_status(1)

                        # Final resets
                        self.threads[i].finished.connect(lambda i = i: self.update_status(0))

        else:
            if (self.test_started):
                if multiple_stb_check:
                    for i in range(len(self.stb_ip_list)):
                        self.update_status(self.workers[i].running + 1)
                else:
                    self.update_status(self.worker.running + 1)

# Added multiple_stb_check parameter
    def check_inputs(self, laptop_ip, box_ip, router_ip, table_ip, test_list, multiple_stb_check):
        if not multiple_stb_check:
            if not test_list:
                self.error_dialog = QtWidgets.QMessageBox()
                self.error_dialog.setText("Please select at least one channel to be TESTED!")
                self.error_dialog.setWindowTitle("Invalid Selection")
                self.error_dialog.show()
                return False
            elif apConn.validIPAddress(laptop_ip) is False:
                self.error_dialog = QtWidgets.QMessageBox()
                self.error_dialog.setText("Please insert a valid Host IP address!")
                self.error_dialog.setWindowTitle("Invalid Host IP")
                self.error_dialog.show()
                return False
            elif apConn.validIPAddress(box_ip) is False:
                self.error_dialog = QtWidgets.QMessageBox()
                self.error_dialog.setText("Please insert a valid Box IP address!")
                self.error_dialog.setWindowTitle("Invalid Box IP")
                self.error_dialog.show()
                return False
            elif apConn.validIPAddress(router_ip) is False:
                self.error_dialog = QtWidgets.QMessageBox()
                self.error_dialog.setText("Please insert a valid Access Point IP address!")
                self.error_dialog.setWindowTitle("Invalid Access Point IP")
                self.error_dialog.show()
            elif apConn.validIPAddress(table_ip) is False:
                self.error_dialog = QtWidgets.QMessageBox()
                self.error_dialog.setText("Please insert a valid Turn Table IP address!")
                self.error_dialog.setWindowTitle("Invalid Turn Table IP")
                self.error_dialog.show()
            elif self.version.currentText() == "Choose iPerf Version":
                self.error_dialog = QtWidgets.QMessageBox()
                self.error_dialog.setText("Please select an iPerf version to test!")
                self.error_dialog.setWindowTitle("No iPerf version selected")
                self.error_dialog.show()
            else:
                return True
        else:
            if not test_list:
                self.error_dialog = QtWidgets.QMessageBox()
                self.error_dialog.setText("Please select at least one channel to be TESTED!")
                self.error_dialog.setWindowTitle("Invalid Selection")
                self.error_dialog.show()
                return False
            elif apConn.validIPAddress(laptop_ip) is False:
                self.error_dialog = QtWidgets.QMessageBox()
                self.error_dialog.setText("Please insert a valid Host IP address!")
                self.error_dialog.setWindowTitle("Invalid Host IP")
                self.error_dialog.show()
                return False
            elif apConn.validIPAddress(router_ip) is False:
                self.error_dialog = QtWidgets.QMessageBox()
                self.error_dialog.setText("Please insert a valid Access Point IP address!")
                self.error_dialog.setWindowTitle("Invalid Access Point IP")
                self.error_dialog.show()
            elif apConn.validIPAddress(table_ip) is False:
                self.error_dialog = QtWidgets.QMessageBox()
                self.error_dialog.setText("Please insert a valid Turn Table IP address!")
                self.error_dialog.setWindowTitle("Invalid Turn Table IP")
                self.error_dialog.show()
            elif self.version.currentText() == "Choose iPerf Version":
                self.error_dialog = QtWidgets.QMessageBox()
                self.error_dialog.setText("Please select an iPerf version to test!")
                self.error_dialog.setWindowTitle("No iPerf version selected")
                self.error_dialog.show()
            else:
                return True
                    
    # def update_status(self, n):
    #     # if self.multiple_stb_check:
    #     #     current_worker = self.workers[0]
    #     # else:
    #     #     current_worker = self.worker
            
    #     self.worker.running = n
    #     if (self.worker.running % 2):
    #         self.start_test.setText(QtCore.QCoreApplication.translate("MainWindow", "Pause Test"))
    #     elif (self.worker.running == 0):
    #         self.start_test.setText(QtCore.QCoreApplication.translate("MainWindow", "Start Test"))
    #     else:
    #         self.start_test.setText(QtCore.QCoreApplication.translate("MainWindow", "Resume Test"))


