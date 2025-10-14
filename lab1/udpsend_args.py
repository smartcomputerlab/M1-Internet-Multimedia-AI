#!/usr/bin/env python3
# udpsend_exact.py - UDP sender with REMOTE_ADDR and PORT as arguments (no bind)

import socket
import sys

BUFLEN = 512
LOCAL_LOOP = "127.0.0.1"


def die(message):
    print(f"Error: {message}", file=sys.stderr)
    sys.exit(1)


def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <REMOTE_ADDR> <PORT>")
        sys.exit(1)

    REMOTE_ADDR = sys.argv[1]
    try:
        PORT = int(sys.argv[2])
    except ValueError:
        die("PORT must be an integer")

    # Create UDP socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    except socket.error:
        die("socket")

    # Configure remote address
    # For local testing, send to loopback at PORT+1
    if REMOTE_ADDR == "127.0.0.1" or REMOTE_ADDR.lower() == "localhost":
        remote_ip = LOCAL_LOOP
        remote_port = PORT + 1
    else:
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

            try:
                # Send data with null terminator (C-like behavior)
                data_to_send = buf.encode("utf-8") + b"\0"
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

