./rtp_rtcp_video.py --mode recv \
  --bind 127.0.0.1 --peer 127.0.0.1 \
  --rtp-port 5000 --rtcp-port 5001 --rtcp-back-port 5005 --pt 96
[GStreamer ERROR] gst-stream-error-quark: Internal data stream error. (1)
../libs/gst/base/gstbasesrc.c(3177): gst_base_src_loop (): /GstPipeline:pipeline0/GstUDPSrc:udpsrc0:
streaming stopped, reason not-linked (-1)
#!/usr/bin/env python3
# rtp_rtcp_video.py
# Requires: GStreamer 1.0 + PyGObject (python3-gi) and plugins (good/ugly/libav)

import argparse
import sys
import gi

gi.require_version("Gst", "1.0")
from gi.repository import Gst

def die(msg):
    print(msg, file=sys.stderr)
    sys.exit(1)

def make(factory, name=None):
    e = Gst.ElementFactory.make(factory, name or factory)
    if not e:
        die(f"Failed to create element: {factory}")
    return e

def run_pipeline(pipeline: Gst.Pipeline):
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

def build_sender(args) -> Gst.Pipeline:
    """
    Webcam (H.264) -> rtpbin -> RTP to peer (rtp_port), RTCP to peer (rtcp_port)
                         ^                                    |
                         |----------- RTCP from peer (rtcp_back_port)
    """
    Gst.init(None)
    pipe = Gst.Pipeline.new("sender")

    # Elements
    rtpbin = make("rtpbin", "rtpbin")
    rtpbin.set_property("latency", args.latency)

    vsrc = make("v4l2src", "v4l2src")
    vsrc.set_property("device", args.video_device)
    vsrc.set_property("do-timestamp", True)

    capsfilter = make("capsfilter", "v_caps")
    caps = Gst.Caps.from_string(
        f"video/x-h264,width={args.width},height={args.height},framerate={args.framerate}"
    )
    capsfilter.set_property("caps", caps)

    h264parse = make("h264parse", "h264parse")
    h264parse.set_property("config-interval", -1)  # push SPS/PPS downstream

    pay = make("rtph264pay", "pay")
    pay.set_property("pt", args.pt)
    pay.set_property("config-interval", 1)  # send SPS/PPS with each IDR
    # (optional) pay.set_property("mtu", 1200)

    rtp_udpsink = make("udpsink", "rtp_out")
    rtp_udpsink.set_property("host", args.peer)
    rtp_udpsink.set_property("port", args.rtp_port)
    rtp_udpsink.set_property("sync", False)
    rtp_udpsink.set_property("async", False)

    rtcp_udpsink = make("udpsink", "rtcp_out")
    rtcp_udpsink.set_property("host", args.peer)
    rtcp_udpsink.set_property("port", args.rtcp_port)
    rtcp_udpsink.set_property("sync", False)
    rtcp_udpsink.set_property("async", False)

    rtcp_udpsrc_back = make("udpsrc", "rtcp_in")
    rtcp_udpsrc_back.set_property("port", args.rtcp_back_port)
    # Bind address is optional; uncomment if you need to bind to loopback only:
    # rtcp_udpsrc_back.set_property("address", args.bind)
    rtcp_udpsrc_back.set_property("caps", Gst.Caps.from_string("application/x-rtcp"))

    # Add & link linear parts
    for e in [rtpbin, vsrc, capsfilter, h264parse, pay, rtp_udpsink, rtcp_udpsink, rtcp_udpsrc_back]:
        pipe.add(e)

    if not vsrc.link(capsfilter):
        die("Failed to link v4l2src -> capsfilter")
    if not capsfilter.link(h264parse):
        die("Failed to link capsfilter -> h264parse")
    if not h264parse.link(pay):
        die("Failed to link h264parse -> rtph264pay")

    # Request pads & link to rtpbin
    send_rtp_sink = rtpbin.get_request_pad("send_rtp_sink_0")
    if not send_rtp_sink:
        die("Could not get rtpbin.send_rtp_sink_0")
    if pay.get_static_pad("src").link(send_rtp_sink) != Gst.PadLinkReturn.OK:
        die("Failed to link pay.src -> rtpbin.send_rtp_sink_0")

    # rtpbin.send_rtp_src_0 -> udpsink (RTP out)
    send_rtp_src = rtpbin.get_request_pad("send_rtp_src_0")
    if not send_rtp_src:
        die("Could not get rtpbin.send_rtp_src_0")
    if send_rtp_src.link(rtp_udpsink.get_static_pad("sink")) != Gst.PadLinkReturn.OK:
        die("Failed to link rtpbin.send_rtp_src_0 -> rtp_udpsink.sink")

    # rtpbin.send_rtcp_src_0 -> udpsink (RTCP out)
    send_rtcp_src = rtpbin.get_request_pad("send_rtcp_src_0")
    if not send_rtcp_src:
        die("Could not get rtpbin.send_rtcp_src_0")
    if send_rtcp_src.link(rtcp_udpsink.get_static_pad("sink")) != Gst.PadLinkReturn.OK:
        die("Failed to link rtpbin.send_rtcp_src_0 -> rtcp_udpsink.sink")

    # udpsrc (RTCP back) -> rtpbin.recv_rtcp_sink_0
    recv_rtcp_sink = rtpbin.get_request_pad("recv_rtcp_sink_0")
    if not recv_rtcp_sink:
        die("Could not get rtpbin.recv_rtcp_sink_0")
    if rtcp_udpsrc_back.get_static_pad("src").link(recv_rtcp_sink) != Gst.PadLinkReturn.OK:
        die("Failed to link rtcp_udpsrc_back.src -> rtpbin.recv_rtcp_sink_0")

    return pipe

def build_receiver(args) -> Gst.Pipeline:
    """
    rtpbin <- RTP from sender (rtp_port), <- RTCP from sender (rtcp_port)
      |-> depay -> parse -> decode -> display
    rtpbin --(send RTCP)--> udpsink to sender (rtcp_back_port)
    """
    Gst.init(None)
    pipe = Gst.Pipeline.new("receiver")

    rtpbin = make("rtpbin", "rtpbin")
    rtpbin.set_property("latency", args.latency)
    rtpbin.set_property("do-lost", True)

    rtp_udpsrc = make("udpsrc", "rtp_in")
    rtp_udpsrc.set_property("port", args.rtp_port)
    # rtp_udpsrc.set_property("address", args.bind)  # optional bind IP
    rtp_caps = Gst.Caps.from_string(
        f"application/x-rtp,media=video,encoding-name=H264,clock-rate=90000,payload={args.pt}"
    )
    rtp_udpsrc.set_property("caps", rtp_caps)

    rtcp_udpsrc = make("udpsrc", "rtcp_in")
    rtcp_udpsrc.set_property("port", args.rtcp_port)
    rtcp_udpsrc.set_property("caps", Gst.Caps.from_string("application/x-rtcp"))

    rtcp_udpsink_back = make("udpsink", "rtcp_back")
    rtcp_udpsink_back.set_property("host", args.peer)
    rtcp_udpsink_back.set_property("port", args.rtcp_back_port)
    rtcp_udpsink_back.set_property("sync", False)
    rtcp_udpsink_back.set_property("async", False)

    depay = make("rtph264depay", "depay")
    h264parse = make("h264parse", "h264parse")
    decoder = make("avdec_h264", "decoder")  # or openh264dec
    conv = make("videoconvert", "conv")
    sink = make("autovideosink", "vsink")
    sink.set_property("sync", False)

    for e in [rtpbin, rtp_udpsrc, rtcp_udpsrc, rtcp_udpsink_back, depay, h264parse, decoder, conv, sink]:
        pipe.add(e)

    # Link RTP udpsrc -> rtpbin.recv_rtp_sink_0 (request pad)
    recv_rtp_sink = rtpbin.get_request_pad("recv_rtp_sink_0")
    if not recv_rtp_sink:
        die("Could not get rtpbin.recv_rtp_sink_0")
    if rtp_udpsrc.get_static_pad("src").link(recv_rtp_sink) != Gst.PadLinkReturn.OK:
        die("Failed to link rtp_udpsrc.src -> rtpbin.recv_rtp_sink_0")

    # Link rtpbin.recv_rtp_src_0 -> depay
    recv_rtp_src = rtpbin.get_request_pad("recv_rtp_src_0")
    if not recv_rtp_src:
        die("Could not get rtpbin.recv_rtp_src_0")
    if recv_rtp_src.link(depay.get_static_pad("sink")) != Gst.PadLinkReturn.OK:
        die("Failed to link rtpbin.recv_rtp_src_0 -> depay.sink")

    # Decode chain
    if not depay.link(h264parse):
        die("Failed to link depay -> h264parse")
    if not h264parse.link(decoder):
        die("Failed to link h264parse -> decoder")
    if not decoder.link(conv):
        die("Failed to link decoder -> videoconvert")
    if not conv.link(sink):
        die("Failed to link videoconvert -> sink")

    # RTCP in -> rtpbin.recv_rtcp_sink_0
    recv_rtcp_sink = rtpbin.get_request_pad("recv_rtcp_sink_0")
    if not recv_rtcp_sink:
        die("Could not get rtpbin.recv_rtcp_sink_0")
    if rtcp_udpsrc.get_static_pad("src").link(recv_rtcp_sink) != Gst.PadLinkReturn.OK:
        die("Failed to link rtcp_udpsrc.src -> rtpbin.recv_rtcp_sink_0")

    # rtpbin.send_rtcp_src_0 -> udpsink back to sender
    send_rtcp_src = rtpbin.get_request_pad("send_rtcp_src_0")
    if not send_rtcp_src:
        die("Could not get rtpbin.send_rtcp_src_0")
    if send_rtcp_src.link(rtcp_udpsink_back.get_static_pad("sink")) != Gst.PadLinkReturn.OK:
        die("Failed to link rtpbin.send_rtcp_src_0 -> rtcp_udpsink_back.sink")

    return pipe

def main():
    ap = argparse.ArgumentParser(
        description="Send/Receive H.264 over RTP/RTCP using rtpbin (webcam capture)."
    )
    ap.add_argument("--mode", choices=["send", "recv"], required=True,
                    help="'send' to capture & send; 'recv' to receive & display")
    ap.add_argument("--peer", default="127.0.0.1", help="Remote peer IP/host")
    ap.add_argument("--bind", default="127.0.0.1", help="Local bind IP (optional)")
    ap.add_argument("--rtp-port", type=int, default=5000, help="RTP port (video)")
    ap.add_argument("--rtcp-port", type=int, default=5001, help="RTCP port from peer")
    ap.add_argument("--rtcp-back-port", type=int, default=5005,
                    help="RTCP port on peer to receive our RTCP")
    ap.add_argument("--pt", type=int, default=96, help="RTP payload type (H.264)")
    ap.add_argument("--latency", type=int, default=300, help="rtpbin jitterbuffer latency (ms)")

    # Sender-only capture settings
    ap.add_argument("--video-device", default="/dev/video0", help="V4L2 webcam (sender)")
    ap.add_argument("--width", type=int, default=1280)
    ap.add_argument("--height", type=int, default=720)
    ap.add_argument("--framerate", default="30/1", help='e.g. "30/1"')

    args = ap.parse_args()
    Gst.init(None)

    if args.mode == "send":
        pipeline = build_sender(args)
    else:
        pipeline = build_receiver(args)

    run_pipeline(pipeline)

if __name__ == "__main__":
    main()

