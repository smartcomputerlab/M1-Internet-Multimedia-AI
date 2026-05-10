#!/usr/bin/env python3
"""
Simple wrapper for whisper-talk-llama
Just launches the working command and passes through all input/output
"""

import subprocess
import sys
import os

# --- Configuration ---
WHISPER_MODEL = os.path.expanduser("~/whisper.cpp/models/ggml-tiny.en.bin")
LLAMA_MODEL = os.path.expanduser("~/whisper.cpp/models/Llama-3.2-1B-Instruct-Q4_0.gguf")
WHISPER_TALK_PATH = os.path.expanduser("~/whisper.cpp/build/bin/whisper-talk-llama")
THREADS = 4

def run_whisper_talk():
    """Launch whisper-talk-llama with both models loaded."""
    
    cmd = [
        WHISPER_TALK_PATH,
        "-mw", WHISPER_MODEL,
        "-ml", LLAMA_MODEL,
        "-t", str(THREADS)
    ]
    
    print("🎤 Starting voice assistant...")
    print(f"   Whisper: {WHISPER_MODEL}")
    print(f"   Llama:   {LLAMA_MODEL}")
    print("-" * 50)
    print("Speak into your microphone. Press Ctrl+C to exit.\n")
    
    try:
        # Launch the process, sharing terminal with user
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except FileNotFoundError:
        print(f"ERROR: {WHISPER_TALK_PATH} not found!")
        sys.exit(1)

if __name__ == "__main__":
    run_whisper_talk()

