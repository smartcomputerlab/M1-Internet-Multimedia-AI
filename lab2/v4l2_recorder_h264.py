#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Equivalent to:

  gst-launch-1.0 v4l2src device=/dev/video0 \
    ! queue ! video/x-h264,width=1280,height=720,framerate=30/1 \
    ! h264parse ! queue ! matroskamux \
    ! filesink location=../samples/webcam.video_h264.mkv
"""

import sys
import signal
import argparse
import shlex
import gi

gi.require_version("Gst", "1.0")
gi.require_version("GObject", "2.0")
from gi.repository import Gst, GObject


def main():
    Gst.init(None)
    GObject.threads_init()

    p = argparse.ArgumentParser(description="Capture H.264 from V4L2 to Matroska (.mkv)")
    p.add_argument("--device", default="/dev/video0",
                   help="V4L2 device path (default: /dev/video0)")
    p.add_argument("--width", type=int, default=1280,
                   help="Frame width (default: 1280)")
    p.add_argument("--height", type=int, default=720,
                   help="Frame height (default: 720)")
    p.add_argument("--framerate", type=int, default=30,
                   help="Frames per second (default: 30)")
    p.add_argument("--num-buffers", type=int, default=0,
                   help="Number of buffers to capture; 0 = unlimited until Ctrl+C (default: 0)")
    p.add_argument("--output", default="../samples/webcam.video_h264.mkv",
                   help="Output MKV file path (default: ../samples/webcam.video_h264.mkv)")
    args = p.parse_args()

    # Quote the file path in case it contains spaces
    output_quoted = shlex.quote(args.output)

    # Build the pipeline description (mirrors your gst-launch line)
    pipeline_desc = (
        f"v4l2src device={args.device} "
        f"{'' if args.num_buffers <= 0 else f'num-buffers={args.num_buffers} '} "
        "! queue "
        f"! video/x-h264,width={args.width},height={args.height},framerate={args.framerate}/1 "
        "! h264parse "
        "! queue ! matroskamux "
        f"! filesink location={output_quoted}"
    )

    print("Launching pipeline:")
    print(pipeline_desc)

    try:
        pipeline = Gst.parse_launch(pipeline_desc)
    except Exception as e:
        print(f"Failed to create pipeline: {e}", file=sys.stderr)
        sys.exit(1)

    loop = GObject.MainLoop()
    bus = pipeline.get_bus()
    bus.add_signal_watch()

    def on_message(bus, message):
        t = message.type
        if t == Gst.MessageType.EOS:
            print("Finished writing MKV.")
            loop.quit()
        elif t == Gst.MessageType.ERROR:
            err, debug = message.parse_error()
            print(f"ERROR: {err}", file=sys.stderr)
            if debug:
                print(f"Debug info: {debug}", file=sys.stderr)
            loop.quit()
        return True

    bus.connect("message", on_message)

    def handle_sigint(sig, frame):
        print("Interrupted, stopping pipeline...")
        pipeline.set_state(Gst.State.NULL)
        loop.quit()

    signal.signal(signal.SIGINT, handle_sigint)

    if pipeline.set_state(Gst.State.PLAYING) == Gst.StateChangeReturn.FAILURE:
        print("Could not set pipeline to PLAYING.", file=sys.stderr)
        sys.exit(1)

    try:
        loop.run()
    finally:
        pipeline.set_state(Gst.State.NULL)


if __name__ == "__main__":
    main()

