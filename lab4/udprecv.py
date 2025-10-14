#!/usr/bin/env python3
# udprecv_exact.py - Closer match to C behavior

import socket
import sys

BUFLEN = 512
PORT = 8889
LOCAL_LOOP = "127.0.0.1"
LOCAL_IP = "192.168.2.2"

def die(message):
    print(f"Error: {message}", file=sys.stderr)
    sys.exit(1)

def main():
    # Create UDP socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    except socket.error:
        die("socket")
    
    # Configure socket to use specific local address (not INADDR_ANY)
    local_ip = LOCAL_IP
    local_port = PORT
    
    # Bind socket
    try:
        s.bind((local_ip, local_port))
        print(f"Bound to {local_ip}:{local_port}")
    except socket.error:
        die("bind")
    
    print("Waiting for data...")
    
    # Keep listening for data
    try:
        while True:
            # Receive data (blocking call)
            try:
                data, addr = s.recvfrom(BUFLEN)
            except socket.error:
                die("recvfrom()")
            
            # Print client details
            client_ip, client_port = addr
            print(f"IP, port {client_ip}:{client_port}")
            
            # Process received data
            # Handle null terminator like C strings
            null_pos = data.find(b'\0')
            if null_pos != -1:
                # Extract data up to null terminator
                message_data = data[:null_pos]
            else:
                message_data = data
            
            try:
                message = message_data.decode('utf-8')
                print(f"Received data: {message}")
            except UnicodeDecodeError:
                print(f"Received data (raw): {data.hex()}")
                
    except KeyboardInterrupt:
        print("\nServer shutdown.")
    finally:
        s.close()

if __name__ == "__main__":
    main()

