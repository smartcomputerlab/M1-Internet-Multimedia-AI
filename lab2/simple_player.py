#!/usr/bin/env python3

import sys
import signal
import gi

gi.require_version("Gst", "1.0")
gi.require_version("GObject", "2.0")
from gi.repository import Gst, GObject

def main():
    Gst.init(None)
    GObject.threads_init()
    # Use CLI arg if provided, otherwise default to your sample
    media_path = sys.argv[1] if len(sys.argv) > 1 else "../samples/bunny.mp4"
    # Exact pipeline embedded directly (same as your gst-launch line)
    pipeline_desc = (
        f'filesrc location="{media_path}" ! qtdemux name=foo '
        'foo.video_0 ! queue ! decodebin ! videoconvert ! ximagesink '
        'foo.audio_0 ! queue ! decodebin ! audioconvert ! alsasink'
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
    ret = pipeline.set_state(Gst.State.PLAYING)
    if ret == Gst.StateChangeReturn.FAILURE:
        print("Could not set pipeline to PLAYING.", file=sys.stderr)
        sys.exit(1)
    try:
        loop.run()
    finally:
        pipeline.set_state(Gst.State.NULL)

if __name__ == "__main__":
    main()

