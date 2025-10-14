gst-launch-1.0 udpsrc port=8050 caps="application/x-rtp, media=(string)video, clock-rate=(int)90000, encoding-name=(string)H264, encoding-params=(string)1" ! \
rtph264depay ! h264parse ! avdec_h264 ! queue ! videoconvert ! xvimagesink

