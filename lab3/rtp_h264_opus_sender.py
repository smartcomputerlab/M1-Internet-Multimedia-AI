#!/usr/bin/env python3
# rtp_av_send.py
# Requires: GStreamer 1.0 + PyGObject (python3-gi)

import argparse
import sys
import gi

gi.require_version("Gst", "1.0")
from gi.repository import Gst

def main():
    parser = argparse.ArgumentParser(
        description="Send H.264 video and Opus audio as separate RTP streams over UDP."
    )
    # Destinations
    parser.add_argument("--host", default="127.0.0.1", help="Destination IP/host")
    parser.add_argument("--video-port", type=int, default=9002, help="RTP port for video")
    parser.add_argument("--audio-port", type=int, default=9004, help="RTP port for audio")

    # Video
    parser.add_argument("--video-device", default="/dev/video0", help="V4L2 device")
    parser.add_argument("--width", type=int, default=1280, help="Video width")
    parser.add_argument("--height", type=int, default=720, help="Video height")
    parser.add_argument("--framerate", default="30/1", help='Framerate as fraction, e.g. "30/1"')
    parser.add_argument("--h264-pt", type=int, default=96, help="RTP payload type for H.264")

    # Audio
    parser.add_argument("--audio-device", default="default", help='ALSA device (e.g. "default", "hw:0,0")')
    parser.add_argument("--rate", type=int, default=16000, help="Audio sample rate (Hz)")
    parser.add_argument("--channels", type=int, default=2, help="Audio channels")
    parser.add_argument("--opus-pt", type=int, default=97, help="RTP payload type for Opus")
    parser.add_argument("--opus-bitrate", type=int, default=64000, help="Opus bitrate (bps)")

    args = parser.parse_args()
    Gst.init(None)

    pipeline_str = (
        # Video branch
        f'v4l2src device="{args.video_device}" ! '
        f'video/x-h264,width={args.width},height={args.height},framerate={args.framerate} ! '
        f'rtph264pay pt={args.h264_pt} config-interval=1 ! '
        f'udpsink host="{args.host}" port={args.video_port} sync=false async=false '
        # Audio branch
        f'alsasrc device="{args.audio_device}" ! '
        f'audio/x-raw,rate={args.rate},channels={args.channels} ! '
        f'audioconvert ! opusenc bitrate={args.opus_bitrate} ! queue ! '
        f'rtpopuspay pt={args.opus_pt} ! '
        f'udpsink host="{args.host}" port={args.audio_port} sync=false async=false'
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

