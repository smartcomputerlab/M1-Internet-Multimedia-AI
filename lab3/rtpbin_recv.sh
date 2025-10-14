source config.sh
gst-launch-1.0 -v rtpbin name=rtpbin  \
     udpsrc caps="application/x-rtp, media=(string)video,clock-rate=(int)90000, encoding-name=(string)H264, encoding-params=(string)1" \
     port=$PORT_RTP_VIDEO ! rtpbin.recv_rtp_sink_0  \
     rtpbin. ! queue ! rtph264depay ! h264parse ! avdec_h264 ! queue ! videoconvert ! xvimagesink \
      udpsrc port=$PORT_RTCP_VIDEO ! rtpbin.recv_rtcp_sink_0   \
      rtpbin.send_rtcp_src_0 ! udpsink port=$PORT_RTCP_VIDEO_RET sync=false async=false   \
      udpsrc caps="application/x-rtp,media=(string)audio,clock-rate=(int)16000, encoding-name=(string)SPEEX, encoding-params=(string)1, payload=(int)110" \
      port=$PORT_RTP_AUDIO ! rtpbin.recv_rtp_sink_1  \
      rtpbin. !  queue ! rtpspeexdepay ! decodebin ! audioconvert ! alsasink \
      udpsrc port=$PORT_RTCP_AUDIO ! rtpbin.recv_rtcp_sink_1  \
      rtpbin.send_rtcp_src_1 ! udpsink port=$PORT_RTCP_AUDIO_RET sync=false async=false

