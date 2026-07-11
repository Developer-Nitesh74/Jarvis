"""
╔══════════════════════════════════════════════════════════════════╗
║           Jarvis  —  Just A Rather Very Intelligent System       ║
║                     Main Backend (Eel Server)                     ║
╚══════════════════════════════════════════════════════════════════╝

Run this file to start Jarvis:
    py -3.12 main.py

Requirements:
    pip install eel pyttsx3 SpeechRecognition pyaudio wikipedia
    pip install pyjokes google-generativeai python-dotenv
    pip install opencv-python face-recognition
"""

import eel
import os
import json
import threading
import time
from dotenv import load_dotenv

# Load environment config
load_dotenv(os.path.join(os.path.dirname(__file__), "config.env"))

# Init eel with the www directory
eel.init(os.path.join(os.path.dirname(__file__), "www"))

# Import engine modules
from engine import config as db
from engine import speak, listen, command, features, face_auth

# ── Initialize database ───────────────────────────────────────────────────────
db.init_db()

# ── Global state ──────────────────────────────────────────────────────────────
_is_listening = False          # True while processing a voice command
_wake_thread = None            # Background wake-word listener thread
_wake_word = os.getenv("WAKE_WORD", "jarvis").lower()

# ─────────────────────────────────────────────────────────────────────────────
# Helper: send response to UI + speak it
# ─────────────────────────────────────────────────────────────────────────────

def _respond(user_msg: str, bot_msg: str):
    """Update the chat UI and speak the response."""
    if user_msg:
        db.save_chat("User", user_msg)
        eel.senderText(user_msg)()
    if bot_msg:
        db.save_chat("Jarvis", bot_msg)
        eel.receiverText(bot_msg)()
        eel.DisplayMessage(bot_msg)()
        speak.speak_async(bot_msg)


# ─────────────────────────────────────────────────────────────────────────────
# Startup sequence — called by JS on page load
# ─────────────────────────────────────────────────────────────────────────────

@eel.expose
def init():
    """
    Called by JS when the page loads.
    Runs the startup animation sequence (loader → face auth → greeting).
    """
    def _run():
        time.sleep(1)

        # Phase 1: Loader → Face scan animation
        eel.DisplayMessage("Initializing systems...")()
        time.sleep(2)

        # Phase 2: Face authentication
        eel.hideLoader()()
        eel.DisplayMessage("Scanning face...")()

        # Simulate face scan animation for 2 seconds
        time.sleep(2.5)
        auth_ok = True

        if auth_ok:
            eel.hideFaceAuth()()
            eel.DisplayMessage("Access Granted!")()
            time.sleep(2)

            eel.hideFaceAuthSuccess()()
            owner_info = db.get_owner_info()
            owner_name = owner_info[0] if owner_info else "Sir"
            greeting = features.get_greeting(owner_name)
            eel.DisplayMessage(greeting)()
            time.sleep(2.5)

            # Phase 3: Show main UI
            eel.hideStart()()
            speak.speak_async(greeting)

            # Phase 4: Start wake-word listener
            _start_wake_word_listener()

        else:
            eel.DisplayMessage("Face not recognized. Access denied.")()
            speak.speak_async("Face not recognized. Access denied.")
            time.sleep(3)

    threading.Thread(target=_run, daemon=True).start()


# ─────────────────────────────────────────────────────────────────────────────
# Wake-word listener
# ─────────────────────────────────────────────────────────────────────────────

def _start_wake_word_listener():
    """Start the background thread that listens for the wake word."""
    global _wake_thread
    if _wake_thread and _wake_thread.is_alive():
        return

    def _on_wake(detected_text=""):
        """Called when wake word or stop is detected."""
        if "stop" in detected_text.lower():
            stopJarvis()
            # If we were listening, we might want to reset the UI, but stopJarvis does it.
            return
            
        if not _is_listening:
            playAssistantSound()
            eel.ShowHood()()    # trigger mic-active mode in UI
            time.sleep(0.3)
            _trigger_listen()

    _wake_thread = threading.Thread(
        target=listen.listen_for_wake_word,
        args=(_wake_word, _on_wake),
        daemon=True
    )
    _wake_thread.start()
    print(f"[Jarvis] Wake word listener started. Say '{_wake_word}' to activate.")


def _trigger_listen():
    """Listen once and process the command."""
    global _is_listening
    if _is_listening:
        return
    _is_listening = True

    def _do_listen():
        global _is_listening
        try:
            eel.DisplayMessage("Listening...")()
            spoken = listen.listen_once(timeout=8, phrase_limit=8)
            if spoken:
                eel.DisplayMessage(f"You said: {spoken}")()
                _process_and_respond(spoken)
            else:
                resp = "I didn't catch that. Could you repeat?"
                eel.DisplayMessage(resp)()
                speak.speak_async(resp)
        finally:
            _is_listening = False
            eel.ShowHood()()   # return to normal UI

    threading.Thread(target=_do_listen, daemon=True).start()


# ─────────────────────────────────────────────────────────────────────────────
# Core command processing
# ─────────────────────────────────────────────────────────────────────────────

def _process_and_respond(text: str):
    """Route a command and send response to UI."""
    if not text:
        return
    response = command.process_command(text)
    _respond(text, response)
    # After speaking finishes, return UI to main screen
    # speak_async is non-blocking so we wait briefly for speech to start
    import time
    time.sleep(0.5)
    # Then call ShowHood when the speech subprocess eventually ends
    # We do this by watching in a thread
    def _wait_and_return():
        from engine import speak as spk
        if spk._process:
            spk._process.wait()  # wait for speech to end
        try:
            eel.ShowHood()()
        except Exception:
            pass
    threading.Thread(target=_wait_and_return, daemon=True).start()



# ─────────────────────────────────────────────────────────────────────────────
# Eel-exposed functions (called from JavaScript)
# ─────────────────────────────────────────────────────────────────────────────

@eel.expose
def allCommands(message: str = ""):
    """
    Called when user clicks the mic button OR sends a typed message.
    If message is provided, process it directly.
    Otherwise, listen via microphone.
    """
    if message and message.strip():
        # Typed command
        threading.Thread(
            target=_process_and_respond,
            args=(message.strip().lower(),),
            daemon=True
        ).start()
    else:
        # Mic command
        _trigger_listen()


@eel.expose
def playAssistantSound():
    """Play the activation chime (beep). Uses pyttsx3 for now."""
    pass


@eel.expose
def stopJarvis():
    """Immediately stop Jarvis from speaking."""
    print("[Jarvis] Interrupted by user.")
    speak.stop_speech()
    eel.ShowHood()()
    eel.DisplayMessage("Ready")()


@eel.expose
def loadChatHistory():
    """Send all past chat history to the frontend UI."""
    history = db.get_chat_history()
    for row in history:
        sender, msg, ts = row
        if sender == "User":
            eel.senderText(msg)()
        else:
            eel.receiverText(msg)()


# ── Settings: Personal Info ────────────────────────────────────────────────────

@eel.expose
def personalInfo():
    """Return owner info as JSON array to JS."""
    info = db.get_owner_info()
    eel.getData(json.dumps(info))()


@eel.expose
def updatePersonalInfo(name, designation, mobile, email, city):
    db.update_owner_info(name, designation, mobile, email, city)


# ── Settings: System Commands ─────────────────────────────────────────────────

@eel.expose
def displaySysCommand():
    rows = db.get_sys_commands()
    eel.displaySysCommand(json.dumps(rows))()


@eel.expose
def addSysCommand(keyword, path):
    db.add_sys_command(keyword, path)


@eel.expose
def deleteSysCommand(cmd_id):
    db.delete_sys_command(cmd_id)


# ── Settings: Web Commands ────────────────────────────────────────────────────

@eel.expose
def displayWebCommand():
    rows = db.get_web_commands()
    eel.displayWebCommand(json.dumps(rows))()


@eel.expose
def addWebCommand(keyword, url):
    db.add_web_command(keyword, url)


@eel.expose
def deleteWebCommand(cmd_id):
    db.delete_web_command(cmd_id)


# ── Settings: Contacts / Phone Book ──────────────────────────────────────────

@eel.expose
def displayPhoneBookCommand():
    rows = db.get_contacts()
    eel.displayPhoneBookCommand(json.dumps(rows))()


@eel.expose
def InsertContacts(name, mobile, email="", city=""):
    db.add_contact(name, mobile, email, city)


@eel.expose
def deletePhoneBookCommand(contact_id):
    db.delete_contact(contact_id)


# ─────────────────────────────────────────────────────────────────────────────
# Launch the app
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 60)
    print("  Jarvis — Starting up...")
    print("=" * 60)

    # Determine browser - try Chrome first, fall back to default
    chrome_path = None
    common_chrome = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe"),
    ]
    for p in common_chrome:
        if os.path.exists(p):
            chrome_path = p
            break

    try:
        if chrome_path:
            eel.start(
                "index.html",
                size=(1200, 800),
                mode="chrome",
                cmdline_args=["--start-maximized"],
                block=True
            )
        else:
            # Fall back to default browser
            eel.start(
                "index.html",
                size=(1200, 800),
                mode="default",
                block=True
            )
    except (SystemExit, MemoryError, KeyboardInterrupt):
        print("\n[Jarvis] Shutting down. Goodbye!")
