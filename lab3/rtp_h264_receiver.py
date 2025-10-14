#!/usr/bin/env python3
# rtp_h264_recv.py
# Requires: GStreamer 1.0 + PyGObject (python3-gi)

import argparse
import sys
import gi

gi.require_version("Gst", "1.0")
from gi.repository import Gst

def main():
    parser = argparse.ArgumentParser(
        description="Receive H.264 over RTP (UDP) and display it."
    )
    parser.add_argument("--port", type=int, default=8050, help="UDP port to listen on")
    parser.add_argument("--clock-rate", type=int, default=90000, help="RTP clock rate")
    parser.add_argument("--encoding-params", default="1", help="H.264 encoding-params (often 1)")
    parser.add_argument("--pt", type=int, help="(Optional) RTP payload type (e.g., 96)")
    parser.add_argument("--sink", default="xvimagesink", help="Video sink (e.g., xvimagesink, autovideosink)")
    args = parser.parse_args()

    Gst.init(None)

    # Build caps string (matches your gst-launch line)
    caps = (
        f"application/x-rtp, media=(string)video, "
        f"clock-rate=(int){args.clock_rate}, "
        f"encoding-name=(string)H264, "
        f"encoding-params=(string){args.encoding_params}"
    )
    if args.pt is not None:
        caps += f", payload=(int){args.pt}"

    pipeline_str = (
        f'udpsrc port={args.port} caps="{caps}" ! '
        f'rtph264depay ! h264parse ! avdec_h264 ! queue ! videoconvert ! {args.sink}'
    )

    pipeline = Gst.parse_launch(pipeline_str)
    bus = pipeline.get_bus()

    pipeline.set_state(Gst.State.PLAYING)
    try:
        while True:
            msg = bus.timed_pop_filtered(
                Gst.SECOND, Gst.MessageType.ERROR | Gst.MessageType.EOS
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
                print("EOS reached.")
                break
    except KeyboardInterrupt:
        print("\nInterrupted, stopping...")
    finally:
        pipeline.set_state(Gst.State.NULL)

if __name__ == "__main__":
    main()

