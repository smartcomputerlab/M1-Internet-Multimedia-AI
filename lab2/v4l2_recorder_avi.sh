gst-launch-1.0  v4l2src device=/dev/video0 num-buffers=300 \
! video/x-raw, width=320,height=240,framerate=15/1 \
! videoconvert ! progressreport ! jpegenc ! avimux \
! filesink location=../samples/webcamconvjpeg.avi

