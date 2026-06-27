"""Unit tests for the IntentDetector."""

import pytest

from app.services.intent import Intent, IntentDetector

detector = IntentDetector()

CASES = [
    # greetings
    ("hi", Intent.GREETING),
    ("Hello!", Intent.GREETING),
    ("hey siri", Intent.GREETING),
    ("Good Morning", Intent.GREETING),
    ("what's up?", Intent.GREETING),
    ("yo", Intent.GREETING),
    # farewells
    ("bye", Intent.FAREWELL),
    ("goodbye", Intent.FAREWELL),
    ("see you", Intent.FAREWELL),
    ("take care", Intent.FAREWELL),
    ("catch you later", Intent.FAREWELL),
    ("goodbye for now", Intent.FAREWELL),  # prefix variant
    # gratitude
    ("thanks", Intent.GRATITUDE),
    ("thank you", Intent.GRATITUDE),
    ("thanks for the help", Intent.GRATITUDE),  # prefix variant
    ("awesome", Intent.GRATITUDE),
    ("perfect", Intent.GRATITUDE),
    ("cool", Intent.GRATITUDE),
    # bot info
    ("who are you", Intent.BOT_INFO),
    ("what can you do", Intent.BOT_INFO),
    ("help", Intent.BOT_INFO),
    # small talk
    ("how are you", Intent.SMALL_TALK),
    ("how's it going", Intent.SMALL_TALK),
    ("are you okay", Intent.SMALL_TALK),
    # document queries (must NOT be misclassified)
    ("what is the leave policy?", Intent.DOCUMENT_QUERY),
    ("hello, what is the attendance policy?", Intent.DOCUMENT_QUERY),
    ("tell me about working hours", Intent.DOCUMENT_QUERY),
    ("how many vacation days do I get", Intent.DOCUMENT_QUERY),
    ("", Intent.DOCUMENT_QUERY),
]


@pytest.mark.parametrize("text,expected", CASES)
def test_detect_intent(text, expected):
    assert detector.detect(text) is expected
