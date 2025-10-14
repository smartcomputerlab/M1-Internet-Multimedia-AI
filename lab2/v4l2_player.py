#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Play from a V4L2 camera using GStreamer, equivalent to:

  gst-launch-1.0 v4l2src device=/dev/video0 \
    ! video/x-h264,width=1280,height=720,framerate=30/1 \
    ! h264parse ! openh264dec ! videoconvert ! xvimagesink
Usage:
  python v4l2_player.py
  python v4l2_player.py --device /dev/video2 --width 640 --height 480 --framerate 15
"""

import sys
import signal
import argparse
import gi
gi.require_version("Gst", "1.0")
gi.require_version("GObject", "2.0")
from gi.repository import Gst, GObject

def main():
    Gst.init(None)
    GObject.threads_init()
    parser = argparse.ArgumentParser(description="Simple V4L2 H.264 camera player")
    parser.add_argument("--device", default="/dev/video0", help="Video device path (default: /dev/video0)")
    parser.add_argument("--width", type=int, default=1280, help="Frame width (default: 1280)")
    parser.add_argument("--height", type=int, default=720, help="Frame height (default: 720)")
    parser.add_argument("--framerate", type=int, default=30, help="Frame rate (fps, default: 30)")
    args = parser.parse_args()
    pipeline_desc = (
        f'v4l2src device={args.device} '
        f'! video/x-h264,width={args.width},height={args.height},framerate={args.framerate}/1 '
        '! h264parse ! openh264dec ! videoconvert ! xvimagesink'
    )
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

