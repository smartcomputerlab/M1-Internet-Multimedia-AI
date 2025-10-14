#!/usr/bin/env python3
# simple_capture.py
# Requires: GStreamer 1.0 + PyGObject (python3-gi)

import argparse
import sys
import gi

gi.require_version("Gst", "1.0")
from gi.repository import Gst

def main():
    parser = argparse.ArgumentParser(
        description="Record from ALSA to WAV via a simple GStreamer pipeline."
    )
    parser.add_argument("--device", default="default", help='ALSA device (e.g. "default" or "hw:0,0")')
    parser.add_argument("--num-buffers", type=int, default=1000, help="Stop after this many buffers")
    parser.add_argument("--rate", type=int, default=16000, help="Sample rate (Hz)")
    parser.add_argument("--channels", type=int, default=1, help="Number of channels")
    parser.add_argument("--width", type=int, default=16, help="Sample width (bits) — matches your original pipeline")
    parser.add_argument("--amplification", type=float, default=2.0, help="Gain factor for audioamplify")
    parser.add_argument("--output", default="../samples/webcam.wav", help="Output WAV path")
    args = parser.parse_args()

    Gst.init(None)

    pipeline_str = (
        f'alsasrc device="{args.device}" num-buffers={args.num_buffers} '
        f'! audio/x-raw,rate={args.rate},channels={args.channels},width={args.width} '
        f'! queue ! progressreport ! audioconvert '
        f'! audioamplify amplification={args.amplification} '
        f'! wavenc ! filesink location="{args.output}"'
    )

    pipeline = Gst.parse_launch(pipeline_str)
    bus = pipeline.get_bus()

    pipeline.set_state(Gst.State.PLAYING)
    try:
        while True:
            msg = bus.timed_pop_filtered(
                Gst.SECOND,
                Gst.MessageType.ERROR | Gst.MessageType.EOS | Gst.MessageType.STATE_CHANGED
            )
            if not msg:
                continue
            t = msg.type
            if t == Gst.MessageType.ERROR:
                err, debug = msg.parse_error()
                print(f"ERROR: {err}", file=sys.stderr)
                if debug:
                    print(debug, file=sys.stderr)
                break
            if t == Gst.MessageType.EOS:
                print("Done (EOS).")
                break
    except KeyboardInterrupt:
        print("\nInterrupted, stopping...")
    finally:
        pipeline.set_state(Gst.State.NULL)

if __name__ == "__main__":
    main()

