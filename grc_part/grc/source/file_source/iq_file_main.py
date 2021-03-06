from PyQt4 import QtGui
import os
import sys
from iq_file import Ui_MainWindow
from PyQt4 import QtGui
import time

from PyQt4 import QtCore
import time
import logging
import subprocess
import file_source


class ParamshWrapper:
    def __init__(self, path, frequency_offset):
        self.path_to_iq_file = str(path)
        self.frequency_offset = frequency_offset


class GRCThread(QtCore.QThread):
    finished_signal = QtCore.pyqtSignal(object)

    def __init__(self, params):
        QtCore.QThread.__init__(self)
        self.params = params
        self.process = None

    def run(self):
        print "start thread"
        file_source.main(options=self.params)
        self.finished_signal.emit(True)
        print "stop thread"


class FileChooser(QtGui.QMainWindow, Ui_MainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.buttonChoose.clicked.connect(self.file_browser)
        self.ui.buttonPlay.clicked.connect(self.run_grc)

    def closeEvent(self, event):
        pass

    def file_browser(self):
        file_dialog = QtGui.QFileDialog()
        chosen_path = file_dialog.getOpenFileName(None, 'OpenFile')
        self.ui.pathInput.setText(chosen_path)

    def run_grc(self):
        self.ui.progressBar.setMaximum(0)
        self.ui.statusLabel.setText("Playing")
        self.ui.buttonPlay.setDisabled(True)
        self.ui.frequencyOffset.setDisabled(True)
        self.grc_thread = GRCThread(ParamshWrapper(self.ui.pathInput.toPlainText(), self.ui.frequencyOffset.value()))
        self.grc_thread.finished_signal.connect(self.set_idle)
        self.grc_thread.start()

    def set_idle(self):
        self.ui.progressBar.setMaximum(1)
        self.ui.buttonPlay.setDisabled(False)
        self.ui.frequencyOffset.setDisabled(False)
        self.ui.statusLabel.setText("Idle")


def application():
    app = QtGui.QApplication(sys.argv)
    window = FileChooser()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    application()
