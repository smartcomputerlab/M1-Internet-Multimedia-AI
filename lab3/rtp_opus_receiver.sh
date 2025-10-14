gst-launch-1.0 -v \
    udpsrc port=8060 caps="application/x-rtp, media=audio, encoding-name=OPUS, payload=97" ! \
    rtpopusdepay ! opusdec ! audioconvert ! audioresample ! autoaudiosink sync=false
