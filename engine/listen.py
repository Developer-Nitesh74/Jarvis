import speech_recognition as sr
import os

_recognizer = sr.Recognizer()
_recognizer.pause_threshold = 1.0      # seconds of silence before considering phrase complete
_recognizer.energy_threshold = 300     # minimum audio energy to consider for recording
_recognizer.dynamic_energy_threshold = True


def listen_once(timeout: int = 10, phrase_limit: int = 8) -> str:
    """
    Listen for a single spoken phrase and return the recognized text.
    Returns empty string if nothing is understood.
    """
    with sr.Microphone() as source:
        try:
            _recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio = _recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_limit)
            text = _recognizer.recognize_google(audio, language="en-in")
            return text.lower().strip()
        except sr.WaitTimeoutError:
            return ""
        except sr.UnknownValueError:
            return ""
        except sr.RequestError as e:
            print(f"[Listen] Speech recognition service error: {e}")
            return ""
        except Exception as e:
            print(f"[Listen] Unexpected error: {e}")
            return ""


def listen_for_wake_word(wake_word: str = "jarvis", callback=None) -> None:
    """
    Continuously listen in background for the wake word.
    When detected, calls callback() and stops listening.
    This runs in a loop — call it from a daemon thread.
    """
    wake_word = wake_word.lower()
    print(f"[Wake Word] Listening for '{wake_word}'...")

    with sr.Microphone() as source:
        _recognizer.adjust_for_ambient_noise(source, duration=1)
        while True:
            try:
                audio = _recognizer.listen(source, timeout=None, phrase_time_limit=4)
                text = _recognizer.recognize_google(audio, language="en-in").lower()
                print(f"[Wake Word] Heard: {text}")
                if wake_word in text or "stop" in text:
                    print(f"[Wake Word/Stop] Keyword detected: {text}")
                    if callback:
                        callback(text)
                    # After waking, re-adjust and continue listening
                    _recognizer.adjust_for_ambient_noise(source, duration=0.3)
            except sr.WaitTimeoutError:
                pass
            except sr.UnknownValueError:
                pass
            except sr.RequestError as e:
                print(f"[Wake Word] Service error: {e}")
                break
            except Exception as e:
                print(f"[Wake Word] Error: {e}")
                break
