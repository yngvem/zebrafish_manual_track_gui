# Run instructions

    git clone https://github.com/yngvem/zebrafish_manual_track_gui.git
    cd zebrafish_manual_track_gui
    pip install -e .
    python3 scripts/tracker.py
    
    
1. Load ims-file containing zebrafish bloodflow video
2. Wait for image loading and preprocessing (takes a while, GUI will not respond but there is a progress bar in the terminal window. There is also a wait once the progress bar is at 100%)
3. Adjust contrast by right-clicking and moving mouse up/down and left/right
4. Left click to mark a single particle
5. Left click multiple times to adjust position of mark
6. Use arrow keys on keyboard or buttons in GUI to navigate frames
7. Mark the same particle in the next frame
8. Repeat step 6-7 until particle dissapears (either out of bounds or out of focus plane)
9. Navigate back to the particle's first frame
10. Press [+] button to generate new particle track
11. Repeat step 4-10 untill there are no particles left in the first frame
12. Go to the next frame, and repeat step 4-11 for all unmarked particles


A YAML file with the particle track will be stored in the same folder as the data-file for every frame-change. If the image-stack file is called `filename.ims`, then the track-data file will be named `filename-manualTrack.yml`. The track-data file (if it exists) will be loaded automatically with image files.
