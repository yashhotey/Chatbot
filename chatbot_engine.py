"""
chatbot_engine.py
-----------------
Pure backend logic for the Gemini chatbot.
No UI / Streamlit imports here — keep this layer clean.
"""

import os
import asyncio
from google import genai
from dotenv import load_dotenv

# ── Load environment variables from .env ────────────────────────────────────
load_dotenv()
print("API KEY =", os.getenv("GEMINI_API_KEY"))

# ── Module-level constants ───────────────────────────────────────────────────
MODEL_ID         = "gemini-2.5-flash"
MODEL_DISPLAY    = "Gemini 2.5 Flash"
MODEL_PROVIDER   = "Google DeepMind"
MODEL_DESCRIPTION = (
    "Gemini 2.5 Flash is Google's latest lightweight multimodal model, "
    "optimised for speed and efficiency while maintaining high-quality responses."
)

# ── Client / session factory ─────────────────────────────────────────────────

def create_client() -> genai.Client:
    """Instantiate and return a Gemini async client."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "GEMINI_API_KEY not found. "
            "Add it to your .env file as: GEMINI_API_KEY=your_key_here"
        )
    return genai.Client(api_key=api_key)


def create_chat_session(client: genai.Client):
    """Create and return a new chat session."""
    return client.chats.create(model=MODEL_ID)


# ── Async response helper ────────────────────────────────────────────────────

def get_response(chat_session, prompt: str) -> str:
    """
    Send prompt to Gemini and return response.
    """
    try:
        response = chat_session.send_message(prompt)
        return response.text
    except Exception as exc:
        raise RuntimeError(f"Model returned an error: {exc}") from exc