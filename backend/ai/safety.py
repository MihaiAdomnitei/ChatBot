"""
Safety Utilities - Output validation and sanitization for medical AI.

This module provides:
- Output sanitization to prevent unsafe content
- Response validation for medical conversations
- Content filtering and safety checks
"""

import re
from typing import List, Tuple, Optional
from dataclasses import dataclass

from .config import SafetyConfig, DEFAULT_SAFETY_CONFIG


@dataclass
class SafetyCheckResult:
    """Result of a safety check on AI output."""

    is_safe: bool
    original_text: str
    sanitized_text: str
    warnings: List[str]
    blocked_phrases_found: List[str]

    def __bool__(self) -> bool:
        """Allow using result in boolean context."""
        return self.is_safe


class OutputSanitizer:
    """
    Sanitizes AI output for safety in medical contexts.

    This class performs:
    - Blocked phrase detection and removal
    - Length truncation
    - Medical disclaimer injection when needed
    """

    def __init__(self, config: SafetyConfig = None):
        """
        Initialize the sanitizer.

        Args:
            config: Safety configuration (uses default if not provided)
        """
        self.config = config or DEFAULT_SAFETY_CONFIG

    def sanitize(self, text: str) -> SafetyCheckResult:
        """
        Sanitize AI output text.

        Args:
            text: The AI-generated response text

        Returns:
            SafetyCheckResult with sanitization details
        """
        warnings = []
        blocked_found = []
        sanitized = text

        # Check for blocked phrases
        if self.config.sanitize_output:
            sanitized, blocked_found = self._remove_blocked_phrases(sanitized)
            if blocked_found:
                warnings.append(
                    f"Removed {len(blocked_found)} blocked phrase(s) from output"
                )

        # Truncate if too long
        if len(sanitized) > self.config.max_response_length:
            sanitized = sanitized[:self.config.max_response_length].rsplit(' ', 1)[0] + "..."
            warnings.append(
                f"Response truncated from {len(text)} to {len(sanitized)} characters"
            )

        # Determine if output is safe
        is_safe = len(blocked_found) == 0

        return SafetyCheckResult(
            is_safe=is_safe,
            original_text=text,
            sanitized_text=sanitized.strip(),
            warnings=warnings,
            blocked_phrases_found=blocked_found
        )

    def _remove_blocked_phrases(self, text: str) -> Tuple[str, List[str]]:
        """
        Remove blocked phrases from text.

        Args:
            text: Input text

        Returns:
            Tuple of (cleaned text, list of found blocked phrases)
        """
        found = []
        result = text

        for phrase in self.config.blocked_phrases:
            # Case-insensitive search
            pattern = re.compile(re.escape(phrase), re.IGNORECASE)
            if pattern.search(result):
                found.append(phrase)
                # Replace with ellipsis to maintain flow
                result = pattern.sub("...", result)

        return result, found

    def check_conversation_length(self, message_count: int) -> Optional[str]:
        """
        Check if conversation is getting too long.

        Args:
            message_count: Number of messages in conversation

        Returns:
            Warning message if conversation is too long, None otherwise
        """
        if message_count >= self.config.max_conversation_turns:
            return (
                f"Conversation has reached {message_count} messages. "
                "Consider starting a new session for accurate simulation."
            )
        return None


class ResponseValidator:
    """
    Validates AI responses for quality and safety.

    This performs additional checks beyond basic sanitization.
    """

    # Patterns that indicate the AI may have broken character
    BROKEN_CHARACTER_PATTERNS = [
        r"as an AI",
        r"as a language model",
        r"I cannot provide medical",
        r"I'm not a doctor",
        r"I am not a medical professional",
        r"I don't have access to",
    ]

    # Patterns indicating possible diagnosis disclosure
    DIAGNOSIS_DISCLOSURE_PATTERNS = [
        r"you have ([a-z]+ ){1,3}(disease|condition|syndrome|disorder)",
        r"this is (likely|probably|definitely) ([a-z]+ ){1,3}",
        r"I (think|believe) you have",
    ]

    def __init__(self):
        """Initialize the validator with compiled patterns."""
        self._broken_patterns = [
            re.compile(p, re.IGNORECASE) for p in self.BROKEN_CHARACTER_PATTERNS
        ]
        self._disclosure_patterns = [
            re.compile(p, re.IGNORECASE) for p in self.DIAGNOSIS_DISCLOSURE_PATTERNS
        ]

    def validate(self, response: str) -> Tuple[bool, List[str]]:
        """
        Validate an AI response.

        Args:
            response: The AI-generated response

        Returns:
            Tuple of (is_valid, list of issues found)
        """
        issues = []

        # Check for broken character
        for pattern in self._broken_patterns:
            if pattern.search(response):
                issues.append("AI may have broken character (meta-reference detected)")
                break

        # Check for diagnosis disclosure
        for pattern in self._disclosure_patterns:
            if pattern.search(response):
                issues.append("Possible diagnosis disclosure detected")
                break

        # Check for empty or very short response
        if len(response.strip()) < 5:
            issues.append("Response is too short")

        # Check for excessive repetition (simple check)
        words = response.lower().split()
        if len(words) > 10:
            word_set = set(words)
            if len(word_set) < len(words) * 0.3:  # Less than 30% unique words
                issues.append("Response contains excessive repetition")

        return len(issues) == 0, issues


# Singleton instances for convenience
_sanitizer: Optional[OutputSanitizer] = None
_validator: Optional[ResponseValidator] = None


def get_sanitizer() -> OutputSanitizer:
    """Get the global sanitizer instance."""
    global _sanitizer
    if _sanitizer is None:
        _sanitizer = OutputSanitizer()
    return _sanitizer


def get_validator() -> ResponseValidator:
    """Get the global validator instance."""
    global _validator
    if _validator is None:
        _validator = ResponseValidator()
    return _validator


def sanitize_response(text: str) -> str:
    """
    Convenience function to sanitize a response.

    Args:
        text: AI-generated response text

    Returns:
        Sanitized text
    """
    result = get_sanitizer().sanitize(text)
    return result.sanitized_text


def validate_response(text: str) -> Tuple[bool, List[str]]:
    """
    Convenience function to validate a response.

    Args:
        text: AI-generated response text

    Returns:
        Tuple of (is_valid, list of issues)
    """
    return get_validator().validate(text)

