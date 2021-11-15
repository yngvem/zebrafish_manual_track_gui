import yaml
from collections import defaultdict
from pathlib import Path

import numpy as np
from PyQt5.QtCore import QObject, pyqtSignal

from .files import ims

#from .utils import PythonObjectEncoder, as_python_object


class TrackData(QObject):
    current_frame_changed = pyqtSignal(int)
    points_changed = pyqtSignal(bool)
    num_frames_changed = pyqtSignal(int)
    current_track_changed = pyqtSignal(int)
    vmin_changed = pyqtSignal(int)
    vmax_changed = pyqtSignal(int)
    

    def __init__(self):
        super().__init__()
        self.video_path: Path = None
        self.track_path: Path = None

        self.track_video: np.ndarray = None
        self.background_img: np.ndarray = None
        self._num_frames = 0
        self._vmin: int = 0
        self._vmax: int = 100
        self._current_frame: int = 0
        self._current_track = None
        self.num_tracks_added = 0

        self.tracks: dict = None
        self.frame_to_track_map: dict = defaultdict(set)

    def load_video(self, ims_path):
        ims_path = Path(ims_path)
        if len(sorted(ims_path.parent.glob("*Snap*"))) > 0:
            bg_path = sorted(ims_path.parent.glob("*Snap*"))[0]
            self.background_img = ims.load_background(bg_path)
        elif len(sorted(ims_path.parent.parent.glob("*Snap*"))) > 0:
            bg_path = sorted(ims_path.parent.parent.glob("*Snap*"))[0]
            self.background_img = ims.load_background(bg_path)
        else:
            self.background_img = None

        # Load video and cast to 8-bit
        self.track_video = ims.load_video_stack(ims_path, progress=True, num_timesteps=None).squeeze()
        self.track_video -= self.track_video.min()
        self.track_video = (self.track_video * (255 / self.track_video.max())).astype(np.uint8)
        print("Loaded video", flush=True)

        self.video_path = ims_path
        self.track_path = self.video_path.parent / f"{self.video_path.stem}-manualTrack.yml"
        

        if self.track_path.is_file():
            with open(self.track_path, "r") as f:
                (
                    self.tracks,
                    self.frame_to_track_map,
                    self.num_tracks_added,
                ) = yaml.unsafe_load(f)
        else:
            self.tracks = {0: {}}
            self.frame_to_track_map = defaultdict(set)
            self.num_tracks_added = 1

        self.current_frame = 0
        self.num_frames = self.track_video.shape[0]
        self.current_track = max(self.tracks.keys())

    def save_tracks(self):
        with open(self.track_path, "w") as f:
            yaml.dump(
                [
                    self.tracks,
                    self.frame_to_track_map,
                    self.num_tracks_added,
                ],
                f
            )

    @property
    def vmin(self):
        return self._vmin

    @vmin.setter
    def vmin(self, value):
        if value != self.vmin:
            self._vmin = min(max(value, 0), self.vmax - 1)
            self.vmin_changed.emit(self.vmin)

    @property
    def vmax(self):
        return self._vmax

    @vmax.setter
    def vmax(self, value):
        if value != self.vmax:
            self._vmax = max(min(value, 255), self.vmin + 1)
            self.vmax_changed.emit(self.vmax)

    @property
    def current_track(self):
        return self._current_track

    @current_track.setter
    def current_track(self, value):
        if value != self.current_track:
            self._current_track = value
            self.current_track_changed.emit(self.current_track)
    
    @property
    def current_frame(self):
        return self._current_frame

    @current_frame.setter
    def current_frame(self, value):
        next_frame = min(max(value, 0), self.num_frames)
        self._current_frame = next_frame
        self.current_frame_changed.emit(next_frame)
        self.save_tracks()
    
    @property
    def num_frames(self):
        return self._num_frames
    
    @num_frames.setter
    def num_frames(self, value):
        self._num_frames = value
        self.num_frames_changed.emit(value)

    @property
    def current_points(self):
        tracks = self.tracks
        i = self.current_frame
        return {track: tracks[track][i] for track in self.frame_to_track_map[i]}

    def set_point(self, x, y):
        self.tracks[self.current_track][self.current_frame] = (x, y)
        self.frame_to_track_map[self.current_frame].add(self.current_track)
        self.points_changed.emit(True)

    def remove_point(self):
        del self.tracks[self.current_track][self.current_frame]
        self.frame_to_track_map[self.current_frame] -= {self.current_track}

    def remove_current_track(self):
        del self.tracks[self.current_track]
        for frame in self.frame_to_track_map:
            self.frame_to_track_map[frame] -= {self.current_track}
        
        self.current_track = max(self.tracks.keys())
    
    def add_track(self):
        next_track = self.num_tracks_added
        self.num_tracks_added += 1
        self.tracks[next_track] = {}
        self.current_track = next_track
        self.save_tracks()
    
    def delete_track(self):
        del self.tracks[self.current_track]
        for tracks_in_frame in self.frame_to_track_map.values():
            tracks_in_frame -= {self.current_track}
        
        if len(self.tracks) == 0:
            self.add_track()
        self.current_track = max(self.tracks.keys())
        self.save_tracks()
    

    
