#!/usr/bin/env python3
import argparse
import cv2
import math
import sys


def parse_args():
    p = argparse.ArgumentParser(description="Downsample video by scale factor and save to --output")
    p.add_argument("input", help="Input video file")
    p.add_argument(
        "--scale",
        type=float,
        default=0.5,
        help="Downsampling factor in (0, 1]. e.g. 0.5 => half width/height",
    )
    p.add_argument("--output", required=True, help="Output video path")
    p.add_argument("--codec", default="mp4v", help="FourCC codec (default: mp4v)")
    p.add_argument("--fps", type=float, default=0, help="Override output FPS (default: use input FPS)")
    return p.parse_args()


def main():
    args = parse_args()
    if not math.isfinite(args.scale) or args.scale <= 0 or args.scale > 1.0:
        print("scale must be a finite number in (0, 1]", file=sys.stderr)
        sys.exit(1)

    cap = cv2.VideoCapture(args.input)
    if not cap.isOpened():
        print("Failed to open input:", args.input, file=sys.stderr)
        sys.exit(1)

    writer = None
    try:
        in_fps = cap.get(cv2.CAP_PROP_FPS) or 0
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        if width == 0 or height == 0:
            print("Failed to read input resolution", file=sys.stderr)
            sys.exit(1)

        out_w = max(1, int(round(width * args.scale)))
        out_h = max(1, int(round(height * args.scale)))
        out_fps = args.fps if args.fps > 0 else (in_fps if in_fps > 0 else 30.0)

        fourcc = cv2.VideoWriter_fourcc(*args.codec)
        writer = cv2.VideoWriter(args.output, fourcc, out_fps, (out_w, out_h))
        if not writer.isOpened():
            print("Failed to open output for writing:", args.output, file=sys.stderr)
            sys.exit(1)

        while True:
            ret, frame = cap.read()
            if not ret:
                break
            small = cv2.resize(frame, (out_w, out_h), interpolation=cv2.INTER_AREA)
            writer.write(small)

        print("Saved:", args.output, "resolution:", out_w, "x", out_h, "fps:", out_fps)
    finally:
        cap.release()
        if writer is not None:
            writer.release()


if __name__ == "__main__":
    main()
