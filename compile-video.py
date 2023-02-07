from typing import Dict, List, Tuple

from pathlib import Path
from math import floor
import os

import cv2
import numpy as np


# Frame Folders
SOCIETY_FRAMES_DIR = Path('Society Frames')
ORIGINAL_FRAMES_DIR = Path('Original Frames')

# OP Video File
#Input original video file here
OP_FILE = Path('')

# Frame Timing File
FRAME_TIMINGS_FILE = Path('frame-timings.txt')

# Video Framerate
FRAMERATE = 23.976

# Video Frame res
VIDEO_RESOLUTION = (1920, 1080)

def calculate_frame_durations(total_frames: int) -> Dict[int, int]:
    with open(FRAME_TIMINGS_FILE, 'r') as f:
        frame_timings = [int(l.strip()) for l in f.readlines()]

    frame_durations: Dict[int, int] = {}

    # Black frame starts video
    frame_durations[0] = frame_timings[0]

    # Calculate duration of each frame.
    for i in range(0, len(frame_timings) - 1):
        current_frame = frame_timings[i]
        next_frame = frame_timings[i + 1]
        frame_duration = next_frame - current_frame
        frame_durations[i + 1] = frame_duration

    # Calculate duration of the final frame using the duration of the audio.
    final_frame = max(frame_durations.keys()) + 1
    frame_durations[final_frame] = total_frames - frame_timings[final_frame - 1]

    return frame_durations

def main() -> None:
    # Load original video.
    video_original = cv2.VideoCapture(str(OP_FILE))
    total_frames = int(video_original.get(cv2.CAP_PROP_FRAME_COUNT))

    print('Loading durations.')
    # Calculate the duration to hold each frame.
    frame_durations = calculate_frame_durations(total_frames)

    # Load original frames.
    print('Loading frames.')
    original_frames: Dict[int, cv2.Mat] = {}
    for frame_image in ORIGINAL_FRAMES_DIR.glob('*'):
        frame = cv2.imread(str(frame_image))
        original_frames[int(frame_image.stem)] = frame

    # Add initial black padding frame.
    original_frames[0] = np.zeros(original_frames[1].shape, dtype=np.uint8)

    # Load society frames.
    society_frames: Dict[int, cv2.Mat] = {}
    for frame_image in SOCIETY_FRAMES_DIR.glob('*'):
        original_frame = cv2.imread(str(frame_image))
        scaled_frame = cv2.resize(original_frame, VIDEO_RESOLUTION,interpolation = cv2.INTER_AREA)
        society_frames[int(frame_image.stem)] = scaled_frame

    # Create video frame list.
    video: List[cv2.Mat] = []
    for i in range(0, len(original_frames)):
        # Select the society frame if it exists.
        frame = original_frames[i] if i not in society_frames else society_frames[i]
        duration = frame_durations[i]
        video.extend([frame] * duration)

    print('Writing video.')
    # Write video out to file ('_tmp.mp4') with opencv.
    video_fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video_res = original_frames[0].shape[:2][::-1]
    video_writer = cv2.VideoWriter('_tmp.mp4', video_fourcc, FRAMERATE, video_res, True)
    for frame in video:
        video_writer.write(frame)
    video_writer.release()

    print('Adding aduio.')
    # Combine video and audio with FFMPEG
    command = 'ffmpeg -i {0} -i _tmp.mp4 -map 0:a:0 -map 1:v:0 "{1}"'.format(str(OP_FILE), 'Anisoc Draws - Colors.mp4')
    os.system(command)

    # Cleanup
    os.remove('_tmp.mp4')

    print('Finished.')


if __name__ == '__main__':
    main()
