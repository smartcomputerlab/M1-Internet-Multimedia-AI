#!/usr/bin/env python3
# rtp_h264_rtcp_receiver.py
# Requires: GStreamer 1.0 + PyGObject (python3-gi)

import argparse
import sys
import gi

gi.require_version("Gst", "1.0")
from gi.repository import Gst

def main():
    parser = argparse.ArgumentParser(
        description="Receive H.264 over RTP with RTCP using an rtpsession and display it."
    )
    # Ports
    parser.add_argument("--rtp-port", type=int, default=8050, help="UDP port for RTP video (default: 8050)")
    parser.add_argument("--rtcp-port", type=int, default=8051, help="UDP port for RTCP (default: 8051)")

    # RTP caps
    parser.add_argument("--clock-rate", type=int, default=90000, help="RTP clock rate for H.264 (default: 90000)")
    parser.add_argument("--encoding-params", default="1", help='H.264 encoding-params (default: "1")')
    parser.add_argument("--pt", type=int, help="Optional RTP payload type to match (e.g., 96)")

    # Decode / sink
    parser.add_argument("--decoder", default="openh264dec",
                        help='H.264 decoder element (e.g., "openh264dec", "avdec_h264")')
    parser.add_argument("--video-sink", default="xvimagesink",
                        help='Video sink (e.g., "xvimagesink", "autovideosink")')

    args = parser.parse_args()
    Gst.init(None)

    # Build the RTP caps string
    caps_video = (
        f"application/x-rtp, media=(string)video, "
        f"clock-rate=(int){args.clock_rate}, "
        f"encoding-name=(string)H264, encoding-params=(string){args.encoding_params}"
    )
    if args.pt is not None:
        caps_video += f", payload=(int){args.pt}"

    pipeline_str = (
        # --- RTP video in -> rtpsession -> depay/decode/display ---
        f'udpsrc port={args.rtp_port} caps="{caps_video}" ! '
        f'.recv_rtp_sink rtpsession name=session .recv_rtp_src ! '
        f'rtph264depay ! h264parse ! {args.decoder} ! queue ! videoconvert ! {args.video_sink} '
        # --- RTCP in to the same session ---
        f'udpsrc port={args.rtcp_port} caps="application/x-rtcp" ! session.recv_rtcp_sink'
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
        print("\nInterrupted, stopping...")
    finally:
        pipeline.set_state(Gst.State.NULL)

if __name__ == "__main__":
    main()

