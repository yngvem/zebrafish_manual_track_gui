from pathlib import Path

from matplotlib.backend_bases import MouseButton


class TrackController:
    def __init__(self, view, model):
        self.view = view
        self.model = model
        
        self.view.widget.open_btn.clicked.connect(self.open_file)
        
        self.view.widget.frame_slider.valueChanged.connect(self.set_frame)

        self.model.current_frame_changed.connect(self.update_frame)
        self.view.widget.next_frame_btn.clicked.connect(self.next_frame)
        self.view.widget.prev_frame_btn.clicked.connect(self.prev_frame)

        self.model.num_frames_changed.connect(self.update_slider)

        self.press_event = None
        self.view.widget.mpl_view.canvas.mpl_connect('button_press_event', self.mouse_press)
        self.view.widget.mpl_view.canvas.mpl_connect('button_release_event', self.mouse_release)
        self.view.widget.mpl_view.canvas.mpl_connect('motion_notify_event', self.mouse_drag)
        
        self.model.vmax_changed.connect(self.adjust_vmax)
        self.model.vmin_changed.connect(self.adjust_vmin)

        self.model.points_changed.connect(self.update_points)
        self.model.current_track_changed.connect(self.update_tracks)

        self.view.widget.add_track_btn.clicked.connect(self.add_track)
        self.view.widget.del_track_btn.clicked.connect(self.del_track)

        self.view.widget.track_list.clicked.connect(self.select_track)
        self.view.widget.del_particle_btn.clicked.connect(self.del_point)


        self.view.widget.shortcut_open.activated.connect(self.open_file)
        self.view.widget.shortcut_next_arrow.activated.connect(self.next_frame)
        self.view.widget.shortcut_next_d.activated.connect(self.next_frame)
        self.view.widget.shortcut_prev_arrow.activated.connect(self.prev_frame)
        self.view.widget.shortcut_prev_d.activated.connect(self.prev_frame)
        self.view.widget.shortcut_add_track.activated.connect(self.add_track)
        

    def open_file(self):
        filename = self.view.widget.open_file()
        if filename:
            filename = Path(filename)
            if filename != self.model.video_path:
                self.model.load_video(filename)
    
    def update_frame(self, value):
        self.view.widget.set_frame(
            self.model.track_video[self.model.current_frame].squeeze(),
            self.model.current_points,
            self.model.current_track
        )
    
    def set_frame(self, *args):
        current_frame = self.view.widget.frame_slider.value()
        self.model.current_frame = current_frame
    
    def next_frame(self):
        frame_slider = self.view.widget.frame_slider
        frame_slider.setValue(frame_slider.value() + 1)

    def prev_frame(self):
        frame_slider = self.view.widget.frame_slider
        frame_slider.setValue(frame_slider.value() - 1)
    
    def adjust_vmax(self, value):
        self.view.widget.set_vmax(value)

    def adjust_vmin(self, value):
        self.view.widget.set_vmin(value)
    
    def update_slider(self, value):
        self.view.widget.frame_slider.setMaximum(self.model.num_frames - 1)
        self.view.widget.frame_slider.setMinimum(0)

    def mouse_drag(self, event):
        if self.press_event is None:
            return
        canvas = self.view.widget.mpl_view.canvas
        if abs(round(255*(event.x - self.press_event.x) / canvas.width())) >= 1:
            self.model.vmin += round(255*(event.x - self.press_event.x) / canvas.width())
            self.press_event = event
        if abs(round(255*(event.y - self.press_event.y) / canvas.height())) >= 1:
            self.model.vmax += round(255*(event.y - self.press_event.y) / canvas.height())
            self.press_event = event
        
    def mouse_press(self, event):
        if event.button == MouseButton.RIGHT:
            self.press_event = event
        elif event.button == MouseButton.LEFT:
            self.model.set_point(event.xdata, event.ydata)

    def mouse_release(self, event):
        self.press_event = None
    
    def update_points(self, *args):
        self.view.widget.set_points(self.model.current_points, self.model.current_track)
        self.view.widget.particle_list.clear()
        self.view.widget.particle_list.addItems([
            f"{key}: ({value[0]:.1f}, {value[1]:.1f})" for key, value in self.model.tracks[self.model.current_track].items()
        ])

    def update_tracks(self, value):
        self.view.widget.track_list.clear()
        self.view.widget.track_list.addItems([str(track) for track in self.model.tracks])
        for i, track in enumerate(self.model.tracks):
            if track == self.model.current_track:
                row = i
                break
        else:
            raise ValueError("Not valid track")
        
        self.view.widget.track_list.setCurrentRow(row)
        self.update_points()
    
    def add_track(self):
        self.model.add_track()

    def del_track(self):
        self.model.delete_track()

    def select_track(self, *args):
        track = self.view.widget.track_list.currentItem()
        self.model.current_track = int(track.text())
    
    def del_point(self):
        current_track = self.model.current_track
        current_frame = self.model.current_frame
        if current_track in self.model.frame_to_track_map[current_frame]:
            self.model.remove_point()
            self.update_points()