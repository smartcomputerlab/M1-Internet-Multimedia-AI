gst-launch-1.0 v4l2src device=/dev/video0 ! queue ! video/x-h264,width=1280,height=720,framerate=30/1 ! h264parse ! queue ! mux. \
        alsasrc device="default" ! audio/x-raw,channels=2,rate=16000 ! audioconvert ! queue ! lamemp3enc ! queue ! mux. matroskamux name=mux ! queue ! filesink location='../samples/webcammux.mkv'

