import matplotlib.backends.backend_qt5agg as mpl_backend
import matplotlib.pyplot as plt
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeySequence


class SingleSelectionList(QtWidgets.QListWidget):
    def __init__(self, parent=None, max_selected=1):
        super().__init__(parent)
        self.max_selected = max_selected


class NavigationToolbar(mpl_backend.NavigationToolbar2QT):
    def __init__(self, canvas, parent=None):
        super().__init__(canvas, parent)
        self.remove_tool(1)
        self.remove_tool(1)
        self.remove_tool(4)
        self.remove_tool(4)

    def remove_tool(self, tool_idx):
        self.removeAction(self.actions()[tool_idx])


class MatplotlibView(QtWidgets.QWidget):
    def __init__(self, figure, show_coordinates=True, parent=None, flags=Qt.WindowFlags()):
        super().__init__(parent=parent, flags=flags)
        self.figure = figure
        self.canvas = mpl_backend.FigureCanvasQTAgg(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)
        if not show_coordinates:
            self.toolbar.remove_tool(len(self.toolbar.actions()) - 1)

        self.setLayout(QtWidgets.QVBoxLayout())
        self.layout().addWidget(self.canvas)
        self.layout().addWidget(self.toolbar)
        self.updateGeometry()


class TrackingWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.figure = plt.Figure()
        self.axes = self.figure.add_axes((0, 0, 1, 1))
        self.image = self.axes.imshow([[0]], vmin=0, vmax=100, cmap="gray")
        self.points = self.axes.scatter([], [], facecolors='none', edgecolors="navy", linewidth=2)
        self.current_point = self.axes.scatter([], [], facecolors='none', edgecolors="tomato", linewidth=2)

        self.mpl_view = MatplotlibView(self.figure, parent=self)
        self.track_list = SingleSelectionList(parent=self)
        self.add_track_btn = QtWidgets.QPushButton(text="+", parent=self)
        self.del_track_btn = QtWidgets.QPushButton(text="-", parent=self)
        self.particle_list = SingleSelectionList(parent=self)
        self.del_particle_btn = QtWidgets.QPushButton(text="Delete mark at current frame", parent=self)
        self.frame_slider = QtWidgets.QSlider(Qt.Horizontal, parent=self)
        self.frame_slider.setMaximum(7000)
        self.next_frame_btn = QtWidgets.QPushButton(text="->", parent=self)
        self.prev_frame_btn = QtWidgets.QPushButton(text="<-", parent=self)
        self.open_btn = QtWidgets.QPushButton(text="Open", parent=self)
        self.frame_label = QtWidgets.QLabel(text="Frame: 0", parent=self)

        self.open_dialog = QtWidgets.QFileDialog(self, caption="Select data file")

        layout = QtWidgets.QGridLayout()
        layout.addWidget(self.mpl_view, 0, 0, 4, 4)
        layout.addWidget(self.track_list, 0, 4, 1, 2)
        layout.addWidget(self.add_track_btn, 1, 4, 1, 1)
        layout.addWidget(self.del_track_btn, 1, 5, 1, 1)
        layout.addWidget(self.particle_list, 2, 4, 1, 2)
        layout.addWidget(self.del_particle_btn, 3, 4, 1, 2)
        layout.addWidget(self.prev_frame_btn, 4, 0, 1, 1)
        layout.addWidget(self.frame_label, 4, 1, 1, 1)
        layout.addWidget(self.frame_slider, 4, 2, 1, 1)
        layout.addWidget(self.next_frame_btn, 4, 3, 1, 1)
        layout.addWidget(self.open_btn, 4, 4, 1, 2)
        self.setLayout(layout)

        self.shortcut_open = QtWidgets.QShortcut(QKeySequence('Ctrl+O'), self)
        self.shortcut_next_arrow = QtWidgets.QShortcut(Qt.Key_Right, self)
        self.shortcut_next_d = QtWidgets.QShortcut(Qt.Key_D, self)
        self.shortcut_prev_arrow = QtWidgets.QShortcut(Qt.Key_Left, self)
        self.shortcut_prev_d = QtWidgets.QShortcut(Qt.Key_A, self)
        self.shortcut_add_track = QtWidgets.QShortcut(Qt.Key_Plus, self)
        
    def set_tracks(self, tracks, current_track_id):
        self.track_list.clear()
        for track in tracks:
            item = QtWidgets.QListWidgetItem(str(track), self.track_list)
            if track == current_track_id:
                self.track_list.setCurrentItem(item)

    def set_frame(self, frame_data, points, current_point):
        # Draw image
        old_data = self.image.get_array()
        if old_data.shape != frame_data.shape:
            clim = self.image.get_clim()
            self.image.remove()
            self.image = self.axes.imshow(frame_data, vmin=clim[0], vmax=clim[1], cmap="gray")

            self.axes.set_xlim(0, frame_data.shape[1])
            self.axes.set_ylim(0, frame_data.shape[0])
            self.axes.set_title(f"vmin: {clim[0]}, vmax: {clim[1]}")
        else:
            self.image.set_array(frame_data)
        
        self.set_points(points, current_point)
        self.frame_label.setText(f"Frame: {self.frame_slider.value()}")
        
    def set_points(self, points, current_point):
        # Draw points
        self.points.set_offsets(
            [point for i, point in points.items() if i != current_point]
        )
        if current_point in points:
            self.current_point.set_offsets(
                [points[current_point]]
            )
        else:
            self.current_point.set_offsets([])

        # Update plot
        self.mpl_view.canvas.draw()
    
    def set_vmin(self, vmin):
        self.image.set_clim(vmin=vmin)
        clim = self.image.get_clim()
        self.axes.set_title(f"vmin: {clim[0]}, vmax: {clim[1]}")
        self.mpl_view.canvas.draw()
    
    def set_vmax(self, vmax):
        self.image.set_clim(vmax=vmax)
        clim = self.image.get_clim()
        self.axes.set_title(f"vmin: {clim[0]}, vmax: {clim[1]}")
        self.mpl_view.canvas.draw()
    
    def open_file(self):
        return self.open_dialog.getOpenFileName(filter="*.ims")[0]
        


class TrackingWindow(QtWidgets.QMainWindow):
    """Main Window."""
    def __init__(self, parent=None):
        """Initializer."""
        super().__init__(parent)
        self.setWindowTitle('QMainWindow')
        self.widget = TrackingWidget()
        self.setCentralWidget(self.widget)


if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    win = TrackingWindow()
    win.show()
    sys.exit(app.exec_())