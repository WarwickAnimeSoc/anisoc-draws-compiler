from typing import Dict, List

from pathlib import Path
from argparse import ArgumentParser, Namespace
import os

import cv2
import numpy as np


def calculate_frame_durations(total_frames: int, timing_file: Path) -> Dict[int, int]:
    with open(timing_file, 'r') as f:
        frame_timings = [int(l.strip()) for l in f.readlines()]

    frame_durations: Dict[int, int] = {}

    # Black frame starts video.
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


def main(args: Namespace) -> None:
    # Load paths.
    original_frames_path = Path(args.original_frames_dir)
    society_frames_path = Path(args.society_frames_dir)
    timings_file_path = Path(args.timings_file)
    op_file_path = Path(args.original_video)
    # Load original video.
    video_original = cv2.VideoCapture(str(op_file_path))
    total_frames = int(video_original.get(cv2.CAP_PROP_FRAME_COUNT))

    print('Loading durations.')
    # Calculate the duration to hold each frame.
    frame_durations = calculate_frame_durations(total_frames, timings_file_path)

    # Load original frames.
    print('Loading frames.')
    original_frames: Dict[int, cv2.Mat] = {}
    for frame_image in original_frames_path.glob('*'):
        frame = cv2.imread(str(frame_image))
        original_frames[int(frame_image.stem)] = frame

    # Add initial black padding frame.
    original_frames[0] = np.zeros(original_frames[1].shape, dtype=np.uint8)

    # Load society frames.
    society_frames: Dict[int, cv2.Mat] = {}
    for frame_image in society_frames_path.glob('*'):
        original_frame = cv2.imread(str(frame_image))
        scaled_frame = cv2.resize(original_frame, args.resolution, interpolation=cv2.INTER_AREA)
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
    video_writer = cv2.VideoWriter('_tmp.mp4', video_fourcc,  args.framerate, video_res, True)
    for frame in video:
        video_writer.write(frame)
    video_writer.release()

    print('Adding audio.')
    # Combine video and audio with FFMPEG
    command = 'ffmpeg -i {0} -i _tmp.mp4 -map 0:a:0 -map 1:v:0 "{1}"'.format(str(op_file_path), args.output)
    os.system(command)

    # Cleanup
    os.remove('_tmp.mp4')

    print('Finished.')


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('original_frames_dir', type=str)
    parser.add_argument('society_frames_dir', type=str)
    parser.add_argument('timings_file', type=str)
    parser.add_argument('original_video', type=str)
    parser.add_argument('-o', '--output', type=str, default='out.mp4')
    parser.add_argument('-fr', '--framerate', type=float, default=23.976)
    parser.add_argument('-r', '--resolution', type=int, nargs=2, default=(1920, 1080))

    args = parser.parse_args()
    main(args)
