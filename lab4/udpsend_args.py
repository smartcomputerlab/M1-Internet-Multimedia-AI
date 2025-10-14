#!/usr/bin/env python3
# udpsend_exact.py - Closer match to C behavior, no explicit bind()

import socket
import sys

BUFLEN = 512

def die(message):
    print(f"Error: {message}", file=sys.stderr)
    sys.exit(1)

def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <PORT> <REMOTE_ADDR>")
        sys.exit(1)

    # Parse arguments
    try:
        PORT = int(sys.argv[1])
    except ValueError:
        die("PORT must be an integer")

    REMOTE_ADDR = sys.argv[2]

    # Create UDP socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    except socket.error:
        die("socket")

    # Configure remote address
    remote_ip = REMOTE_ADDR
    remote_port = PORT
    remote_addr = (remote_ip, remote_port)

    print(f"Sending to {remote_addr}")

    # Keep sending data
    try:
        while True:
            print("write message:", end='', flush=True)

            buf = sys.stdin.readline().strip()
            if not buf:
                continue

            # Send data with null terminator
            try:
                data_to_send = buf.encode('utf-8')   # + b'\0'
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

