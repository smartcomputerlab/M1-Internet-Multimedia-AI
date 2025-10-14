#!/usr/bin/env python3
# tcprecv.py - TCP server with host and port arguments

import socket
import sys
import argparse

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='TCP server')
    parser.add_argument('--host', default='127.0.0.1', help='Host address to bind to')
    parser.add_argument('--port', type=int, default=8888, help='Port to listen on')
    args = parser.parse_args()

    # Create TCP socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Allow reuse
    except socket.error as e:
        print(f"Socket creation error: {e}")
        sys.exit(1)

    # Bind socket
    try:
        s.bind((args.host, args.port))
        print(f"Bound to {args.host}:{args.port}")
    except socket.error as e:
        print(f"Bind error: {e}")
        s.close()
        sys.exit(1)

    # Listen for connections
    s.listen(5)  # Queue up to 5 connections
    print(f"Server listening on {args.host}:{args.port}...")

    try:
        while True:
            print("Waiting for incoming connections...")
            
            # Accept connection
            try:
                ns, client_addr = s.accept()
                print(f"Connection accepted from {client_addr[0]}:{client_addr[1]}")
            except socket.error as e:
                print(f"Accept failed: {e}")
                continue

            # Handle client connection
            try:
                while True:
                    # Receive data
                    data = ns.recv(512)  # BUFLEN = 512
                    if not data:
                        print("Client disconnected")
                        break
                    
                    # Remove null terminator if present
                    if data.endswith(b'\0'):
                        message = data[:-1].decode('utf-8', errors='replace')
                    else:
                        message = data.decode('utf-8', errors='replace')
                    
                    print(f"Got message {len(data)} bytes: {message}")
                    
                    # Check for session end
                    if message.startswith('.'):
                        print("Session ended by client")
                        break
                        
            except socket.error as e:
                print(f"Communication error: {e}")
            finally:
                ns.close()
                print("Client connection closed")
                
    except KeyboardInterrupt:
        print("\nServer shutting down...")
    finally:
        s.close()
        print("Server closed")

if __name__ == "__main__":
    main()

