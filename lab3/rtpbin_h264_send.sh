gst-launch-1.0 -v \
  rtpbin name=rtpbin latency=200                                              \
  videotestsrc is-live=true ! \
    x264enc tune=zerolatency speed-preset=veryfast bitrate=1500 key-int-max=30 ! \
    h264parse config-interval=-1 ! rtph264pay pt=96 config-interval=1 ! \
    rtpbin.send_rtp_sink_0                                                    \
  rtpbin.send_rtp_src_0  ! udpsink host=127.0.0.1 port=5000 sync=false async=false \
  rtpbin.send_rtcp_src_0 ! udpsink host=127.0.0.1 port=5001 sync=false async=false

