# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.3.4
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QAction
# from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QFileDialog


class Ui_MainWindow(object):
    def _setup_ui(self, MainWindow):
        MainWindow.setObjectName('MainWindow')

        MainWindow.resize(400, 300)

        self.central_widget = QtWidgets.QWidget(MainWindow)
        self.central_widget.setObjectName('centralwidget')

        self.label = QtWidgets.QLabel(self.central_widget)
        self.label.setGeometry(QtCore.QRect(160, 40, 60, 16))
        self.label.setObjectName('label')

        # Set file
        self.pushButton = QtWidgets.QPushButton(self.central_widget)
        self.pushButton.setGeometry(QtCore.QRect(140, 90, 110, 30))
        self.pushButton.setObjectName('pushButton')
        self.pushButton.pressed.connect(self._show_dialog)

        MainWindow.setCentralWidget(self.central_widget)

        # Menu bar
        self.menu_bar = QtWidgets.QMenuBar(MainWindow)
        self.menu_bar.setGeometry(QtCore.QRect(0, 0, 400, 22))
        self.menu_bar.setObjectName('menubar')
        file_menu = self.menu_bar.addMenu('File')
        file_menu.addAction(self._open_file)
        MainWindow.setMenuBar(self.menu_bar)

        # Status bar
        self.status_bar = QtWidgets.QStatusBar(MainWindow)
        self.status_bar.setObjectName('statusbar')
        MainWindow.setStatusBar(self.status_bar)

        self.setGeometry(300, 300, 350, 300)
        self.setWindowTitle('File dialog')

        self._retranslate_ui(MainWindow)
#         self.pushButton.pressed.connect(MainWindow.set_text)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def _retranslate_ui(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate('MainWindow', 'MainWindow'))
        self.label.setText(_translate('MainWindow', 'TextLabel'))
        self.pushButton.setText(_translate('MainWindow', 'PushButton'))
        
    def _open_file(self):
        open_file = QAction('Open', self)
        open_file.setShortcut('Ctrl+O')
        open_file.setStatusTip('Open File')
        open_file.triggered.connect(self._show_dialog)
        return open_file

    def _show_dialog(self):
        file_name = QFileDialog.getOpenFileName(self, 'Open file', '/home')
        if file_name[0]:
            with open(file_name[0], 'r', 'utf-8', 'ignore') as f:
                data = f.read()
                self.label.setText(data)
