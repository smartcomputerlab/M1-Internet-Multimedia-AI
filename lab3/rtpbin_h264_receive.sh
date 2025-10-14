gst-launch-1.0 -v \
  rtpbin name=rtpbin latency=200                                             \
  udpsrc address=127.0.0.1 port=5000 \
    caps="application/x-rtp,media=video,encoding-name=H264,clock-rate=90000,payload=96" \
      ! rtpbin.recv_rtp_sink_0                                               \
  rtpbin.recv_rtp_src_0 ! rtph264depay ! h264parse ! avdec_h264 ! autovideosink sync=false \
  udpsrc address=127.0.0.1 port=5001 caps="application/x-rtcp" ! rtpbin.recv_rtcp_sink_0

