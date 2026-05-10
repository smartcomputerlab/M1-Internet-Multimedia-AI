#!/usr/bin/env python3
import subprocess
import socket
import argparse
import signal
import sys
import re
import random
import time
from datetime import datetime
# Paho MQTT client is required: pip install paho-mqtt
from paho.mqtt import client as mqtt_client
# --- Configuration ---
DEFAULT_MQTT_BROKER = "broker.emqx.io"  # Free public MQTT broker 
DEFAULT_MQTT_PORT = 1883
DEFAULT_TOPIC = "whisper/transcription"

def clean_transcription(text):
    # Remove IP addresses in brackets: [192.168.1.100]
    text = re.sub(r'\[\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\]', '', text)
    # Remove [BLANK_AUDIO] tag
    text = re.sub(r'\[BLANK_AUDIO\]', '', text, flags=re.IGNORECASE)
    # Remove action descriptions in brackets: [Sighs], [Laughs], [Music], etc.
    text = re.sub(r'\[[A-Za-z\s]+\]', '', text)
    # Remove parenthetical comments like (dramatic music), (applause), etc.
    text = re.sub(r'\([^)]*\)', '', text)
    # Remove any remaining empty brackets
    text = re.sub(r'\[\]', '', text)
    # Clean up extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def connect_mqtt(broker, port, client_id):
    # Callback when client connects to broker 
    def on_connect(client, userdata, flags, reason_code, properties):
        if reason_code == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n" % reason_code)

    client = mqtt_client.Client(
        callback_api_version=mqtt_client.CallbackAPIVersion.VERSION2,
        client_id=client_id
    )
    client.on_connect = on_connect
    client.connect(broker, port)
    return client

def main():
    parser = argparse.ArgumentParser(description="Send whisper.cpp transcriptions via MQTT")
    parser.add_argument("--broker", default=DEFAULT_MQTT_BROKER,
                        help="MQTT broker address (default: %(default)s)")
    parser.add_argument("--port", type=int, default=DEFAULT_MQTT_PORT,
                        help="MQTT broker port (default: %(default)s)")
    parser.add_argument("--topic", default=DEFAULT_TOPIC,
                        help="MQTT topic to publish to (default: %(default)s)")
    parser.add_argument("--model", default="./models/ggml-tiny.en.bin",
                        help="Whisper model path")
    parser.add_argument("--threads", "-t", type=int, default=6,
                        help="Number of threads")
    parser.add_argument("--step", type=int, default=2048,
                        help="Step size in ms")
    parser.add_argument("--length", type=int, default=2048,
                        help="Audio length in ms")
    parser.add_argument("--whisper-path", default="./build/bin/whisper-stream",
                        help="Path to whisper-stream executable")
    parser.add_argument("--no-filter", action="store_true",
                        help="Disable content filtering (send raw output)")
    args = parser.parse_args()

    # Generate a random client ID for MQTT connection
    client_id = f'whisper-mqtt-{random.randint(0, 1000)}'

    print("=" * 60)
    print("Whisper MQTT Sender")
    print("   MQTT Broker: " + args.broker + ":" + str(args.port))
    print("   Topic: " + args.topic)
    print("   Model: " + args.model)
    print("   Threads: " + str(args.threads))
    print("   Step/Length: " + str(args.step) + "ms / " + str(args.length) + "ms")
    print("   Filtering: " + ("Disabled" if args.no_filter else "Enabled"))
    print("=" * 60)

    # Connect to MQTT broker
    print("\nConnecting to MQTT broker...")
    mqtt_client_obj = connect_mqtt(args.broker, args.port, client_id)
    mqtt_client_obj.loop_start()

    # Whisper-stream command
    cmd = [
        args.whisper_path,
        "-m", args.model,
        "-t", str(args.threads),
        "--step", str(args.step),
        "--length", str(args.length)
    ]

    print("Running: " + " ".join(cmd) + "\n")
    # Flag to track if cleanup has already run
    cleanup_done = [False]
    # Cleanup handler
    def cleanup(signum, frame):
        if cleanup_done[0]:
            return
        cleanup_done[0] = True
        print("\nStopping...")
        if process and process.poll() is None:
            process.terminate()
        mqtt_client_obj.loop_stop()
        mqtt_client_obj.disconnect()
        sys.exit(0)

    signal.signal(signal.SIGINT, cleanup)
    signal.signal(signal.SIGTERM, cleanup)
    # Launch whisper-stream
    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            bufsize=1
        )
    except FileNotFoundError:
        print("Error: '" + args.whisper_path + "' not found. Build whisper.cpp with SDL2 support first.")
        mqtt_client_obj.loop_stop()
        mqtt_client_obj.disconnect()
        sys.exit(1)

    print("Listening... Speak into the microphone (Ctrl+C to stop)\n")
    # Read lines, filter, display locally, and publish via MQTT
    for line in process.stdout:
        line = line.strip()
        if line:
            # Strip ANSI escape codes
            line = re.sub(r'\x1b\[[0-9;]*[a-zA-Z]', '', line)
            # Apply filters (unless disabled)
            if args.no_filter:
                clean_line = line
            else:
                clean_line = clean_transcription(line)
            # Only print and send if there's content after filtering
            if clean_line:
                timestamp = datetime.now().strftime("%H:%M:%S")
                # Show both raw and filtered in terminal
                if line != clean_line:
                    print("  [" + timestamp + "] Raw: " + line)
                    print("  [" + timestamp + "] Filtered: " + clean_line)
                else:
                    print("  [" + timestamp + "] " + clean_line)
                # Publish the filtered version via MQTT
                result = mqtt_client_obj.publish(args.topic, clean_line)
                status = result[0]
                if status != 0:
                    print("  [" + timestamp + "] Failed to send message to MQTT topic " + args.topic)

    cleanup(None, None)

if __name__ == "__main__":
    main()

