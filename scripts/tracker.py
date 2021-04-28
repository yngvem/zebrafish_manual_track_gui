import sys
from PyQt5.QtWidgets import QApplication
from importlib import reload
from ims_track_gui import TrackController, TrackingWindow, TrackData


app = QApplication(sys.argv)
view = TrackingWindow()
model = TrackData()
controller = TrackController(view, model)

view.show()
sys.exit(app.exec_())