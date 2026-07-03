#!/usr/bin/env python3
"""
Extract one screenshot per distinct on-screen action from a screen recording.

Approach: sample the video at a fixed rate, track frame-to-frame visual
difference, and capture a screenshot once the screen has just STABILIZED
after a burst of change (i.e. right after a click/transition finishes,
not mid-animation). This avoids blurry in-between frames and avoids
firing once per pixel-flicker.

Usage:
    python3 extract_keyframes.py <video_path> <output_dir> [--max-frames N]

Outputs:
    <output_dir>/frame_0001.png, frame_0002.png, ...
    <output_dir>/manifest.json  -> [{"index", "timestamp_seconds", "path"}, ...]
"""
import argparse
import json
import os
import sys

import cv2
import numpy as np


def extract(video_path, out_dir, sample_fps=4.0, change_thresh=6.0,
            stable_frames_needed=2, min_gap_seconds=1.2, max_frames=60):
    os.makedirs(out_dir, exist_ok=True)

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(json.dumps({"error": f"Could not open video: {video_path}"}))
        sys.exit(1)

    src_fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = total_frames / src_fps if src_fps else 0

    step = max(1, int(round(src_fps / sample_fps)))

    prev_small = None
    changing = False
    stable_count = 0
    last_capture_t = -min_gap_seconds
    manifest = []
    frame_idx = 0

    def save_frame(frame, t_seconds):
        idx = len(manifest) + 1
        fname = f"frame_{idx:03d}.png"
        fpath = os.path.join(out_dir, fname)
        cv2.imwrite(fpath, frame)
        manifest.append({
            "index": idx,
            "timestamp_seconds": round(t_seconds, 2),
            "path": fpath,
            "filename": fname,
        })

    first_frame = None
    last_frame = None
    last_t = 0.0

    while True:
        ok, frame = cap.read()
        if not ok:
            break
        if frame_idx % step == 0:
            t = frame_idx / src_fps
            small = cv2.resize(frame, (160, 90)).astype(np.int16)

            if first_frame is None:
                first_frame = frame.copy()
                save_frame(frame, t)
                prev_small = small
                last_frame, last_t = frame, t
                frame_idx += 1
                continue

            # Full color-channel diff (not grayscale) so pure hue changes
            # with similar luminance (e.g. blue -> red UI highlight) still register.
            diff = np.mean(np.abs(small - prev_small))

            if diff > change_thresh:
                changing = True
                stable_count = 0
            elif changing:
                stable_count += 1
                if stable_count >= stable_frames_needed:
                    if (t - last_capture_t) >= min_gap_seconds and len(manifest) < max_frames:
                        save_frame(frame, t)
                        last_capture_t = t
                    changing = False
                    stable_count = 0

            prev_small = small
            last_frame, last_t = frame, t

        frame_idx += 1

    # Always capture the final on-screen state if we haven't already
    if last_frame is not None and (last_t - last_capture_t) >= min_gap_seconds and len(manifest) < max_frames:
        save_frame(last_frame, last_t)

    cap.release()

    result = {
        "video_path": video_path,
        "duration_seconds": round(duration, 2),
        "source_fps": src_fps,
        "keyframe_count": len(manifest),
        "keyframes": manifest,
    }
    with open(os.path.join(out_dir, "manifest.json"), "w") as f:
        json.dump(result, f, indent=2)

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("video_path")
    parser.add_argument("output_dir")
    parser.add_argument("--max-frames", type=int, default=60)
    parser.add_argument("--change-thresh", type=float, default=6.0)
    parser.add_argument("--min-gap-seconds", type=float, default=1.2)
    args = parser.parse_args()

    extract(
        args.video_path,
        args.output_dir,
        change_thresh=args.change_thresh,
        min_gap_seconds=args.min_gap_seconds,
        max_frames=args.max_frames,
    )
