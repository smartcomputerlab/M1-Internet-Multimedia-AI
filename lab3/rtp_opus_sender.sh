CLIENT="127.0.0.1"
PORT_RTP_AUDIO=8060
gst-launch-1.0 -v alsasrc device="default" ! audio/x-raw,rate=16000,channels=2 ! audioconvert ! opusenc ! queue ! rtpopuspay ! udpsink host=$CLIENT port=$PORT_RTP_AUDIO
