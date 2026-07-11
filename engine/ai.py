"""
Google Gemini AI integration for Jarvis.
Uses the new google-genai SDK (google.genai).
Handles conversational AI responses for unknown commands.
"""

import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.env"))

_client = None
_chat = None
_api_available = False

SYSTEM_PROMPT = (
    "You are Jarvis, an advanced AI assistant inspired by Iron Man's Jarvis. "
    "You are helpful, intelligent, and slightly witty. Address the user as 'Sir' or by name. "
    "Keep responses concise (2-3 sentences max) since they will be spoken aloud. "
    "Do not use markdown, bullet points, or special formatting. "
    "Speak in a natural, conversational tone."
)


def _init_gemini():
    """Initialize Gemini client lazily on first use."""
    global _client, _chat, _api_available

    api_key = os.getenv("GEMINI_API_KEY", "")
    if not api_key or api_key == "YOUR_GEMINI_API_KEY_HERE":
        print("[AI] Gemini API key not set in config.env. AI responses disabled.")
        _api_available = False
        return

    try:
        from google import genai
        from google.genai import types

        _client = genai.Client(api_key=api_key)

        # Start a chat with system instruction
        _chat = _client.chats.create(
            model="gemini-2.0-flash",
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                max_output_tokens=200,
                temperature=0.7,
            )
        )
        _api_available = True
        print("[AI] Gemini 2.0 Flash initialized successfully.")
    except Exception as e:
        print(f"[AI] Failed to initialize Gemini: {e}")
        _api_available = False


def ask_gemini(question: str, owner_name: str = "Sir") -> str:
    """
    Send a question to Gemini and return the response text.
    Falls back to a polite error message if API is unavailable.
    """
    global _chat

    if not _api_available:
        _init_gemini()

    if not _api_available:
        return (
            "My AI brain is not connected yet, Sir. "
            "Please open config.env and add your Gemini API key."
        )

    try:
        prompt = f"[User: {owner_name}] {question}"
        response = _chat.send_message(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"[AI] Gemini error: {e}")
        # Reset chat session on error
        try:
            from google import genai
            from google.genai import types
            _chat = _client.chats.create(
                model="gemini-2.0-flash",
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    max_output_tokens=200,
                )
            )
        except Exception:
            pass
        return "I encountered an error processing that, Sir. Please try again."


def reset_conversation():
    """Start a fresh conversation (clear chat history)."""
    global _chat, _api_available
    _api_available = False
    _init_gemini()
