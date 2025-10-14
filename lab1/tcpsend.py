#!/usr/bin/env python3
# tcpsend.py - Simple TCP client

import socket
import sys
import time
import argparse

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Simple TCP client')
    parser.add_argument('--host', default='127.0.0.1', help='Server host address')
    parser.add_argument('--port', type=int, default=8888, help='Server port')
    args = parser.parse_args()

    # Create TCP socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error as e:
        print(f"Socket creation error: {e}")
        sys.exit(1)

    # Connect to server
    try:
        s.connect((args.host, args.port))
        print(f"Connected to {args.host}:{args.port}")
    except socket.error as e:
        print(f"Connection error: {e}")
        s.close()
        sys.exit(1)

    # Communication loop
    try:
        while True:
            print("write the message, replace spaces by _, end session with . message")
            message = input().strip()
            
            if not message:
                continue
                
            # Send message with null terminator (like C version)
            try:
                s.sendall((message + '\0').encode())
            except socket.error as e:
                print(f"Send error: {e}")
                break
            
            # Check if session should end
            if message.startswith('.'):
                print("Ending session...")
                break
                
            time.sleep(3)  # Wait 3 seconds like C version
            
    except KeyboardInterrupt:
        print("\nSession interrupted by user")
    except EOFError:
        print("\nEnd of input")
    finally:
        s.close()
        print("Connection closed")

if __name__ == "__main__":
    main()

