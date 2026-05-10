#!/usr/bin/env python3
"""
whisper_udp_sender.py
Captures text from whisper-stream and sends each line as a UDP datagram.
Includes filters for unwanted content.
"""

import subprocess
import socket
import argparse
import signal
import sys
import re
from datetime import datetime

def clean_transcription(text):
    """Remove unwanted elements from transcription text."""
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

def main():
    parser = argparse.ArgumentParser(description="Send whisper.cpp transcriptions via UDP")
    parser.add_argument("--host", required=True, help="Destination IP address")
    parser.add_argument("--port", type=int, required=True, help="Destination port")
    parser.add_argument("--model", default="./models/ggml-tiny.en.bin", help="Whisper model path")
    parser.add_argument("--threads", "-t", type=int, default=6, help="Number of threads")
    parser.add_argument("--step", type=int, default=2048, help="Step size in ms")
    parser.add_argument("--length", type=int, default=2048, help="Audio length in ms")
    parser.add_argument("--whisper-path", default="./build/bin/whisper-stream",
                        help="Path to whisper-stream executable")
    parser.add_argument("--no-filter", action="store_true",
                        help="Disable content filtering (send raw output)")
    args = parser.parse_args()

    # Create UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    dest = (args.host, args.port)

    print("=" * 60)
    print(f"🎤 Whisper UDP Sender")
    print(f"   Destination: {args.host}:{args.port}")
    print(f"   Model: {args.model}")
    print(f"   Threads: {args.threads}")
    print(f"   Step/Length: {args.step}ms / {args.length}ms")
    print(f"   Filtering: {'Disabled' if args.no_filter else 'Enabled'}")
    print("=" * 60)

    # Whisper-stream command
    cmd = [
        args.whisper_path,
        "-m", args.model,
        "-t", str(args.threads),
        "--step", str(args.step),
        "--length", str(args.length)
    ]

    print(f"\nRunning: {' '.join(cmd)}\n")

    # Cleanup handler
    def cleanup(signum, frame):
        print("\nStopping...")
        if process and process.poll() is None:
            process.terminate()
        sock.close()
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
        print(f"Error: '{args.whisper_path}' not found. Build whisper.cpp with SDL2 support first.")
        sys.exit(1)

    print("🎙️   Listening... Speak into the microphone (Ctrl+C to stop)\n")

    # Read lines, filter, display locally, and send as UDP
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
                    print(f"  [{timestamp}] 🔴 Raw: {line}")
                    print(f"  [{timestamp}] 🟢 Filtered: {clean_line}")
                else:
                    print(f"  [{timestamp}] 📝 {clean_line}")

                # Send the filtered version via UDP
                sock.sendto(clean_line.encode("utf-8"), dest)

    cleanup(None, None)

if __name__ == "__main__":
    main()

