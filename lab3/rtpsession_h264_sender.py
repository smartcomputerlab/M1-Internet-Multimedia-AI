#!/usr/bin/env python3
# rtp_h264_rtcp_sender.py
# Requires: GStreamer 1.0 + PyGObject (python3-gi)

import argparse
import sys
import gi

gi.require_version("Gst", "1.0")
from gi.repository import Gst

def main():
    parser = argparse.ArgumentParser(
        description="Send H.264 over RTP with RTCP using an rtpsession."
    )
    # Source / caps
    parser.add_argument("--device", default="/dev/video0", help="V4L2 video device")
    parser.add_argument("--width", type=int, default=1920, help="Video width")
    parser.add_argument("--height", type=int, default=1080, help="Video height")
    parser.add_argument("--framerate", default="30/1", help='Framerate as fraction (e.g., "30/1")')

    # RTP/RTCP destination
    parser.add_argument("--host", default="127.0.0.1", help="Destination host/IP")
    parser.add_argument("--rtp-port", type=int, default=8050, help="Destination RTP port")
    parser.add_argument("--rtcp-port", type=int, default=8051, help="Destination RTCP port")
    parser.add_argument("--pt", type=int, default=96, help="RTP payload type for H.264")

    args = parser.parse_args()
    Gst.init(None)

    # Matches your gst-launch pipeline, with PT/config made explicit
    pipeline_str = (
        f'v4l2src device="{args.device}" ! '
        f'video/x-h264,width={args.width},height={args.height},framerate={args.framerate} ! '
        f'rtph264pay pt={args.pt} config-interval=1 ! '
        f'session.send_rtp_sink '
        f'rtpsession name=session '
        f'session.send_rtp_src ! udpsink host="{args.host}" port={args.rtp_port} sync=false async=false '
        f'session.send_rtcp_src ! udpsink host="{args.host}" port={args.rtcp_port} sync=false async=false'
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
                print("End of stream.")
                break
    except KeyboardInterrupt:
        print("\nInterrupted, stopping…")
    finally:
        pipeline.set_state(Gst.State.NULL)

if __name__ == "__main__":
    main()

