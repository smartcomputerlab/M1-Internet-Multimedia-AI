gst-launch-1.0 rtpbin name=rtpbin \
v4l2src device=/dev/video0 ! video/x-h264, width=1280, height=720, framerate=30/1 ! rtph264pay ! rtpbin.send_rtp_sink_0 \
rtpbin.send_rtp_src_0 ! udpsink host=127.0.0.1 port=$PORT_RTP_VIDEO \
rtpbin.send_rtcp_src_0 ! udpsink host=127.0.0.1 port=$PORT_RTCP_VIDEO \
sync=false async=false \
udpsrc port=$PORT_RTCP_VIDEO_RET ! rtpbin.recv_rtcp_sink_0 \
alsasrc device="default" ! queue ! audioconvert ! audioresample ! audio/x-raw, rate=16000, width=16, channels=1 ! speexenc ! rtpspeexpay ! rtpbin.send_rtp_sink_1 \
rtpbin.send_rtp_src_1 ! udpsink host=127.0.0.1 port=$PORT_RTP_AUDIO \
rtpbin.send_rtcp_src_1 ! udpsink host=127.0.0.1 port=$PORT_RTCP_AUDIO \
sync=false async=false \
udpsrc port=$PORT_RTCP_AUDIO_RET ! rtpbin.recv_rtcp_sink_1

