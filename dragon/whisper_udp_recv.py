#!/usr/bin/env python3
"""
whisper_udp_receiver.py
Receives UDP datagrams from whisper_udp_sender.py and prints only the message.
"""

import socket
import argparse
import signal
import sys
from datetime import datetime

def main():
    parser = argparse.ArgumentParser(description="Receive whisper transcriptions via UDP")
    parser.add_argument("--port", type=int, default=9999, help="Port to listen on")
    parser.add_argument("--show-ip", action="store_true", 
                        help="Show sender IP address with each message")
    parser.add_argument("--show-timestamp", action="store_true",
                        help="Show local timestamp with each message")
    args = parser.parse_args()

    # Create and bind UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("0.0.0.0", args.port))

    def cleanup(signum, frame):
        print("\nStopping receiver...")
        sock.close()
        sys.exit(0)

    signal.signal(signal.SIGINT, cleanup)
    signal.signal(signal.SIGTERM, cleanup)

    print(f"🎧 Listening for transcriptions on port {args.port}... (Ctrl+C to stop)")
    print("-" * 60)

    while True:
        try:
            data, addr = sock.recvfrom(65535)
            text = data.decode("utf-8")
            
            # Build the output line based on options
            output_parts = []
            
            if args.show_timestamp:
                output_parts.append(f"[{datetime.now().strftime('%H:%M:%S')}]")
            
            if args.show_ip:
                output_parts.append(f"[{addr[0]}]")
            
            output_parts.append(text)
            
            # Print the message
            print(" ".join(output_parts))
            
        except Exception as e:
            print(f"Error: {e}")
            break

if __name__ == "__main__":
    main()

