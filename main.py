import sys
import os
from PyQt4 import QtCore, QtGui
from PyQt4 import QtSvg
from app.receive_distribute import ReceiveDistribute
from app.upload_cloud import UploadCloud
from app.save_frames_file import SaveFramesFileThread
from threading import Event
from app.setup_log import setup_log
import imp
import Queue
from collections import deque
from zmq import *
from app.gui_pyqt import StartQT4
from app.pyinstaller_hacks import resource_path
import shutil
import argparse


'''TO DO: Temporary, ugly thing to unpack some data from exe
 because of cloud side limitations in folders zipping'''
def unpack_example_frames():
    try:
        sys._MEIPASS
        if not os.path.exists("saved_frames"):
            os.makedirs("saved_frames")

        for i in range(1, 6):
            shutil.copyfile(resource_path('saved_frames/test_{0}.frames'.format(i)), 'saved_frames/test_{0}.frames'.format(i))
    except AttributeError:
        pass


unpack_example_frames()

parser = argparse.ArgumentParser()
parser.add_argument("-v", "--verbose", required=False, default=False, action="store_true",
                    help="Increase output verbosity.")
args = parser.parse_args()

root_logger = setup_log(args.verbose)
config = imp.load_source('config', 'config.py')


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    gui_queue = deque()
    cloud_tx_queue = deque()
    cloud_rx_queue = deque()
    error_queue = deque()
    file_queue = Queue.Queue()
    path_queue = Queue.Queue()

    stop_event = Event()
    send_active = Event()
    hamApp = StartQT4(stop_event, config, gui_queue, cloud_tx_queue, cloud_rx_queue, error_queue, path_queue, send_active)

    rec = ReceiveDistribute(stop_event, config.config, gui_queue, file_queue)
    rec.start()

    clo = UploadCloud(stop_event, config.config, cloud_rx_queue, cloud_tx_queue, error_queue, send_active)
    clo.start()

    file_save = SaveFramesFileThread(stop_event, config.config, file_queue, path_queue)
    file_save.start()

    hamApp.show()

    status = app.exec_()
    stop_event.set()
    clo.join()
    rec.join()
    file_save.join()
    sys.exit(status)
