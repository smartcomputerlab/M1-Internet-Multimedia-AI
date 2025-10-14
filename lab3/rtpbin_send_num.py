#!/usr/bin/env python3
# rtpbin_sender_av.py
# Requires: GStreamer 1.0 + PyGObject (python3-gi)

import argparse
import sys
import gi

gi.require_version("Gst", "1.0")
from gi.repository import Gst

def main():
    parser = argparse.ArgumentParser(
        description="Send H.264 video + Speex audio over RTP/UDP using rtpbin."
    )
    # Dest host and ports (defaults = your example)
    parser.add_argument("--host", default="127.0.0.1", help="Destination host/IP")
    parser.add_argument("--video-rtp-port",  type=int, default=5000)
    parser.add_argument("--video-rtcp-port", type=int, default=5001)
    parser.add_argument("--video-rtcp-ret",  type=int, default=5005)
    parser.add_argument("--audio-rtp-port",  type=int, default=5002)
    parser.add_argument("--audio-rtcp-port", type=int, default=5003)
    parser.add_argument("--audio-rtcp-ret",  type=int, default=5007)

    # Video source/caps
    parser.add_argument("--video-device", default="/dev/video0")
    parser.add_argument("--width",  type=int, default=1920)
    parser.add_argument("--height", type=int, default=1080)
    parser.add_argument("--framerate", default="30/1")
    parser.add_argument("--h264-pt", type=int, default=96, help="RTP payload type for H.264")

    # Audio source/caps (Speex)
    parser.add_argument("--audio-device", default="default")
    parser.add_argument("--rate",     type=int, default=16000)
    parser.add_argument("--channels", type=int, default=1)
    parser.add_argument("--speex-pt", type=int, default=97, help="RTP payload type for Speex")

    # rtpbin options
    parser.add_argument("--rtpbin-latency", type=int, default=200)

    args = parser.parse_args()
    Gst.init(None)

    # Pipeline string (kept close to your gst-launch; adds minor robustness)
    pipeline_str = (
        f'rtpbin name=rtpbin latency={args.rtpbin_latency} '

        # --- Video branch (H.264) ---
        f'v4l2src device="{args.video_device}" do-timestamp=true ! '
        f'video/x-h264,width={args.width},height={args.height},framerate={args.framerate} ! '
        f'rtph264pay pt={args.h264_pt} config-interval=1 ! '
        f'rtpbin.send_rtp_sink_0 '
        f'rtpbin.send_rtp_src_0  ! udpsink host="{args.host}" port={args.video_rtp_port} sync=false async=false '
        f'rtpbin.send_rtcp_src_0 ! udpsink host="{args.host}" port={args.video_rtcp_port} sync=false async=false '
        f'udpsrc port={args.video_rtcp_ret} caps="application/x-rtcp" ! rtpbin.recv_rtcp_sink_0 '

        # --- Audio branch (Speex) ---
        f'alsasrc device="{args.audio_device}" ! queue ! '
        f'audioconvert ! audioresample ! '
        f'audio/x-raw,rate={args.rate},width=16,channels={args.channels} ! '
        f'speexenc ! rtpspeexpay pt={args.speex_pt} ! '
        f'rtpbin.send_rtp_sink_1 '
        f'rtpbin.send_rtp_src_1  ! udpsink host="{args.host}" port={args.audio_rtp_port} sync=false async=false '
        f'rtpbin.send_rtcp_src_1 ! udpsink host="{args.host}" port={args.audio_rtcp_port} sync=false async=false '
        f'udpsrc port={args.audio_rtcp_ret} caps="application/x-rtcp" ! rtpbin.recv_rtcp_sink_1 '
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
                print(f"[GStreamer ERROR] {err}", file=sys.stderr)
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

