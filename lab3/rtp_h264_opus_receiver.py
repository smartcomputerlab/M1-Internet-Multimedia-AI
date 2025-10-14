#!/usr/bin/env python3
# rtp_av_receive.py
# Requires: GStreamer 1.0 + PyGObject (python3-gi)

import argparse
import sys
import gi

gi.require_version("Gst", "1.0")
from gi.repository import Gst

def main():
    parser = argparse.ArgumentParser(
        description="Receive RTP H.264 video and RTP Opus audio and play them."
    )
    # Video (RTP H.264)
    parser.add_argument("--video-port", type=int, default=9002, help="UDP port for RTP video")
    parser.add_argument("--video-clock", type=int, default=90000, help="RTP clock rate for video")
    parser.add_argument("--h264-encoding-params", default="1", help='H.264 encoding-params (e.g., "1")')
    parser.add_argument("--video-sink", default="xvimagesink", help="Video sink (e.g., xvimagesink, autovideosink)")
    parser.add_argument("--video-decoder", default="avdec_h264", help="H.264 decoder element (e.g., avdec_h264)")

    # Audio (RTP Opus)
    parser.add_argument("--audio-port", type=int, default=9004, help="UDP port for RTP audio")
    parser.add_argument("--opus-pt", type=int, default=97, help="RTP payload type for Opus")
    parser.add_argument("--opus-clock", type=int, default=48000, help="RTP clock rate for Opus")
    parser.add_argument("--audio-sink", default="autoaudiosink", help="Audio sink (e.g., autoaudiosink, alsasink)")
    parser.add_argument("--audio-sync", action="store_true", default=True, help="Keep audio sink synced (default on)")
    parser.add_argument("--no-audio-sync", dest="audio_sync", action="store_false", help="Disable audio sink sync")

    args = parser.parse_args()
    Gst.init(None)

    # Build caps strings
    caps_video = (
        f"application/x-rtp, media=(string)video, "
        f"clock-rate=(int){args.video_clock}, "
        f"encoding-name=(string)H264, encoding-params=(string){args.h264_encoding_params}"
    )
    caps_audio = (
        f"application/x-rtp, media=audio, encoding-name=OPUS, "
        f"payload={args.opus_pt}, clock-rate={args.opus_clock}"
    )

    pipeline_str = (
        # --- Video branch ---
        f'udpsrc port={args.video_port} caps="{caps_video}" ! '
        f'rtph264depay ! h264parse ! {args.video_decoder} ! queue ! videoconvert ! {args.video_sink} '
        # --- Audio branch ---
        f'udpsrc port={args.audio_port} caps="{caps_audio}" ! queue ! '
        f'rtpopusdepay ! opusdec ! audioconvert ! audioresample ! '
        f'{args.audio_sink} sync={"true" if args.audio_sync else "false"}'
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

