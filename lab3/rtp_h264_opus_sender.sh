CLIENT="127.0.0.1"
gst-launch-1.0  v4l2src device=/dev/video0 ! video/x-h264, width=1280, height=720, framerate=30/1 !rtph264pay ! udpsink host=$CLIENT port=9002 \
  alsasrc device="default" ! audio/x-raw,rate=16000,channels=2 ! audioconvert ! opusenc ! queue ! rtpopuspay ! udpsink host=$CLIENT port=9004

