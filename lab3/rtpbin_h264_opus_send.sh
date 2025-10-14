gst-launch-1.0 \
rtpbin name=rtpbin \
! \
v4l2src device=/dev/video0 ! video/x-raw,width=640,height=480,framerate=30/1 ! \
videoconvert ! \
x264enc tune=zerolatency bitrate=500 speed-preset=ultrafast ! \
video/x-h264,profile=baseline ! \
rtph264pay pt=96 ! \
rtpbin.send_rtp_sink_0 \
rtpbin.send_rtp_src_0 ! \
udpsink host=127.0.0.1 port=5000 \
rtpbin.send_rtcp_src_0 ! \
udpsink host=127.0.0.1 port=5001 sync=false async=false \
! \
# Audio pipeline (Opus from default audio source)
alsasrc device="default" ! \
audioconvert ! \
audioresample ! \
opusenc bitrate=64000 ! \
rtpopuspay pt=97 ! \
rtpbin.send_rtp_sink_1 \
rtpbin.send_rtp_src_1 ! \
udpsink host=127.0.0.1 port=5002 \
rtpbin.send_rtcp_src_1 ! \
udpsink host=127.0.0.1 port=5003 sync=false async=false

