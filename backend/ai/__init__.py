"""
AI Module - Core AI components for patient simulation.

This module exposes:
- PatientChatEngine: The AI inference engine
- ChatManager: Conversation session management
- build_patient_prompt: Prompt construction utilities
- PATIENT_PROFILES: Predefined patient symptom profiles
- PathologyEnum: Supported pathology types
- GenerationConfig: AI generation parameter configuration
- Safety utilities: Output sanitization and validation
"""

from .patient_engine import PatientChatEngine
from .chat_manager import ChatManager, ChatSession, ChatPersistence, InMemoryPersistence
from .prompt_builder import (
    build_patient_prompt,
    build_minimal_prompt,
    build_context_injection,
    build_opening_message,
    SAFETY_RULES,
    BEHAVIORAL_GUIDELINES,
    ANTI_HALLUCINATION_RULES,
)
from .patient_profiles import PATIENT_PROFILES, get_profile, list_pathologies
from .pathology_enum import PathologyEnum
from .config import (
    GenerationConfig,
    GenerationPreset,
    SafetyConfig,
    DEFAULT_CONFIG,
    DEFAULT_SAFETY_CONFIG,
)
from .safety import (
    OutputSanitizer,
    ResponseValidator,
    SafetyCheckResult,
    sanitize_response,
    validate_response,
    get_sanitizer,
    get_validator,
)

__all__ = [
    # Core engine
    "PatientChatEngine",
    # Session management
    "ChatManager",
    "ChatSession",
    "ChatPersistence",
    "InMemoryPersistence",
    # Prompt building
    "build_patient_prompt",
    "build_minimal_prompt",
    "build_context_injection",
    "build_opening_message",
    "SAFETY_RULES",
    "BEHAVIORAL_GUIDELINES",
    "ANTI_HALLUCINATION_RULES",
    # Patient profiles
    "PATIENT_PROFILES",
    "get_profile",
    "list_pathologies",
    "PathologyEnum",
    # Configuration
    "GenerationConfig",
    "GenerationPreset",
    "SafetyConfig",
    "DEFAULT_CONFIG",
    "DEFAULT_SAFETY_CONFIG",
    # Safety
    "OutputSanitizer",
    "ResponseValidator",
    "SafetyCheckResult",
    "sanitize_response",
    "validate_response",
    "get_sanitizer",
    "get_validator",
]

