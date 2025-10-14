#!/usr/bin/env python3
# udpsend_exact.py - Closer match to C behavior

import socket
import sys

BUFLEN = 512
PORT = 8888
REMOTE_ADDR = "127.0.0.1"
LOCAL_LOOP = "127.0.0.1"

def die(message):
    print(f"Error: {message}", file=sys.stderr)
    sys.exit(1)

def main():
    # Create UDP socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    except socket.error:
        die("socket")
    
    # Configure local address (optional binding)
    local_ip = LOCAL_LOOP
    local_port = PORT
    
    # Configure remote address
    remote_ip = LOCAL_LOOP  # Using local loop as in C comments
    remote_port = PORT + 1  # Using PORT+1 for local operation
    
    # Alternative configurations (commented out):
    # remote_ip = REMOTE_ADDR    # For remote operation
    # remote_port = PORT         # For remote operation
    # remote_ip = '0.0.0.0'      # Equivalent to INADDR_ANY
    
    # Bind socket (optional)
    try:
        s.bind((local_ip, local_port))
        print(f"Bound to {local_ip}:{local_port}")
    except socket.error:
        die("bind")
    
    remote_addr = (remote_ip, remote_port)
    print(f"Sending to {remote_addr}")
    
    # Keep sending data
    try:
        while True:
            print("write message:", end='', flush=True)
            
            # Read input (equivalent to scanf)
            buf = sys.stdin.readline().strip()
            if not buf:
                continue
            
            # Send data with null terminator
            try:
                # Include null terminator like C's strlen(buf)+1
                data_to_send = buf.encode('utf-8') + b'\0'
                bytes_sent = s.sendto(data_to_send, remote_addr)
                print(f"Sent {bytes_sent} bytes")
            except socket.error:
                die("sendto()")
                
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        s.close()

if __name__ == "__main__":
    main()

