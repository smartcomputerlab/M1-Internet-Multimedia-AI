#!/usr/bin/env python3
# -*- coding: utf-8 -
"""
Equivalent to:
  gst-launch-1.0 v4l2src device=/dev/video0 num-buffers=300 \
    ! video/x-raw,width=320,height=240,framerate=15/1 \
    ! videoconvert ! progressreport ! jpegenc ! avimux \
    ! filesink location=../samples/webcamconvjpeg.avi

Now with command-line arguments for width, height, framerate, and output file.
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
    parser = argparse.ArgumentParser(description="Capture webcam to AVI with JPEG frames")
    parser.add_argument("--device", default="/dev/video0", help="V4L2 device path (default: /dev/video0)")
    parser.add_argument("--num-buffers", type=int, default=300, help="Number of frames to capture (default: 300)")
    parser.add_argument("--width", type=int, default=320, help="Frame width (default: 320)")
    parser.add_argument("--height", type=int, default=240, help="Frame height (default: 240)")
    parser.add_argument("--framerate", type=int, default=15, help="Frame rate in fps (default: 15)")
    parser.add_argument("--output", default="../samples/webcamconvjpeg.avi",
                        help="Output AVI file path (default: ../samples/webcamconvjpeg.avi)")
    args = parser.parse_args()

    pipeline_desc = (
        f"v4l2src device={args.device} num-buffers={args.num_buffers} "
        f"! video/x-raw,width={args.width},height={args.height},framerate={args.framerate}/1 "
        "! videoconvert ! progressreport ! jpegenc ! avimux "
        f"! filesink location={args.output}"
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
            print("✅ Finished writing video.")
            loop.quit()
        elif t == Gst.MessageType.ERROR:
            err, debug = message.parse_error()
            print(f"❌ ERROR: {err}", file=sys.stderr)
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

