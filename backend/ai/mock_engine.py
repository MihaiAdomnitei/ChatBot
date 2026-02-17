"""
Mock Engine - A mock AI engine for testing without the real model.

This provides realistic-looking responses without requiring
the actual LLM to be loaded.
"""

import random
from typing import List, Dict


class MockPatientEngine:
    """
    Mock engine that simulates patient responses for testing.

    This allows testing the full API flow without loading
    the actual AI model.
    """

    # Sample responses based on common questions
    RESPONSES = {
        "pain": [
            "The pain is sharp and throbbing, mostly in my lower right side.",
            "It hurts a lot, especially when I bite down on something.",
            "The pain comes and goes, but it's been getting worse lately.",
            "It's a dull ache that sometimes becomes very intense.",
        ],
        "location": [
            "It's in my back teeth, on the right side.",
            "The pain seems to be coming from one of my molars.",
            "I think it's the tooth second from the back, lower jaw.",
            "It's hard to tell exactly, but somewhere in the back of my mouth.",
        ],
        "duration": [
            "It started about three days ago.",
            "I've been having this problem for about a week now.",
            "The pain began suddenly yesterday morning.",
            "It's been bothering me on and off for a few weeks.",
        ],
        "trigger": [
            "Cold drinks make it much worse.",
            "It hurts when I eat anything sweet.",
            "Biting down on hard food triggers the pain.",
            "Hot coffee seems to set it off.",
        ],
        "default": [
            "I'm not sure how to describe it, but it's quite uncomfortable.",
            "Can you explain what you mean? I'm just here because my tooth hurts.",
            "I've never had dental problems like this before.",
            "I just want to find out what's wrong and get some relief.",
            "Is this something serious, doctor?",
        ]
    }

    def __init__(self):
        self.device = "mock"

    def generate(
        self,
        messages: List[Dict[str, str]],
        max_new_tokens: int = 100,
        temperature: float = 0.4,
        **kwargs
    ) -> str:
        """
        Generate a mock response based on the user's message.

        Args:
            messages: Conversation history
            max_new_tokens: Ignored in mock
            temperature: Ignored in mock

        Returns:
            A mock patient response
        """
        # Get the last user message
        user_message = ""
        for msg in reversed(messages):
            if msg.get("role") == "user":
                user_message = msg.get("content", "").lower()
                break

        # Select appropriate response category
        if any(word in user_message for word in ["pain", "hurt", "ache", "sore"]):
            category = "pain"
        elif any(word in user_message for word in ["where", "location", "which tooth", "side"]):
            category = "location"
        elif any(word in user_message for word in ["when", "how long", "start", "began", "duration"]):
            category = "duration"
        elif any(word in user_message for word in ["trigger", "worse", "cause", "cold", "hot", "sweet"]):
            category = "trigger"
        else:
            category = "default"

        return random.choice(self.RESPONSES[category])


# Singleton instance
_mock_engine = None


def get_mock_engine() -> MockPatientEngine:
    """Get or create the mock engine instance."""
    global _mock_engine
    if _mock_engine is None:
        _mock_engine = MockPatientEngine()
    return _mock_engine

