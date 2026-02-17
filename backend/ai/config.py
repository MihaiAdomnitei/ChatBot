"""
AI Configuration - Generation parameters and safety constraints.

This module provides:
- Validated generation parameters
- Safety boundaries for medical AI
- Configuration presets for different use cases
"""

from dataclasses import dataclass, field
from enum import Enum


class GenerationPreset(str, Enum):
    """Predefined generation parameter presets."""

    # Conservative: Low creativity, high consistency (medical recommended)
    CONSERVATIVE = "conservative"

    # Balanced: Moderate creativity with safety
    BALANCED = "balanced"

    # Creative: Higher variability (testing only)
    CREATIVE = "creative"


@dataclass
class GenerationConfig:
    """
    Validated generation parameters for the AI model.

    All parameters are validated to ensure they fall within
    safe ranges for medical conversation simulation.

    Attributes:
        max_new_tokens: Maximum tokens in response (10-500)
        temperature: Sampling randomness (0.0-1.5)
        top_p: Nucleus sampling threshold (0.0-1.0)
        repetition_penalty: Penalty for repeating tokens (1.0-2.0)
    """

    max_new_tokens: int = 100
    temperature: float = 0.4
    top_p: float = 0.9
    repetition_penalty: float = 1.1

    # Safety boundaries (class-level constants)
    MIN_TOKENS: int = field(default=10, init=False, repr=False)
    MAX_TOKENS: int = field(default=500, init=False, repr=False)
    MIN_TEMPERATURE: float = field(default=0.0, init=False, repr=False)
    MAX_TEMPERATURE: float = field(default=1.5, init=False, repr=False)
    MIN_TOP_P: float = field(default=0.0, init=False, repr=False)
    MAX_TOP_P: float = field(default=1.0, init=False, repr=False)
    MIN_REPETITION_PENALTY: float = field(default=1.0, init=False, repr=False)
    MAX_REPETITION_PENALTY: float = field(default=2.0, init=False, repr=False)

    def __post_init__(self):
        """Validate all parameters after initialization."""
        self.validate()

    def validate(self) -> None:
        """
        Validate all parameters are within safe ranges.

        Raises:
            ValueError: If any parameter is out of range
        """
        if not (self.MIN_TOKENS <= self.max_new_tokens <= self.MAX_TOKENS):
            raise ValueError(
                f"max_new_tokens must be between {self.MIN_TOKENS} and {self.MAX_TOKENS}, "
                f"got {self.max_new_tokens}"
            )

        if not (self.MIN_TEMPERATURE <= self.temperature <= self.MAX_TEMPERATURE):
            raise ValueError(
                f"temperature must be between {self.MIN_TEMPERATURE} and {self.MAX_TEMPERATURE}, "
                f"got {self.temperature}"
            )

        if not (self.MIN_TOP_P <= self.top_p <= self.MAX_TOP_P):
            raise ValueError(
                f"top_p must be between {self.MIN_TOP_P} and {self.MAX_TOP_P}, "
                f"got {self.top_p}"
            )

        if not (self.MIN_REPETITION_PENALTY <= self.repetition_penalty <= self.MAX_REPETITION_PENALTY):
            raise ValueError(
                f"repetition_penalty must be between {self.MIN_REPETITION_PENALTY} and {self.MAX_REPETITION_PENALTY}, "
                f"got {self.repetition_penalty}"
            )

    @classmethod
    def from_preset(cls, preset: GenerationPreset) -> 'GenerationConfig':
        """
        Create a configuration from a named preset.

        Args:
            preset: The preset to use

        Returns:
            GenerationConfig with preset values
        """
        presets = {
            GenerationPreset.CONSERVATIVE: {
                "max_new_tokens": 80,
                "temperature": 0.3,
                "top_p": 0.85,
                "repetition_penalty": 1.15
            },
            GenerationPreset.BALANCED: {
                "max_new_tokens": 100,
                "temperature": 0.4,
                "top_p": 0.9,
                "repetition_penalty": 1.1
            },
            GenerationPreset.CREATIVE: {
                "max_new_tokens": 150,
                "temperature": 0.7,
                "top_p": 0.95,
                "repetition_penalty": 1.05
            }
        }
        return cls(**presets[preset])

    def to_dict(self) -> dict:
        """Convert to dictionary for passing to generate()."""
        return {
            "max_new_tokens": self.max_new_tokens,
            "temperature": self.temperature,
            "top_p": self.top_p,
            "repetition_penalty": self.repetition_penalty
        }


# Default configuration (conservative for medical use)
DEFAULT_CONFIG = GenerationConfig.from_preset(GenerationPreset.CONSERVATIVE)


@dataclass
class SafetyConfig:
    """
    Safety configuration for medical AI conversations.

    These settings control content filtering and safety measures.
    """

    # Maximum conversation length before suggesting reset
    max_conversation_turns: int = 50

    # Maximum response length for safety truncation
    max_response_length: int = 1000

    # Enable output sanitization
    sanitize_output: bool = True

    # Keywords that should never appear in output
    blocked_phrases: list = field(default_factory=lambda: [
        "I diagnose",
        "My diagnosis is",
        "You have",
        "The diagnosis is",
        "I prescribe",
        "Take this medication",
        "You should take",
        "I recommend you take",
    ])

    # Disclaimer to append if needed
    safety_disclaimer: str = (
        "Note: This is a simulated patient for training purposes only. "
        "Do not use for actual medical diagnosis."
    )


# Default safety configuration
DEFAULT_SAFETY_CONFIG = SafetyConfig()

