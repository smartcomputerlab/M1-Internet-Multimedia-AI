gst-launch-1.0 v4l2src device=/dev/video0 \
! video/x-h264, width=1280,height=720, framerate=30/1 \
! h264parse ! openh264dec ! videoconvert ! xvimagesink

