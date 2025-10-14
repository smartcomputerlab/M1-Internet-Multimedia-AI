gst-launch-1.0 \
  alsasrc device=default \
  ! audio/x-raw,format=S16LE,rate=44100,channels=2 \
  ! queue ! progressreport update-freq=1 \
  ! audioconvert ! audioresample \
  ! lamemp3enc target=bitrate cbr=true bitrate=192 \
  ! id3v2mux \
  ! filesink location=../samples/webcam_stereo.mp3

