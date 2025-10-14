gst-launch-1.0 -v \
    udpsrc port=8060 caps="application/x-rtp, media=audio, encoding-name=SPEEX, payload=97" ! \
    rtpspeexdepay ! speexdec ! audioconvert ! audioresample ! autoaudiosink sync=false
