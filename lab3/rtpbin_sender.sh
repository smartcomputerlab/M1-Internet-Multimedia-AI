# Sends to receiver ports 5000/5001 (video) and 5002/5003 (audio);
# listens for receiver RTCP back on 5005 (video) and 5007 (audio).
gst-launch-1.0 -v \
  rtpbin name=rtpbin latency=200                                                 \
  v4l2src device=/dev/video0 ! \
    video/x-h264,width=1280,height=720,framerate=30/1 ! \
    h264parse config-interval=-1 ! rtph264pay pt=96 config-interval=1 ! \
    rtpbin.send_rtp_sink_0                                                       \
  rtpbin.send_rtp_src_0  ! udpsink host=127.0.0.1 port=5000 sync=false async=false \
  rtpbin.send_rtcp_src_0 ! udpsink host=127.0.0.1 port=5001 sync=false async=false \
  udpsrc address=127.0.0.1 port=5005 caps="application/x-rtcp" ! rtpbin.recv_rtcp_sink_0 \
  alsasrc device=default ! audio/x-raw,rate=48000,channels=2 ! \
    audioconvert ! audioresample ! opusenc bitrate=64000 inband-fec=true ! \
    rtpopuspay pt=111 ! rtpbin.send_rtp_sink_1                                    \
  rtpbin.send_rtp_src_1  ! udpsink host=127.0.0.1 port=5002 sync=false async=false \
  rtpbin.send_rtcp_src_1 ! udpsink host=127.0.0.1 port=5003 sync=false async=false \
  udpsrc address=127.0.0.1 port=5007 caps="application/x-rtcp" ! rtpbin.recv_rtcp_sink_1

