#!/usr/bin/env python3
"""
Voice Assistant: whisper-talk-llama + Piper TTS
Equivalent to: build/bin/whisper-talk-llama -mw models/ggml-tiny.en.bin 
               -ml models/Llama-3.2-1B-Instruct-Q4_0.gguf -t 4 --speak ./speak 2>/dev/null

Usage:
    python3 voice_assistant.py
    python3 voice_assistant.py --whisper ggml-base.en.bin
    python3 voice_assistant.py --llama Llama-3.2-3B.Q4_0.gguf --threads 8
    python3 voice_assistant.py -w ggml-small.en.bin -l Qwen2.5-3B.Q4_0.gguf -t 6
"""

import subprocess
import sys
import os
import argparse

# --- Default Configuration ---
WHISPER_TALK_PATH = os.path.expanduser("~/whisper.cpp/build/bin/whisper-talk-llama")
DEFAULT_WHISPER_MODEL = "ggml-tiny.en.bin"
DEFAULT_LLAMA_MODEL = "Llama-3.2-1B-Instruct-Q4_0.gguf"
DEFAULT_THREADS = 4
MODELS_DIR = os.path.expanduser("~/whisper.cpp/models")

def parse_arguments():
    """Parse command-line arguments."""
    
    parser = argparse.ArgumentParser(
        description="Voice Assistant with Whisper + Llama + Piper TTS",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s
  %(prog)s --whisper ggml-base.en.bin
  %(prog)s --llama Llama-3.2-3B.Q4_0.gguf --threads 8
  %(prog)s -w ggml-small.en.bin -l Qwen2.5-3B.Q4_0.gguf -t 6
        """
    )
    
    parser.add_argument(
        "-w", "--whisper",
        type=str,
        default=DEFAULT_WHISPER_MODEL,
        help=f"Whisper model filename (default: {DEFAULT_WHISPER_MODEL})"
    )
    
    parser.add_argument(
        "-l", "--llama",
        type=str,
        default=DEFAULT_LLAMA_MODEL,
        help=f"Llama model filename (default: {DEFAULT_LLAMA_MODEL})"
    )
    
    parser.add_argument(
        "-t", "--threads",
        type=int,
        default=DEFAULT_THREADS,
        help=f"Number of CPU threads (default: {DEFAULT_THREADS})"
    )
    
    parser.add_argument(
        "--list-models",
        action="store_true",
        help="List available models in the models directory and exit"
    )
    
    return parser.parse_args()

def list_available_models():
    """Display available Whisper and Llama models in the models directory."""
    
    print(f"\n📁 Models directory: {MODELS_DIR}")
    print("=" * 60)
    
    if not os.path.exists(MODELS_DIR):
        print("❌ Models directory not found!")
        return
    
    # List all model files
    models = sorted(os.listdir(MODELS_DIR))
    
    whisper_models = [m for m in models if m.startswith("ggml-") and m.endswith(".bin")]
    llama_models = [m for m in models if m.endswith(".gguf")]
    other_files = [m for m in models if m not in whisper_models and m not in llama_models]
    
    if whisper_models:
        print("\n🎤 Whisper Models (use with --whisper):")
        for model in whisper_models:
            size_mb = os.path.getsize(os.path.join(MODELS_DIR, model)) / (1024 * 1024)
            print(f"   {model} ({size_mb:.1f} MB)")
    
    if llama_models:
        print("\n🧠 Llama Models (use with --llama):")
        for model in llama_models:
            size_gb = os.path.getsize(os.path.join(MODELS_DIR, model)) / (1024 * 1024 * 1024)
            print(f"   {model} ({size_gb:.2f} GB)")
    
    if other_files:
        print("\n📄 Other files:")
        for f in other_files:
            print(f"   {f}")
    
    print("\n💡 Usage examples:")
    print(f"   python3 {sys.argv[0]} --whisper {whisper_models[0] if whisper_models else 'ggml-tiny.en.bin'}")
    print(f"   python3 {sys.argv[0]} --llama {llama_models[0] if llama_models else 'model.gguf'}")
    print(f"   python3 {sys.argv[0]} -w {whisper_models[1] if len(whisper_models) > 1 else 'model.bin'} -t 8")

def resolve_model_path(filename):
    """Resolve a model filename to its full path."""
    
    # If it's already an absolute path, use it directly
    if os.path.isabs(filename):
        if os.path.exists(filename):
            return filename
        else:
            print(f"❌ Model not found: {filename}")
            sys.exit(1)
    
    # Check in models directory
    model_path = os.path.join(MODELS_DIR, filename)
    if os.path.exists(model_path):
        return model_path
    
    # Check in current directory
    if os.path.exists(filename):
        return os.path.abspath(filename)
    
    print(f"❌ Model '{filename}' not found in:")
    print(f"   - Current directory: {os.path.abspath(filename)}")
    print(f"   - Models directory: {model_path}")
    print(f"\n💡 Tip: Use --list-models to see available models")
    sys.exit(1)

def run_voice_assistant(whisper_model, llama_model, threads):
    """Launch the complete voice assistant pipeline."""
    
    whisper_path = resolve_model_path(whisper_model)
    llama_path = resolve_model_path(llama_model)
    
    # Build the command
    cmd = [
        WHISPER_TALK_PATH,
        "-mw", whisper_path,
        "-ml", llama_path,
        "-t", str(threads),
        "--speak", "./speak"
    ]
    
    print("\n🎤 Starting Voice Assistant")
    print("=" * 60)
    print(f"   Whisper model: {os.path.basename(whisper_path)}")
    print(f"   Llama model:   {os.path.basename(llama_path)}")
    print(f"   CPU threads:   {threads}")
    print(f"   TTS engine:    Piper (female.onnx)")
    print("=" * 60)
    print("Speak into your microphone. The AI will respond with voice.")
    print("Press Ctrl+C to exit.\n")
    
    try:
        process = subprocess.run(
            cmd,
            stderr=subprocess.DEVNULL,  # Hide ONNX Runtime warnings (2>/dev/null)
            cwd=os.path.expanduser("~/whisper.cpp")
        )
        
        sys.exit(process.returncode)
        
    except KeyboardInterrupt:
        print("\n\n👋 Voice assistant stopped.")
        sys.exit(0)
        
    except FileNotFoundError:
        print(f"❌ ERROR: {WHISPER_TALK_PATH} not found!")
        print("   Make sure whisper-talk-llama is built correctly.")
        print(f"   Expected location: {WHISPER_TALK_PATH}")
        sys.exit(1)

def main():
    """Main entry point."""
    
    args = parse_arguments()
    
    # Handle --list-models flag
    if args.list_models:
        list_available_models()
        sys.exit(0)
    
    # Validate thread count
    if args.threads < 1:
        print("❌ Thread count must be at least 1")
        sys.exit(1)
    
    if args.threads > 16:
        print("⚠️  Warning: High thread count may cause performance issues")
    
    # Run the voice assistant
    run_voice_assistant(args.whisper, args.llama, args.threads)

if __name__ == "__main__":
    main()

