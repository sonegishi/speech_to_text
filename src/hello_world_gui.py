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

# +
import sys

from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QMainWindow
# from PyQt5.QtWidgets import QAction
# from PyQt5.QtWidgets import QFileDialog
# from PyQt5.QtGui import QIcon

from hello_world_ui import Ui_MainWindow


# -

class HelloWorldGui(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(HelloWorldGui, self).__init__(parent)
        self._setup_ui(self)
        self._init_ui()

    def _init_ui(self):
        self.show()

    @pyqtSlot()
    def set_text(self, text):
        self.label.setText(text)

    @pyqtSlot()
    def set_text_hello_world(self):
        self.label.setText("Hello World")


app = QApplication(sys.argv)
hello_world_gui = HelloWorldGui()
sys.exit(app.exec_())


