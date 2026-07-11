import subprocess
import os
import threading
import tempfile

_process = None
_lock = threading.Lock()

def speak(text: str):
    """Speak text aloud using pyttsx3 in a subprocess for robust interruption."""
    global _process
    
    with _lock:
        # If already speaking, kill it
        if _process and _process.poll() is None:
            try:
                _process.kill()
            except Exception:
                pass

        # Write text to a temp file
        fd, path = tempfile.mkstemp(suffix=".txt", text=True)
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            f.write(text)
            
        # Create the pyttsx3 runner script
        script = """
import pyttsx3
import sys
import os

text_file = sys.argv[1]
with open(text_file, 'r', encoding='utf-8') as f:
    text = f.read()

try:
    engine = pyttsx3.init()
    engine.setProperty('rate', 170)
    engine.say(text)
    engine.runAndWait()
except Exception as e:
    pass
"""
        script_fd, script_path = tempfile.mkstemp(suffix=".py", text=True)
        with os.fdopen(script_fd, 'w', encoding='utf-8') as f:
            f.write(script)
            
        # Run the subprocess invisibly
        # python executable
        import sys
        python_exe = sys.executable
        
        # CREATE_NO_WINDOW = 0x08000000 to hide console window on Windows
        _process = subprocess.Popen([python_exe, script_path, path], 
                                    creationflags=0x08000000)
        
    # Wait for completion outside the lock so we don't block stop_speech
    _process.wait()
    
    # Clean up temp files
    try:
        os.remove(path)
        os.remove(script_path)
    except:
        pass


def stop_speech():
    """Immediately kill the speech subprocess."""
    global _process
    with _lock:
        if _process is not None and _process.poll() is None:
            try:
                _process.kill()
                print("[Speak] Subprocess killed.")
            except Exception as e:
                print(f"[Speak] Error killing process: {e}")
            _process = None


def speak_async(text: str):
    """Speak text in a background thread."""
    t = threading.Thread(target=speak, args=(text,), daemon=True)
    t.start()

