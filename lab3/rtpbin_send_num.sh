gst-launch-1.0 rtpbin name=rtpbin \
v4l2src device=/dev/video0 ! video/x-h264, width=1920, height=1080, framerate=30/1 ! rtph264pay ! rtpbin.send_rtp_sink_0 \
rtpbin.send_rtp_src_0 ! udpsink host="127.0.0.1" port=5000 \
rtpbin.send_rtcp_src_0 ! udpsink host="127.0.0.1" port=5001 \
sync=false async=false \
udpsrc port=5005 ! rtpbin.recv_rtcp_sink_0 \
alsasrc device="default" ! queue ! audioconvert ! audioresample ! audio/x-raw, rate=16000, width=16, channels=1 ! speexenc ! rtpspeexpay ! rtpbin.send_rtp_sink_1 \
rtpbin.send_rtp_src_1 ! udpsink host="127.0.0.1" port=5002 \
rtpbin.send_rtcp_src_1 ! udpsink host="127.0.0.1" port=5003 \
sync=false async=false \
udpsrc port=5007 ! rtpbin.recv_rtcp_sink_1

