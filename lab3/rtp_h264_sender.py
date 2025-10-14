#!/usr/bin/env python3
# rtp_h264_send.py
# Requires: GStreamer 1.0 + PyGObject (python3-gi)

import argparse
import sys
import gi

gi.require_version("Gst", "1.0")
from gi.repository import Gst

def main():
    parser = argparse.ArgumentParser(
        description="Send H.264 from V4L2 over RTP/UDP."
    )
    # Destination
    parser.add_argument("host", help="Destination IP/hostname (CLIENT_IP)")
    parser.add_argument("--port", type=int, default=8050, help="Destination UDP port for RTP (default: 8050)")
    # Video source/caps
    parser.add_argument("--device", default="/dev/video1", help="V4L2 device (default: /dev/video1)")
    parser.add_argument("--width", type=int, default=1920, help="Width (default: 1920)")
    parser.add_argument("--height", type=int, default=1080, help="Height (default: 1080)")
    parser.add_argument("--framerate", default="30/1", help='Framerate as fraction (default: "30/1")')
    # RTP settings
    parser.add_argument("--mtu", type=int, default=1400, help="RTP packet MTU (default: 1400)")
    parser.add_argument("--pt", type=int, default=96, help="RTP payload type (default: 96)")
    args = parser.parse_args()

    Gst.init(None)

    pipeline_str = (
        f'v4l2src device="{args.device}" ! '
        f'video/x-h264,width={args.width},height={args.height},framerate={args.framerate} ! '
        f'h264parse ! rtph264pay pt={args.pt} mtu={args.mtu} ! '
        f'udpsink host="{args.host}" port={args.port} sync=false async=false'
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

