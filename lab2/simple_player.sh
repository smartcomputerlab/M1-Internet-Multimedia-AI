gst-launch-1.0  filesrc location=../samples/bunny.mp4 ! qtdemux name=foo \
foo.video_0 ! queue ! decodebin ! videoconvert ! ximagesink \
foo.audio_0 ! queue ! decodebin ! audioconvert ! alsasink
