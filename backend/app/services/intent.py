"""Intent detection for incoming chat messages.

Classifies a message into a conversational intent (greeting, farewell, …) or
``DOCUMENT_QUERY`` (which should run the RAG pipeline). Conversational intents
have canned responses and must never reach the vector DB or the LLM.

Detection is deliberately conservative — exact normalized-phrase matching plus a
few safe prefixes — so genuine document questions are never misclassified as
chit-chat. The phrase lists live here so they can evolve and be unit-tested
independently of the chat service.
"""

import re
from enum import Enum


class Intent(str, Enum):
    GREETING = "greeting"
    FAREWELL = "farewell"
    GRATITUDE = "gratitude"
    BOT_INFO = "bot_info"
    SMALL_TALK = "small_talk"
    DOCUMENT_QUERY = "document_query"


# -- canned responses --------------------------------------------------------

GREETING_RESPONSE = (
    "👋 Hello! I'm your Company Policy Assistant. I can answer questions based "
    "on the uploaded company documents. How can I help you today?"
)
FAREWELL_RESPONSE = (
    "👋 Goodbye! Have a great day. Feel free to return anytime if you have "
    "questions about the uploaded company documents."
)
GRATITUDE_RESPONSE = (
    "😊 You're welcome! Let me know if you need any help with the uploaded "
    "company documents."
)
BOT_INFO_RESPONSE = (
    "I'm your Company Policy Assistant. I answer questions using the uploaded "
    "company documents, including leave policies, attendance, salary & "
    "benefits, HR policies, and learning & development."
)
SMALL_TALK_RESPONSE = (
    "I'm doing well, thank you! 😊 I'm here to help answer questions about your "
    "uploaded company documents."
)
# Returned by the chat service when retrieval finds no relevant context.
OUT_OF_SCOPE_RESPONSE = (
    "I couldn't find information about that in the uploaded company documents."
    "\n\nPlease ask questions related to:\n\n"
    "- Leave Policy\n"
    "- Attendance\n"
    "- Working Hours\n"
    "- Salary & Benefits\n"
    "- Learning & Development\n"
    "- HR Policies"
)

# Maps a conversational intent to its canned response (excludes DOCUMENT_QUERY).
INTENT_RESPONSES: dict[Intent, str] = {
    Intent.GREETING: GREETING_RESPONSE,
    Intent.FAREWELL: FAREWELL_RESPONSE,
    Intent.GRATITUDE: GRATITUDE_RESPONSE,
    Intent.BOT_INFO: BOT_INFO_RESPONSE,
    Intent.SMALL_TALK: SMALL_TALK_RESPONSE,
}


# -- phrase tables (normalized: lowercase, no punctuation) -------------------

_EXACT: dict[Intent, frozenset[str]] = {
    Intent.GREETING: frozenset(
        {
            "hi", "hii", "hello", "helo", "hey", "hey siri", "hey there",
            "hi there", "hello there", "good morning", "good afternoon",
            "good evening", "good day", "whats up", "wassup", "sup", "yo",
            "greetings", "howdy",
        }
    ),
    Intent.FAREWELL: frozenset(
        {
            "bye", "byebye", "bye bye", "goodbye", "good bye", "see you",
            "see you later", "see ya", "cya", "take care", "catch you later",
            "later", "farewell", "good night", "goodnight",
        }
    ),
    Intent.GRATITUDE: frozenset(
        {
            "thanks", "thank you", "thanks a lot", "thank you so much",
            "thankyou", "thx", "ty", "awesome", "great", "perfect", "cool",
            "nice", "well done",
        }
    ),
    Intent.BOT_INFO: frozenset(
        {
            "who are you", "what are you", "what can you do", "what do you do",
            "who r u", "help", "what is this", "how do you work",
            "what can you help with", "what do you know",
        }
    ),
    Intent.SMALL_TALK: frozenset(
        {
            "how are you", "how are you doing", "hows it going",
            "how is it going", "are you okay", "are you ok", "how do you do",
            "how are things", "hope you are doing well",
        }
    ),
}

# Safe phrase prefixes for multi-word farewell variants (e.g. "goodbye for
# now", "see you soon"). Each matches the whole message or the message starting
# with "<prefix> ".
_FAREWELL_PREFIXES: tuple[str, ...] = (
    "goodbye",
    "good bye",
    "see you",
    "good night",
)


def _normalize(text: str) -> str:
    t = text.strip().lower().replace("’", "'")
    t = re.sub(r"[^\w\s']", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t.replace("'", "")  # "what's" -> "whats"


class IntentDetector:
    """Classifies a chat message into an :class:`Intent`."""

    def detect(self, text: str) -> Intent:
        norm = _normalize(text or "")
        if not norm:
            return Intent.DOCUMENT_QUERY

        for intent, phrases in _EXACT.items():
            if norm in phrases:
                return intent

        # Gratitude stem: "thanks", "thank you", "thanks for the help", ...
        if norm.startswith("thank"):
            return Intent.GRATITUDE

        # Farewell phrase prefixes.
        if any(
            norm == p or norm.startswith(p + " ") for p in _FAREWELL_PREFIXES
        ):
            return Intent.FAREWELL

        return Intent.DOCUMENT_QUERY
