#!/usr/bin/env python3

import os
import sys
import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GLib

class RTPStreamer:
    def __init__(self):
        # Configuration
        self.CLIENT = "127.0.0.1"
        self.PORT_UDP_VIDEO = 5000    # UDP video stream
        self.PORT_RTP_VIDEO = 5000    # RTP-UDP video stream
        self.PORT_RTCP_VIDEO = 5001   # RTCP video stream
        self.PORT_UDP_AUDIO = 5002    # UDP audio stream
        self.PORT_RTP_AUDIO = 5002    # RTP-UDP audio stream
        self.PORT_RTCP_AUDIO = 5003   # RTCP audio stream
        self.PORT_RTCP_VIDEO_RET = 5005  # Return RTCP video stream
        self.PORT_RTCP_AUDIO_RET = 5007  # Return RTCP audio stream
        
        Gst.init(sys.argv)
        self.pipeline = None
        self.loop = GLib.MainLoop()
        
    def create_pipeline(self):
        # Build the pipeline string
        pipeline_str = f"""
            rtpbin name=rtpbin 
            
            # Video pipeline
            v4l2src device=/dev/video0 ! 
            video/x-h264, width=1920, height=1080, framerate=30/1 ! 
            rtph264pay ! 
            rtpbin.send_rtp_sink_0 
            
            rtpbin.send_rtp_src_0 ! 
            udpsink host={self.CLIENT} port={self.PORT_RTP_VIDEO} 
            
            rtpbin.send_rtcp_src_0 ! 
            udpsink host={self.CLIENT} port={self.PORT_RTCP_VIDEO} 
            sync=false async=false 
            
            udpsrc port={self.PORT_RTCP_VIDEO_RET} ! 
            rtpbin.recv_rtcp_sink_0 
            
            # Audio pipeline
            alsasrc device="default" ! 
            queue ! 
            audioconvert ! 
            audioresample ! 
            audio/x-raw, rate=16000, width=16, channels=1 ! 
            speexenc ! 
            rtpspeexpay ! 
            rtpbin.send_rtp_sink_1 
            
            rtpbin.send_rtp_src_1 ! 
            udpsink host={self.CLIENT} port={self.PORT_RTP_AUDIO} 
            
            rtpbin.send_rtcp_src_1 ! 
            udpsink host={self.CLIENT} port={self.PORT_RTCP_AUDIO} 
            sync=false async=false 
            
            udpsrc port={self.PORT_RTCP_AUDIO_RET} ! 
            rtpbin.recv_rtcp_sink_1
        """
        
        # Clean up the pipeline string
        pipeline_str = ' '.join(line.strip() for line in pipeline_str.split('\n') if line.strip())
        
        print("Creating pipeline with configuration:")
        print(f"Client: {self.CLIENT}")
        print(f"Video RTP Port: {self.PORT_RTP_VIDEO}")
        print(f"Video RTCP Port: {self.PORT_RTCP_VIDEO}")
        print(f"Audio RTP Port: {self.PORT_RTP_AUDIO}")
        print(f"Audio RTCP Port: {self.PORT_RTCP_AUDIO}")
        
        self.pipeline = Gst.parse_launch(pipeline_str)
        return self.pipeline is not None
    
    def on_message(self, bus, message):
        mtype = message.type
        if mtype == Gst.MessageType.EOS:
            print("End of stream")
            self.loop.quit()
        elif mtype == Gst.MessageType.ERROR:
            err, debug = message.parse_error()
            print(f"Error: {err}, {debug}")
            self.loop.quit()
        elif mtype == Gst.MessageType.STATE_CHANGED:
            old_state, new_state, pending_state = message.parse_state_changed()
            print(f"State changed: {old_state} -> {new_state}")
        return True
    
    def run(self):
        if not self.create_pipeline():
            print("Failed to create pipeline")
            return False
        
        # Set up message handling
        bus = self.pipeline.get_bus()
        bus.add_signal_watch()
        bus.connect("message", self.on_message)
        
        # Start the pipeline
        print("Starting pipeline...")
        self.pipeline.set_state(Gst.State.PLAYING)
        
        try:
            self.loop.run()
        except KeyboardInterrupt:
            print("Interrupted by user")
        
        # Clean up
        self.pipeline.set_state(Gst.State.NULL)
        return True

    def print_config(self):
        """Print the current configuration"""
        print("Current Configuration:")
        print(f"CLIENT={self.CLIENT}")
        print(f"PORT_UDP_VIDEO={self.PORT_UDP_VIDEO}   # UDP video stream")
        print(f"PORT_RTP_VIDEO={self.PORT_RTP_VIDEO}   # RTP-UDP video stream")
        print(f"PORT_RTCP_VIDEO={self.PORT_RTCP_VIDEO}  # RTCP video stream")
        print(f"PORT_UDP_AUDIO={self.PORT_UDP_AUDIO}   # UDP audio stream")
        print(f"PORT_RTP_AUDIO={self.PORT_RTP_AUDIO}   # RTP-UDP audio stream")
        print(f"PORT_RTCP_AUDIO={self.PORT_RTCP_AUDIO}  # RTCP audio stream")
        print(f"PORT_RTCP_VIDEO_RET={self.PORT_RTCP_VIDEO_RET} # Return RTCP video stream")
        print(f"PORT_RTCP_AUDIO_RET={self.PORT_RTCP_AUDIO_RET} # Return RTCP audio stream")

if __name__ == "__main__":
    streamer = RTPStreamer()
    streamer.print_config()
    print("\n" + "="*50 + "\n")
    
    if streamer.run():
        print("Pipeline executed successfully")
    else:
        print("Pipeline failed")
        sys.exit(1)

