#!/usr/bin/env python3
"""
whisper_udp_receiver.py
Receives UDP datagrams from whisper_udp_sender.py, prints the message,
and speaks it aloud using Piper TTS.
"""

import socket
import argparse
import signal
import sys
import subprocess
import os
from datetime import datetime

def main():
    parser = argparse.ArgumentParser(description="Receive whisper transcriptions via UDP and speak them with Piper")
    parser.add_argument("--port", type=int, default=9999, help="Port to listen on")
    parser.add_argument("--show-ip", action="store_true",
                        help="Show sender IP address with each message")
    parser.add_argument("--show-timestamp", action="store_true",
                        help="Show local timestamp with each message")
    parser.add_argument("--piper-model", default="models/female.onnx",
                        help="Piper TTS model file path")
    parser.add_argument("--no-speak", action="store_true",
                        help="Disable text-to-speech output (print only)")
    parser.add_argument("--quiet", action="store_true",
                        help="Suppress Piper ONNX runtime warnings")
    args = parser.parse_args()

    # Verify piper is installed
    if not args.no_speak:
        if not os.path.exists(args.piper_model):
            print(f"⚠️  Warning: Piper model '{args.piper_model}' not found.")
            print("   Download it first or use --no-speak to disable TTS.")
            print("   Continuing in print-only mode...\n")
            args.no_speak = True
        else:
            # Check if piper command is available
            try:
                subprocess.run(["piper", "--help"], capture_output=True, check=True)
            except (subprocess.CalledProcessError, FileNotFoundError):
                print("⚠️  Warning: 'piper' command not found. Install piper-tts first.")
                print("   Continuing in print-only mode...\n")
                args.no_speak = True

    # Create and bind UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("0.0.0.0", args.port))

    def cleanup(signum, frame):
        print("\nStopping receiver...")
        sock.close()
        sys.exit(0)

    signal.signal(signal.SIGINT, cleanup)
    signal.signal(signal.SIGTERM, cleanup)

    print(f"🎧 Listening for transcriptions on port {args.port}... (Ctrl+C to stop)")
    if not args.no_speak:
        print(f"🔊 Speaking with Piper model: {args.piper_model}")
    print("-" * 60)

    while True:
        try:
            data, addr = sock.recvfrom(65535)
            text = data.decode("utf-8")
            # Skip empty messages
            if not text.strip():
                continue

            # Build the output line based on options
            output_parts = []
            if args.show_timestamp:
                output_parts.append(f"[{datetime.now().strftime('%H:%M:%S')}]")
            if args.show_ip:
                output_parts.append(f"[{addr[0]}]")
            output_parts.append(text)
            # Print the message
            print(" ".join(output_parts))
            # Speak the message with Piper (unless disabled)
            if not args.no_speak:
                try:
                    # Build the piper command
                    piper_cmd = ["piper", "--model", args.piper_model, "--output-raw"]
                    # Suppress stderr to hide ONNX runtime warnings
                    stderr_target = subprocess.DEVNULL if args.quiet else None
                    # Run piper and pipe to aplay for audio output
                    piper_process = subprocess.Popen(
                        piper_cmd,
                        stdin=subprocess.PIPE,
                        stdout=subprocess.PIPE,
                        stderr=stderr_target
                    )
                    aplay_process = subprocess.Popen(
                        ["aplay", "-r", "16000", "-f", "S16_LE", "-t", "raw", "-c", "1"],
                        stdin=piper_process.stdout,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL
                    )
                    # Send the text to piper
                    piper_process.stdin.write(text.encode("utf-8"))
                    piper_process.stdin.close()
                    # Wait for both processes to finish
                    piper_process.wait()
                    aplay_process.wait()
                except Exception as e:
                    print(f"  ⚠️  TTS error: {e}")

        except Exception as e:
            print(f"Error: {e}")
            break

if __name__ == "__main__":
    main()

