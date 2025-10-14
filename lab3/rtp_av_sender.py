#!/usr/bin/env python3
# rtp_av_sender_fixed.py
# Requires: GStreamer 1.0 + PyGObject (python3-gi) and the relevant plugins.

import argparse
import sys
import gi

gi.require_version("Gst", "1.0")
from gi.repository import Gst

def main():
    p = argparse.ArgumentParser(
        description="Send H.264 (video) + Speex (audio) via rtpbin (RTP/RTCP)."
    )

    # --- Defaults from your config.sh ---
    p.add_argument("--host", default="127.0.0.1", help="Destination host/IP (CLIENT)")
    p.add_argument("--video-rtp-port", type=int, default=5000, help="PORT_RTP_VIDEO")
    p.add_argument("--video-rtcp-port", type=int, default=5001, help="PORT_RTCP_VIDEO")
    p.add_argument("--audio-rtp-port", type=int, default=5002, help="PORT_RTP_AUDIO")
    p.add_argument("--audio-rtcp-port", type=int, default=5003, help="PORT_RTCP_AUDIO")
    p.add_argument("--video-rtcp-ret", type=int, default=5005, help="PORT_RTCP_VIDEO_RET (listen here)")
    p.add_argument("--audio-rtcp-ret", type=int, default=5007, help="PORT_RTCP_AUDIO_RET (listen here)")
    p.add_argument("--bind-address", default="127.0.0.1", help="Local bind address for RTCP udpsrc")

    # --- rtpbin / general ---
    p.add_argument("--rtpbin-latency", type=int, default=300, help="rtpbin jitterbuffer latency (ms)")

    # --- Video source/caps ---
    p.add_argument("--video-device", default="/dev/video0", help="V4L2 video device")
    p.add_argument("--width", type=int, default=1920)
    p.add_argument("--height", type=int, default=1080)
    p.add_argument("--framerate", default="30/1", help='e.g. "30/1"')
    p.add_argument("--h264-pt", type=int, default=96, help="RTP payload type for H.264")

    # --- Audio source/caps (Speex) ---
    p.add_argument("--audio-device", default="default", help='ALSA device (e.g., "default", "hw:0,0")')
    p.add_argument("--rate", type=int, default=16000, help="Audio sample rate (Hz)")
    p.add_argument("--channels", type=int, default=1, help="Audio channels (1=mono)")
    p.add_argument("--speex-pt", type=int, default=97, help="RTP payload type for Speex")

    args = p.parse_args()
    Gst.init(None)

    # Notes to avoid frozen image:
    # - do-timestamp=true : ensure upstream timestamps exist
    # - h264parse config-interval=-1 : push SPS/PPS downstream
    # - video/x-h264,stream-format=byte-stream,alignment=au : friendly to payloader/decoder
    # - rtph264pay config-interval=1 : send SPS/PPS with every IDR
    # - queues around critical points to decouple threads

    pipeline_str = (
        f'rtpbin name=rtpbin latency={args.rtpbin_latency} '

        # -------- VIDEO (H.264) --------
        f'v4l2src device="{args.video_device}" do-timestamp=true ! queue ! '
        f'video/x-h264,width={args.width},height={args.height},framerate={args.framerate} ! '
        f'h264parse config-interval=-1 ! '
        f'video/x-h264,stream-format=byte-stream,alignment=au ! queue ! '
        f'rtph264pay pt={args.h264_pt} config-interval=1 ! '
        f'rtpbin.send_rtp_sink_0 '
        f'rtpbin.send_rtp_src_0  ! udpsink host="{args.host}" port={args.video_rtp_port} sync=false async=false '
        f'rtpbin.send_rtcp_src_0 ! udpsink host="{args.host}" port={args.video_rtcp_port} sync=false async=false '
        f'udpsrc address="{args.bind_address}" port={args.video_rtcp_ret} caps="application/x-rtcp" ! rtpbin.recv_rtcp_sink_0 '

        # -------- AUDIO (Speex) --------
        f'alsasrc device="{args.audio_device}" ! queue ! '
        f'audioconvert ! audioresample ! '
        f'audio/x-raw,rate={args.rate},channels={args.channels},format=S16LE ! '
        f'speexenc ! rtpspeexpay pt={args.speex_pt} ! '
        f'rtpbin.send_rtp_sink_1 '
        f'rtpbin.send_rtp_src_1  ! udpsink host="{args.host}" port={args.audio_rtp_port} sync=false async=false '
        f'rtpbin.send_rtcp_src_1 ! udpsink host="{args.host}" port={args.audio_rtcp_port} sync=false async=false '
        f'udpsrc address="{args.bind_address}" port={args.audio_rtcp_ret} caps="application/x-rtcp" ! rtpbin.recv_rtcp_sink_1 '
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
                err, dbg = msg.parse_error()
                print(f"[GStreamer ERROR] {err}", file=sys.stderr)
                if dbg:
                    print(dbg, file=sys.stderr)
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

