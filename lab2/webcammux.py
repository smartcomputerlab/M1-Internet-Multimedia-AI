#!/usr/bin/env python3
# webcammux.py
# Requires: GStreamer 1.0 + PyGObject (python3-gi)

import argparse
import sys
import gi

gi.require_version("Gst", "1.0")
from gi.repository import Gst

def main():
    parser = argparse.ArgumentParser(
        description="Capture H.264 video from V4L2 and audio from ALSA, mux into Matroska, write to file."
    )
    # Video
    parser.add_argument("--video-device", default="/dev/video0", help="V4L2 video device")
    parser.add_argument("--width", type=int, default=1280, help="Video width")
    parser.add_argument("--height", type=int, default=720, help="Video height")
    parser.add_argument("--framerate", default="30/1", help='Video framerate as fraction, e.g. "30/1"')
    # Audio
    parser.add_argument("--audio-device", default="default", help='ALSA device (e.g. "default", "hw:0,0")')
    parser.add_argument("--channels", type=int, default=2, help="Audio channels")
    parser.add_argument("--rate", type=int, default=16000, help="Audio sample rate (Hz)")
    parser.add_argument("--mp3-bitrate", type=int, default=192, help="MP3 bitrate (kbps)")
    # Output
    parser.add_argument("--output", default="../samples/webcammux.mkv", help="Output MKV path")
    args = parser.parse_args()

    Gst.init(None)

    pipeline_str = (
        # Video branch
        f'v4l2src device="{args.video_device}" ! queue '
        f'! video/x-h264,width={args.width},height={args.height},framerate={args.framerate} '
        f'! h264parse ! queue ! mux. '
        # Audio branch
        f'alsasrc device="{args.audio_device}" '
        f'! audio/x-raw,channels={args.channels},rate={args.rate} '
        f'! audioconvert ! queue ! lamemp3enc bitrate={args.mp3_bitrate} '
        f'! queue ! mux. '
        # Mux + sink
        f'matroskamux name=mux ! queue ! filesink location="{args.output}"'
    )

    pipeline = Gst.parse_launch(pipeline_str)
    bus = pipeline.get_bus()

    pipeline.set_state(Gst.State.PLAYING)
    try:
        while True:
            msg = bus.timed_pop_filtered(
                Gst.SECOND,
                Gst.MessageType.ERROR | Gst.MessageType.EOS
            )
            if not msg:
                continue
            if msg.type == Gst.MessageType.ERROR:
                err, debug = msg.parse_error()
                print(f"ERROR: {err}", file=sys.stderr)
                if debug:
                    print(debug, file=sys.stderr)
                break
            if msg.type == Gst.MessageType.EOS:
                print("Done (EOS).")
                break
    except KeyboardInterrupt:
        print("\nInterrupted, stopping...")
    finally:
        pipeline.set_state(Gst.State.NULL)

if __name__ == "__main__":
    main()

