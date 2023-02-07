# anisoc-draws-compiler
A python script to combine individual frames created by members into a video for the Anisoc Draws event. The script will generate a video using the original frames from the video and replace the frames with society drawn frames where available.

# How to use
To run the script you will need Python 3.

Required packages for the script can be installed using `pip install -r requirements.txt`. 

Input all chosen frames from the original video into a folder and input the society drawn frames into another folder. The format of the image names should be formatted such as `0003.png` for frame number 3.
 
A `timings.txt` file must be created where the frame number of the next frame appearing must be noted down in this format:

```
    24
    34 
    64
``` 
where `24` denotes how long the initial black frame is held before the first frame is used. `34` denotes that the first frame is held until `34` frames have passed then passed to 2nd frame and so forth.

Example usage of the script is as follows `python .\compile-video.py "input/Original Frames" "input/Society Frames" "input/frame-timings.txt" "input/CodeGeass-OP1.webm"`
where `CodeGeass-OP1.webm` is the original source video.

# Notes
The output video name of the script is set to `out.mp4` but can be changed using the `-o` argument.

The default framerate of the video is set to `23.976` but can changed with the `-fr` argument.

The default resolution of the video is `1920 x 1080` but can be changed with the `-r` argument.
