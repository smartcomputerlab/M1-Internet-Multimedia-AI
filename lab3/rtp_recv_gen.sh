V_RTP=5000 V_RTCP=5001 A_RTP=5002 A_RTCP=5003 V_BACK=5005 A_BACK=5007
gst-launch-1.0 -v \
  rtpbin name=rtpbin latency=300 do-lost=true                                      \
  udpsrc address=127.0.0.1 port=$V_RTP  \
    caps="application/x-rtp,media=video,encoding-name=H264,clock-rate=90000,payload=96" \
      ! rtpbin.recv_rtp_sink_0                                                    \
  rtpbin.recv_rtp_src_0 ! rtph264depay ! h264parse ! avdec_h264 ! videoconvert ! autovideosink sync=false \
  udpsrc address=127.0.0.1 port=$V_RTCP caps="application/x-rtcp" ! rtpbin.recv_rtcp_sink_0               \
  rtpbin.send_rtcp_src_0 ! udpsink host=127.0.0.1 port=$V_BACK sync=false async=false                     \
  udpsrc address=127.0.0.1 port=$A_RTP  \
    caps="application/x-rtp,media=audio,encoding-name=Speex,clock-rate=16000,payload=97" \
      ! rtpbin.recv_rtp_sink_1                                                    \
  rtpbin.recv_rtp_src_1 ! rtpspeexdepay ! speexdec ! audioconvert ! audioresample ! autoaudiosink \
  udpsrc address=127.0.0.1 port=$A_RTCP caps="application/x-rtcp" ! rtpbin.recv_rtcp_sink_1               \
  rtpbin.send_rtcp_src_1 ! udpsink host=127.0.0.1 port=$A_BACK sync=false async=false

