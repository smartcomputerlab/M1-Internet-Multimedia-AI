#!/usr/bin/env python3
# rtp_speex_send.py
# Requires: GStreamer 1.0 + PyGObject (python3-gi)

import argparse
import sys
import gi

gi.require_version("Gst", "1.0")
from gi.repository import Gst

def main():
    parser = argparse.ArgumentParser(
        description="Send ALSA audio as RTP/Speex over UDP (GStreamer)."
    )
    parser.add_argument("--host", default="127.0.0.1", help="Destination host/IP")
    parser.add_argument("--port", type=int, default=8060, help="Destination UDP port")
    parser.add_argument("--device", default="default", help='ALSA device (e.g., "default", "hw:0,0")')
    parser.add_argument("--rate", type=int, default=16000, help="Sample rate (Hz)")
    parser.add_argument("--channels", type=int, default=2, help="Number of channels")
    parser.add_argument("--pt", type=int, help="RTP payload type (dynamic), e.g., 110")
    args = parser.parse_args()

    Gst.init(None)

    # Build the pipeline string that mirrors your gst-launch command
    pay_props = f" pt={args.pt}" if args.pt is not None else ""
    pipeline_str = (
        f'alsasrc device="{args.device}" '
        f'! audio/x-raw,rate={args.rate},channels={args.channels} '
        f'! audioconvert ! speexenc '
        f'! queue ! rtpspeexpay{pay_props} '
        f'! udpsink host="{args.host}" port={args.port} sync=false async=false'
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

