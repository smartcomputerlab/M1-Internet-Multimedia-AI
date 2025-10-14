gst-launch-1.0 v4l2src device=/dev/video0 \
! queue ! video/x-h264,width=1280,height=720, framerate=30/1 \
! h264parse ! queue ! matroskamux \
! filesink location=../samples/webcam.video_h264.mkv

