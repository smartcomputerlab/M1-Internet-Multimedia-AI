#!/usr/bin/python3
import socket
import serial, tempfile, os
import subprocess
import sys

def receive_udp_message(port):
    try:
        # Create a UDP socket
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Bind the socket to the given port
        udp_socket.bind(("", port))
        print(f"Listening for UDP messages on port {port}...")
        # Receive a message
        data, addr = udp_socket.recvfrom(1024)  # Buffer size is 1024 bytes
        print("Received message: " + str(data))
        udp_socket.close()
        return str(data)

    except Exception as e:
        print(f"Error receiving UDP message: {e}")

# Function for when a message is received
def echo_udp_message(msg):
    try:
        msg = msg + "\n"
        print(f"Received message: {msg}")
        with tempfile.NamedTemporaryFile(delete=False, mode='w', prefix='mqtt_', suffix='.txt') as temp_file:
            temp_file.write(msg)
            print(f"Message written to temporary file: {temp_file.name}")

        with open(temp_file.name, 'r') as file:
            file_content = file.read()
            print(f"Read from temporary file: {file_content}")
            os.remove(temp_file.name)
            os.system(f'echo "{file_content}"')

    except Exception as e:
        print(f"Error handling message: {e}")

def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <port>")
        sys.exit(1)

    try:
        target_port = int(sys.argv[1])
    except ValueError:
        print("Error: Port must be an integer.")
        sys.exit(1)

    # Start receiving messages
    while True:
        message = receive_udp_message(target_port)
        echo_udp_message(message)

if __name__ == "__main__":
    main()

