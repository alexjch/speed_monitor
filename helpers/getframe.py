#!/usr/bin/env python3
import sys
import cv2
import argparse
from pathlib import Path

_default_out_file = "out.jpeg"
_frame_n = 2

def parse_arguments():
    parser = argparse.ArgumentParser(description="Extract a frame N from provided video")
    parser.add_argument("input", help="Path to input video file")
    parser.add_argument("--output", help="File name for output frame, the extension is always jpeg",
                        required=False, default=_default_out_file)
    parser.add_argument("--number", help="Frame number to extract", default=2, type=int)

    return parser.parse_args()

def extract_frame_to_jpeg(input_file: str, output_file: str = _default_out_file, frame_n: int = _frame_n) -> None:
    """
    Extract frame_n from a video file and save it as a JPEG image.
    
    The output image maintains the same resolution as the input video.
    
    Args:
        input_file: Path to the input video file
        output_file: Path for the output JPEG file (default: "out.jpeg")
    
    Raises:
        FileNotFoundError: If the input video file does not exist
        ValueError: If the video cannot be opened or frame 2 cannot be extracted
    """
    input_path = Path(input_file)
    
    if not input_path.exists():
        raise FileNotFoundError(f"Video file not found: {input_file}")
    
    cap = cv2.VideoCapture(str(input_path))
    
    if not cap.isOpened():
        raise ValueError(f"Unable to open video file: {input_file}")
    
    # For some codecs/containers this value can be approximate
    max_frame = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    if frame_n > max_frame:
        raise ValueError(f"Frame {frame_n} is more than the total number of frames {max_frame}")

    # Move to frame 2 (0-indexed)
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_n)
    
    ok, frame = cap.read()
    cap.release()
    
    if not ok:
        raise ValueError(f"Unable to extract frame {frame_n} from video")

    cv2.imwrite(output_file, frame)


if __name__ == "__main__":
    args = parse_arguments()
    try:
        extract_frame_to_jpeg(args.input, args.output, args.number)
        sys.exit(0)
    except Exception as e:
        print(e, file=sys.stderr)
        sys.exit(1)
