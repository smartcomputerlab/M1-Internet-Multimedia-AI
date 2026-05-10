#!/usr/bin/env python3
"""
Voice Assistant: whisper-talk-llama + Piper TTS
Equivalent to: build/bin/whisper-talk-llama -mw models/ggml-tiny.en.bin 
               -ml models/Llama-3.2-1B-Instruct-Q4_0.gguf -t 4 --speak ./speak 2>/dev/null
"""

import subprocess
import sys
import os

# --- Configuration ---
WHISPER_TALK_PATH = os.path.expanduser("~/whisper.cpp/build/bin/whisper-talk-llama")
WHISPER_MODEL = os.path.expanduser("~/whisper.cpp/models/ggml-tiny.en.bin")
LLAMA_MODEL = os.path.expanduser("~/whisper.cpp/models/Llama-3.2-1B-Instruct-Q4_0.gguf")
THREADS = 4

def run_voice_assistant():
    """Launch the complete voice assistant pipeline."""
    
    # Build the command exactly as you run it in the terminal
    cmd = [
        WHISPER_TALK_PATH,
        "-mw", WHISPER_MODEL,
        "-ml", LLAMA_MODEL,
        "-t", str(THREADS),
        "--speak", "./speak"
    ]
    
    print("🎤 Starting Voice Assistant")
    print("=" * 50)
    print(f"   Whisper model: {os.path.basename(WHISPER_MODEL)}")
    print(f"   Llama model:   {os.path.basename(LLAMA_MODEL)}")
    print(f"   CPU threads:   {THREADS}")
    print(f"   TTS engine:    Piper (female.onnx)")
    print("=" * 50)
    print("Speak into your microphone. The AI will respond with voice.")
    print("Press Ctrl+C to exit.\n")
    
    try:
        # Run the process
        # stderr=subprocess.DEVNULL silences warnings (equivalent to 2>/dev/null)
        process = subprocess.run(
            cmd,
            stderr=subprocess.DEVNULL,  # Hide ONNX Runtime warnings
            cwd=os.path.expanduser("~/whisper.cpp")  # Run from whisper.cpp directory
        )
        
        # Exit with the same code as the subprocess
        sys.exit(process.returncode)
        
    except KeyboardInterrupt:
        print("\n\n👋 Voice assistant stopped.")
        sys.exit(0)
        
    except FileNotFoundError:
        print(f"❌ ERROR: {WHISPER_TALK_PATH} not found!")
        print("   Make sure whisper-talk-llama is built correctly.")
        print("   Expected location: ~/whisper.cpp/build/bin/whisper-talk-llama")
        sys.exit(1)

if __name__ == "__main__":
    run_voice_assistant()

