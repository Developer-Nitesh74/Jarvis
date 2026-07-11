"""
Jarvis Command Router.
Takes a text command and routes it to the correct feature handler.
Falls back to Gemini AI for unrecognized commands.
"""

from engine import features, config, ai

# Minimum length for AI fallback
MIN_AI_QUERY_LENGTH = 3


def process_command(text: str, eel_instance=None) -> str:
    """
    Route a text command to the appropriate handler.
    
    Args:
        text: lowercase command string
        eel_instance: the eel module (for calling JS functions if needed)
    
    Returns:
        Response string to speak and display.
    """
    if not text or len(text.strip()) < 1:
        return ""

    t = text.lower().strip()

    # Get owner name + DB data for context
    owner_info = config.get_owner_info()
    owner_name = owner_info[0] if owner_info else "Sir"
    sys_cmds = config.get_sys_commands()
    web_cmds = config.get_web_commands()

    # ── Greetings ──────────────────────────────────────────────────────────────
    if any(w in t for w in ["hello", "hi jarvis", "hey jarvis", "good morning", "good afternoon", "good evening", "good night", "wake up"]):
        return features.get_greeting(owner_name)

    # ── Identity ───────────────────────────────────────────────────────────────
    if any(w in t for w in ["who are you", "what are you", "introduce yourself", "your name"]):
        return features.introduce_self()

    # ── Time & Date ────────────────────────────────────────────────────────────
    if any(w in t for w in ["what time", "current time", "time now", "tell me the time"]):
        return features.get_time()

    if any(w in t for w in ["what's the date", "what date", "today's date", "current date", "tell me the date"]):
        return features.get_date()

    if any(w in t for w in ["what day", "which day", "today is"]):
        return features.get_day()

    # ── Wikipedia ──────────────────────────────────────────────────────────────
    if t.startswith("search wikipedia") or t.startswith("wikipedia"):
        query = t.replace("search wikipedia", "").replace("wikipedia", "").strip()
        if query:
            return features.wikipedia_search(query)

    if t.startswith("tell me about") or t.startswith("what is") or t.startswith("who is") or t.startswith("what are"):
        query = (t.replace("tell me about", "")
                  .replace("what is", "")
                  .replace("who is", "")
                  .replace("what are", "")
                  .strip())
        if query and len(query) > 2:
            return features.wikipedia_search(query)

    # ── Jokes & Fun ────────────────────────────────────────────────────────────
    if any(w in t for w in ["tell me a joke", "say a joke", "joke", "make me laugh", "funny"]):
        return features.tell_joke()

    if any(w in t for w in ["fun fact", "interesting fact", "did you know", "tell me a fact"]):
        return features.tell_fact()

    if "flip a coin" in t or "flip coin" in t or "toss a coin" in t:
        return features.flip_coin()

    if "roll a dice" in t or "roll dice" in t or "roll the dice" in t:
        return features.roll_dice()

    # ── System & App Control ───────────────────────────────────────────────────
    if t.startswith("open"):
        target = t.replace("open", "").strip()
        if target:
            # Check if it's a website keyword
            for _, keyword, url in web_cmds:
                if keyword.lower() in target:
                    import webbrowser
                    webbrowser.open(url)
                    return f"Opening {keyword}, Sir."
            # Check common website names
            web_keywords = ["google", "youtube", "facebook", "instagram", "twitter",
                          "github", "reddit", "wikipedia", "netflix", "amazon", "linkedin"]
            if any(w in target for w in web_keywords):
                return features.open_website(target, web_cmds)
            # Otherwise open as app
            return features.open_app(target, sys_cmds)

    if t.startswith("close") or t.startswith("exit"):
        target = t.replace("close", "").replace("exit", "").strip()
        if target:
            return f"I cannot force-close apps yet, Sir. Please close {target} manually."

    # ── Web Search ─────────────────────────────────────────────────────────────
    if t.startswith("search for") or t.startswith("search"):
        query = t.replace("search for", "").replace("search", "").strip()
        if query:
            return features.google_search(query)

    if t.startswith("google"):
        query = t.replace("google", "").strip()
        return features.google_search(query) if query else features.open_website("google", web_cmds)

    if "youtube" in t and ("search" in t or "play" in t or "find" in t):
        query = (t.replace("youtube", "").replace("search", "")
                  .replace("play", "").replace("find", "").strip())
        if query:
            return features.youtube_search(query)
        return features.open_website("youtube", web_cmds)

    # ── Music ──────────────────────────────────────────────────────────────────
    if any(w in t for w in ["play music", "play song", "play some music", "play songs"]):
        return features.play_music()

    # ── System Controls ────────────────────────────────────────────────────────
    if "shutdown" in t or "shut down" in t:
        if "cancel" in t:
            return features.cancel_shutdown()
        return features.shutdown_system()

    if "restart" in t or "reboot" in t:
        return features.restart_system()

    if "sleep" in t and ("system" in t or "computer" in t or "pc" in t):
        return features.sleep_system()

    if "battery" in t:
        return features.get_battery_status()

    if "screenshot" in t or "screen capture" in t:
        return features.take_screenshot()

    if "volume" in t or "mute" in t or "unmute" in t:
        if "mute" in t:
            return features.set_volume("mute")
        elif "unmute" in t:
            return features.set_volume("unmute")
        elif "up" in t or "increase" in t or "louder" in t:
            return features.set_volume("up")
        elif "down" in t or "decrease" in t or "lower" in t:
            return features.set_volume("down")

    # ── Farewells ──────────────────────────────────────────────────────────────
    if any(w in t for w in ["goodbye", "bye", "see you", "good bye", "quit", "stop", "that's all"]):
        return features.farewell(owner_name)

    # ── Thank you ──────────────────────────────────────────────────────────────
    if any(w in t for w in ["thank you", "thanks", "thank u", "ty"]):
        return f"You're always welcome, {owner_name}."

    # ── AI Fallback ────────────────────────────────────────────────────────────
    if len(t) >= MIN_AI_QUERY_LENGTH:
        return ai.ask_gemini(text, owner_name)

    return f"I didn't quite catch that, {owner_name}. Could you repeat?"
