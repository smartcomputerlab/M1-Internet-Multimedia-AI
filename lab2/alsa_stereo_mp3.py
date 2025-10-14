#!/usr/bin/env python3
# record_stereo_mp3.py
# Requires: GStreamer 1.0 + PyGObject (python3-gi)

import argparse
import sys
import gi

gi.require_version("Gst", "1.0")
from gi.repository import Gst

def main():
    parser = argparse.ArgumentParser(
        description="Capture ALSA audio and save as MP3 via a simple GStreamer pipeline."
    )
    parser.add_argument("--device", default="default", help='ALSA device (e.g. "default" or "hw:0,0")')
    parser.add_argument("--format", default="S16LE", help="Sample format (e.g. S16LE)")
    parser.add_argument("--rate", type=int, default=44100, help="Sample rate (Hz)")
    parser.add_argument("--channels", type=int, default=2, help="Number of channels")
    parser.add_argument("--update-freq", type=int, default=1, help="progressreport update frequency (seconds)")
    parser.add_argument("--bitrate", type=int, default=192, help="MP3 bitrate (kbps)")
    parser.add_argument("--cbr", action="store_true", default=True, help="Use constant bitrate (default: on)")
    parser.add_argument("--vbr", dest="cbr", action="store_false", help="Use variable bitrate (turn off CBR)")
    parser.add_argument("--output", default="../samples/webcam_stereo.mp3", help="Output MP3 path")
    args = parser.parse_args()

    Gst.init(None)

    # Build the pipeline string
    pipeline_str = (
        f'alsasrc device="{args.device}" '
        f'! audio/x-raw,format={args.format},rate={args.rate},channels={args.channels} '
        f'! queue ! progressreport update-freq={args.update_freq} '
        f'! audioconvert ! audioresample '
        f'! lamemp3enc target=bitrate cbr={"true" if args.cbr else "false"} bitrate={args.bitrate} '
        f'! id3v2mux '
        f'! filesink location="{args.output}"'
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

