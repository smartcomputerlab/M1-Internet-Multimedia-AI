#!/usr/bin/env python3
# rtp_speex_recv.py
# Requires: GStreamer 1.0 + PyGObject (python3-gi)

import argparse
import sys
import gi

gi.require_version("Gst", "1.0")
from gi.repository import Gst

def main():
    parser = argparse.ArgumentParser(
        description="Receive RTP/Speex over UDP and play it (GStreamer)."
    )
    parser.add_argument("--port", type=int, default=8060, help="UDP port to listen on (default: 5002)")
    parser.add_argument("--payload", type=int, default=97, help="RTP payload type for Speex (default: 97)")
    parser.add_argument("--clock-rate", type=int, default=16000, help="RTP clock rate (Hz) (default: 16000)")
    parser.add_argument("--sink", default="autoaudiosink", help="Audio sink (e.g., autoaudiosink, alsasink)")
    args = parser.parse_args()

    Gst.init(None)

    # Build caps (note: use args.clock_rate, not args.clock-rate)
    caps = (
        f"application/x-rtp, media=audio, encoding-name=SPEEX, "
        f"payload={args.payload}, clock-rate={args.clock_rate}"
    )

    pipeline_str = (
        f'udpsrc port={args.port} caps="{caps}" ! '
        f'rtpspeexdepay ! speexdec ! audioconvert ! audioresample ! '
        f'{args.sink} sync=false'
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

