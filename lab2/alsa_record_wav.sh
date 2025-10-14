gst-launch-1.0 alsasrc device="default" num-buffers=1000 ! audio/x-raw,rate=16000,channels=1,width=16 ! queue  ! progressreport \
! audioconvert ! audioamplify amplification=2.0 \
! wavenc ! filesink location=../samples/webcam.wav

