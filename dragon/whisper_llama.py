import subprocess
import sys

# --- Configuration ---
# !!IMPORTANT: Replace these with your actual model paths and preferred flags!!
WHISPER_MODEL = "/home/rock/whisper.cpp/models/ggml-tiny.en.bin"
LLAMA_MODEL =   "/home/rock/whisper.cpp/models/Llama-3.2-1B-Instruct-Q4_0.gguf" # or your specific model
# ---------------------

def run_talk_pipeline():
    # Step 1: Launch whisper-talk-llama
    # The '-f' flag tells it to output text to stdout, which is essential for piping.
    try:
        whisper_process = subprocess.Popen(
            [
                "/home/rock/whisper.cpp/build/bin/whisper-talk-llama", # Path to the executable
                "-mw", WHISPER_MODEL,
                "-f", # Crucial flag to output text to stdout instead of a file
                # Add any other necessary flags like -t for threads, etc.
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, # Capture errors from whisper-talk-llama
            text=True,
            bufsize=1
        )
    except FileNotFoundError:
        print("ERROR: whisper-talk-llama executable not found. Check the path.")
        return

    # Step 2: Launch llama-cli, reading from the pipe
    try:
        llama_process = subprocess.Popen(
            [
                "/home/rock/llama.cpp/build/bin/llama-cli", # Path to the llama-cli executable
                "-m", LLAMA_MODEL,
                "--gpu-layers", "0", # Set to 0 for CPU-only as per your earlier experience
                "-t", "4",
                "-n", "256", # Max tokens
                "--temp", "0.7",
                # IMPORTANT: Directly piped input might not work well with interactive flags like -i
                # A simple completion mode is often better for scripting.
                "-p", "", # Start with an empty prompt, input comes from pipe
            ],
            stdin=whisper_process.stdout, # Connects whisper output to llama input
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
    except FileNotFoundError:
        print("ERROR: llama-cli executable not found. Check the path.")
        whisper_process.terminate()
        return

    # Close whisper's stdout in this parent process so llama gets SIGPIPE when done
    whisper_process.stdout.close()

    # Step 3: Read and print llama's output
    print("Pipeline started. Speak into your microphone...")
    print("-" * 30)
    
    try:
        for line in iter(llama_process.stdout.readline, ''):
            print(f"AI: {line.strip()}")
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        # Clean up processes
        whisper_process.terminate()
        llama_process.terminate()
        
        # Print any errors from whisper
        whisper_stderr = whisper_process.stderr.read()
        if whisper_stderr:
            print(f"Whisper errors:\n{whisper_stderr}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        print("Usage: python talk_pipeline.py")
        print("Make sure models and executables are configured correctly in the script.")
    else:
        run_talk_pipeline()

