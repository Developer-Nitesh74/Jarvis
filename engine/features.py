"""
Jarvis Features — all voice/text command handlers.
Each function returns a response string (to speak + display).
"""

import os
import webbrowser
import subprocess
import datetime
import random
import threading

# ── Lazy imports (keep startup fast) ──────────────────────────────────────────

def _try_import(module_name):
    try:
        import importlib
        return importlib.import_module(module_name)
    except ImportError:
        return None


# ── Greetings ──────────────────────────────────────────────────────────────────

def get_greeting(owner_name: str = "Sir") -> str:
    hour = datetime.datetime.now().hour
    if 5 <= hour < 12:
        period = "Good morning"
    elif 12 <= hour < 17:
        period = "Good afternoon"
    elif 17 <= hour < 21:
        period = "Good evening"
    else:
        period = "Good night"
    
    greetings = [
        f"{period}, {owner_name}. All systems are online and ready.",
        f"{period}, {owner_name}. Jarvis at your service.",
        f"{period}, {owner_name}. How may I assist you today?",
    ]
    return random.choice(greetings)


def introduce_self() -> str:
    lines = [
        "I am Jarvis, your Just A Rather Very Intelligent System. I'm here to assist with anything you need.",
        "I am Jarvis, your personal AI assistant. Think of me as your digital Alfred, but smarter.",
        "Jarvis — Just A Rather Very Intelligent System. At your service, as always.",
    ]
    return random.choice(lines)


# ── Time & Date ────────────────────────────────────────────────────────────────

def get_time() -> str:
    now = datetime.datetime.now()
    hour = now.strftime("%I").lstrip("0")
    minute = now.strftime("%M")
    period = now.strftime("%p")
    if minute == "00":
        return f"The time is {hour} {period}, Sir."
    return f"The time is {hour} {minute} {period}, Sir."


def get_date() -> str:
    now = datetime.datetime.now()
    day = now.strftime("%A")
    date = now.strftime("%B %d, %Y")
    return f"Today is {day}, {date}, Sir."


def get_day() -> str:
    return f"Today is {datetime.datetime.now().strftime('%A')}, Sir."


# ── Wikipedia ──────────────────────────────────────────────────────────────────

def wikipedia_search(query: str) -> str:
    wiki = _try_import("wikipedia")
    if wiki is None:
        return "Wikipedia module is not available, Sir."
    try:
        wiki.set_lang("en")
        results = wiki.summary(query, sentences=2, auto_suggest=True)
        return results
    except wiki.exceptions.DisambiguationError as e:
        # Take the first option
        try:
            results = wiki.summary(e.options[0], sentences=2)
            return results
        except Exception:
            return f"There are multiple results for {query}. Please be more specific, Sir."
    except wiki.exceptions.PageError:
        return f"I couldn't find information about {query} on Wikipedia, Sir."
    except Exception as e:
        return f"I encountered an error searching Wikipedia: {str(e)}"


# ── Jokes ──────────────────────────────────────────────────────────────────────

def tell_joke() -> str:
    pyjokes = _try_import("pyjokes")
    if pyjokes is None:
        jokes = [
            "Why don't scientists trust atoms? Because they make up everything.",
            "I told my computer I needed a break. Now it won't stop sending me Kit-Kat ads.",
            "Why do programmers prefer dark mode? Because light attracts bugs.",
            "How many programmers does it take to change a light bulb? None — it's a hardware problem.",
        ]
        return random.choice(jokes)
    return pyjokes.get_joke()


# ── System Apps ───────────────────────────────────────────────────────────────

BUILTIN_APPS = {
    "notepad":     "notepad.exe",
    "calculator":  "calc.exe",
    "paint":       "mspaint.exe",
    "explorer":    "explorer.exe",
    "cmd":         "cmd.exe",
    "task manager":"taskmgr.exe",
    "camera":      "microsoft.windows.camera:",
    "settings":    "ms-settings:",
    "calendar":    "outlookcal:",
}

def open_app(app_name: str, sys_commands: list = None) -> str:
    """
    Open an application. Checks custom sys_commands DB first, then builtins.
    sys_commands: list of (id, keyword, path) tuples from DB
    """
    app_lower = app_name.lower().strip()

    # Check custom commands first
    if sys_commands:
        for _, keyword, path in sys_commands:
            if keyword.lower() in app_lower or app_lower in keyword.lower():
                try:
                    os.startfile(path)
                    return f"Opening {keyword}, Sir."
                except Exception as e:
                    return f"I couldn't open {keyword}: {str(e)}"

    # Check builtins
    for key, cmd in BUILTIN_APPS.items():
        if key in app_lower:
            try:
                if cmd.endswith(":"):
                    os.startfile(cmd)
                else:
                    subprocess.Popen(cmd)
                return f"Opening {key}, Sir."
            except Exception as e:
                return f"I couldn't open {key}: {str(e)}"

    return f"I couldn't find an app named {app_name}, Sir. You can add it in Settings."


# ── Web Browsing ───────────────────────────────────────────────────────────────

def open_website(site_name: str, web_commands: list = None) -> str:
    """
    Open a website. Checks custom web_commands DB first, then common sites.
    """
    site_lower = site_name.lower().strip()

    # Check custom commands
    if web_commands:
        for _, keyword, url in web_commands:
            if keyword.lower() in site_lower or site_lower in keyword.lower():
                webbrowser.open(url)
                return f"Opening {keyword}, Sir."

    # Common websites
    common = {
        "google":    "https://www.google.com",
        "youtube":   "https://www.youtube.com",
        "facebook":  "https://www.facebook.com",
        "instagram": "https://www.instagram.com",
        "twitter":   "https://www.twitter.com",
        "github":    "https://www.github.com",
        "reddit":    "https://www.reddit.com",
        "wikipedia": "https://www.wikipedia.org",
        "netflix":   "https://www.netflix.com",
        "amazon":    "https://www.amazon.com",
        "linkedin":  "https://www.linkedin.com",
    }

    for key, url in common.items():
        if key in site_lower:
            webbrowser.open(url)
            return f"Opening {key}, Sir."

    # Treat as direct URL or search
    if "." in site_lower:
        url = f"https://{site_lower}" if not site_lower.startswith("http") else site_lower
        webbrowser.open(url)
        return f"Opening {site_lower}, Sir."

    return google_search(site_name)


def google_search(query: str) -> str:
    url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
    webbrowser.open(url)
    return f"Searching Google for {query}, Sir."


def youtube_search(query: str) -> str:
    url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
    webbrowser.open(url)
    return f"Searching YouTube for {query}, Sir."


# ── System Controls ────────────────────────────────────────────────────────────

def get_battery_status() -> str:
    try:
        import psutil
        battery = psutil.sensors_battery()
        if battery:
            percent = battery.percent
            plugged = "and plugged in" if battery.power_plugged else "and not plugged in"
            return f"Battery is at {percent:.0f}% {plugged}, Sir."
        return "Battery information is not available, Sir."
    except Exception:
        return "I couldn't retrieve battery status, Sir."


def shutdown_system(delay: int = 10) -> str:
    os.system(f"shutdown /s /t {delay}")
    return f"System will shut down in {delay} seconds, Sir."


def restart_system(delay: int = 10) -> str:
    os.system(f"shutdown /r /t {delay}")
    return f"System will restart in {delay} seconds, Sir."


def sleep_system() -> str:
    os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
    return "Putting the system to sleep, Sir."


def cancel_shutdown() -> str:
    os.system("shutdown /a")
    return "Shutdown cancelled, Sir."


# ── Music & Media ──────────────────────────────────────────────────────────────

def play_music() -> str:
    music_dirs = [
        os.path.expanduser("~/Music"),
        os.path.expanduser("~/Downloads"),
        "C:/Users/Public/Music",
    ]
    for d in music_dirs:
        if os.path.isdir(d):
            files = [f for f in os.listdir(d) if f.endswith((".mp3", ".wav", ".m4a", ".flac"))]
            if files:
                os.startfile(os.path.join(d, files[0]))
                return "Playing music, Sir."
    # Fallback: open YouTube Music
    webbrowser.open("https://music.youtube.com")
    return "Opening YouTube Music, Sir."


# ── Utility ────────────────────────────────────────────────────────────────────

def take_screenshot() -> str:
    try:
        import pyautogui
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        path = os.path.expanduser(f"~/Desktop/screenshot_{ts}.png")
        pyautogui.screenshot(path)
        return f"Screenshot saved to your desktop, Sir."
    except Exception:
        return "I couldn't take a screenshot, Sir. pyautogui may not be installed."


def set_volume(level: str) -> str:
    """level should be 'up', 'down', 'mute', or a number 0-100"""
    try:
        from ctypes import cast, POINTER
        from comtypes import CLSCTX_ALL
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        if level == "mute":
            volume.SetMute(1, None)
            return "Volume muted, Sir."
        elif level == "unmute":
            volume.SetMute(0, None)
            return "Volume unmuted, Sir."
        elif level.isdigit():
            lvl = int(level) / 100.0
            volume.SetMasterVolumeLevelScalar(max(0.0, min(1.0, lvl)), None)
            return f"Volume set to {level}%, Sir."
    except Exception:
        pass
    return "I couldn't adjust the volume, Sir."


# ── Fun / Misc ─────────────────────────────────────────────────────────────────

FACTS = [
    "A group of flamingos is called a flamboyance.",
    "Honey never expires. Archaeologists have found 3000-year-old honey in Egyptian tombs.",
    "Octopuses have three hearts and blue blood.",
    "The Eiffel Tower can be 15 cm taller during summer due to thermal expansion.",
    "A day on Venus is longer than a year on Venus.",
    "Bananas are berries, but strawberries are not.",
    "The shortest war in history lasted 38 to 45 minutes.",
]

def tell_fact() -> str:
    return random.choice(FACTS)


def flip_coin() -> str:
    result = random.choice(["Heads", "Tails"])
    return f"It's {result}, Sir."


def roll_dice(sides: int = 6) -> str:
    result = random.randint(1, sides)
    return f"I rolled a {sides}-sided dice and got {result}, Sir."


# ── Farewells ──────────────────────────────────────────────────────────────────

def farewell(owner_name: str = "Sir") -> str:
    lines = [
        f"Goodbye, {owner_name}. Have a great day.",
        f"Take care, {owner_name}. I'll be here if you need me.",
        f"Farewell, {owner_name}. Jarvis signing off.",
    ]
    return random.choice(lines)
