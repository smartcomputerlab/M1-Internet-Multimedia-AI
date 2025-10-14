#!/usr/bin/env python3
import serial
import sys
import paho.mqtt.client as mqtt

port = 1883
topic = "from/whisper"

def send_message(message, broker):
    try:
        client = mqtt.Client()
        client.connect(broker, port, 60)
        print(f"Publishing: {message} to topic: {topic}")
        client.publish(topic, message)
        client.disconnect()
        print("Message sent")
    except Exception as e:
        print(f"Failed to send. Error: {e}")

def filter_string(input_string):
    # pattern to find
    pattern = bytes.fromhex("201b5b324b0d20").decode('latin1')
    start_index = input_string.rfind(pattern)
    if start_index == -1:
        return ""
    return input_string[start_index + 7:]

def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <broker_host_or_ip>")
        sys.exit(1)

    broker = sys.argv[1]

    try:
        while True:
            user_input = input("")
            result = filter_string(user_input)
            print(result)

            if result.lower() == 'exit':
                print("Exiting program.")
                break

            # Only send if result is non-empty and doesn't start with '[' or '('
            if result and result[0:1] not in ("[", "("):
                send_message(result, broker)
                print("sent")
            else:
                print("not sent")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()

