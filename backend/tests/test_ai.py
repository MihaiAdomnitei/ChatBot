"""
Test Suite - AI Component Tests

Tests for AI-specific components:
- Prompt building
- Safety sanitization
- Response validation
- Configuration
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.ai.prompt_builder import (
    build_patient_prompt,
    build_minimal_prompt,
    build_context_injection,
    SAFETY_RULES,
    ANTI_HALLUCINATION_RULES,
)
from backend.ai.safety import (
    OutputSanitizer,
    ResponseValidator,
    sanitize_response,
    validate_response,
)
from backend.ai.config import (
    GenerationConfig,
    GenerationPreset,
    SafetyConfig,
)
from backend.ai.patient_profiles import PATIENT_PROFILES, get_profile, list_pathologies
from backend.ai.pathology_enum import PathologyEnum


# ============================================
# Prompt Builder Tests
# ============================================

class TestPromptBuilder:
    """Tests for prompt building functions."""

    def test_build_patient_prompt_structure(self):
        """Test that patient prompt contains required sections."""
        profile = PATIENT_PROFILES["dental_caries"]
        prompt = build_patient_prompt("Dental Caries", profile)

        assert "PATIENT" in prompt
        assert "SAFETY RULES" in prompt
        assert "SYMPTOMS" in prompt
        assert "BEHAVIOR" in prompt
        assert "Dental Caries" in prompt

    def test_build_patient_prompt_includes_symptoms(self):
        """Test that symptoms are included in prompt."""
        profile = PATIENT_PROFILES["periodontal_abscess"]
        prompt = build_patient_prompt("Periodontal Abscess", profile)

        assert profile["chief_complaint"] in prompt
        assert "Pain Description" in prompt
        assert "Location" in prompt

    def test_build_minimal_prompt(self):
        """Test minimal prompt generation."""
        profile = PATIENT_PROFILES["dental_caries"]
        prompt = build_minimal_prompt("Dental Caries", profile)

        assert "PATIENT" in prompt
        assert len(prompt) < len(build_patient_prompt("Dental Caries", profile))

    def test_build_context_injection_empty(self):
        """Test context injection with no context."""
        result = build_context_injection()
        assert result == ""

    def test_build_context_injection_with_summary(self):
        """Test context injection with summary."""
        result = build_context_injection(
            conversation_summary="Patient reported tooth pain"
        )
        assert "CONTEXT" in result
        assert "tooth pain" in result

    def test_build_context_injection_with_facts(self):
        """Test context injection with facts."""
        result = build_context_injection(
            important_facts=["Pain started 3 days ago", "No medications"]
        )
        assert "3 days ago" in result
        assert "No medications" in result


# ============================================
# Safety Tests
# ============================================

class TestOutputSanitizer:
    """Tests for output sanitization."""

    def test_sanitize_clean_text(self):
        """Test sanitizing clean text."""
        sanitizer = OutputSanitizer()
        result = sanitizer.sanitize("I have a toothache")

        assert result.is_safe
        assert result.sanitized_text == "I have a toothache"
        assert len(result.blocked_phrases_found) == 0

    def test_sanitize_blocked_phrase(self):
        """Test sanitizing text with blocked phrase."""
        config = SafetyConfig(blocked_phrases=["I diagnose"])
        sanitizer = OutputSanitizer(config)

        result = sanitizer.sanitize("I diagnose you with cavities")

        assert not result.is_safe
        assert "I diagnose" not in result.sanitized_text
        assert "I diagnose" in result.blocked_phrases_found

    def test_sanitize_truncates_long_text(self):
        """Test that long text is truncated."""
        config = SafetyConfig(max_response_length=50)
        sanitizer = OutputSanitizer(config)

        long_text = "This is a very long response " * 10
        result = sanitizer.sanitize(long_text)

        assert len(result.sanitized_text) <= 55  # Allow for ellipsis
        assert result.sanitized_text.endswith("...")

    def test_check_conversation_length_ok(self):
        """Test conversation length check - within limit."""
        sanitizer = OutputSanitizer()
        result = sanitizer.check_conversation_length(10)
        assert result is None

    def test_check_conversation_length_exceeded(self):
        """Test conversation length check - exceeded."""
        config = SafetyConfig(max_conversation_turns=20)
        sanitizer = OutputSanitizer(config)
        result = sanitizer.check_conversation_length(25)
        assert result is not None
        assert "25 messages" in result


class TestResponseValidator:
    """Tests for response validation."""

    def test_validate_good_response(self):
        """Test validating a good response."""
        validator = ResponseValidator()
        is_valid, issues = validator.validate(
            "I've been having this sharp pain in my lower right tooth for about three days now."
        )
        assert is_valid
        assert len(issues) == 0

    def test_validate_broken_character(self):
        """Test detecting broken character."""
        validator = ResponseValidator()
        is_valid, issues = validator.validate(
            "As an AI language model, I cannot provide medical advice."
        )
        assert not is_valid
        assert any("broken character" in issue.lower() for issue in issues)

    def test_validate_diagnosis_disclosure(self):
        """Test detecting diagnosis disclosure."""
        validator = ResponseValidator()
        is_valid, issues = validator.validate(
            "I think you have dental caries based on these symptoms."
        )
        assert not is_valid
        assert any("diagnosis" in issue.lower() for issue in issues)

    def test_validate_too_short(self):
        """Test detecting too short response."""
        validator = ResponseValidator()
        is_valid, issues = validator.validate("Hi")
        assert not is_valid
        assert any("too short" in issue.lower() for issue in issues)

    def test_validate_excessive_repetition(self):
        """Test detecting excessive repetition."""
        validator = ResponseValidator()
        is_valid, issues = validator.validate(
            "pain pain pain pain pain pain pain pain pain pain pain pain"
        )
        assert not is_valid
        assert any("repetition" in issue.lower() for issue in issues)


class TestConvenienceFunctions:
    """Tests for convenience functions."""

    def test_sanitize_response(self):
        """Test sanitize_response function."""
        result = sanitize_response("I have a toothache")
        assert isinstance(result, str)
        assert result == "I have a toothache"

    def test_validate_response(self):
        """Test validate_response function."""
        is_valid, issues = validate_response("Normal patient response here.")
        assert isinstance(is_valid, bool)
        assert isinstance(issues, list)


# ============================================
# Configuration Tests
# ============================================

class TestGenerationConfig:
    """Tests for generation configuration."""

    def test_default_config(self):
        """Test default configuration."""
        config = GenerationConfig()
        assert config.max_new_tokens == 100
        assert config.temperature == 0.4

    def test_valid_config(self):
        """Test valid custom configuration."""
        config = GenerationConfig(
            max_new_tokens=150,
            temperature=0.5,
            top_p=0.85
        )
        assert config.max_new_tokens == 150
        assert config.temperature == 0.5

    def test_invalid_tokens_raises(self):
        """Test that invalid tokens raise error."""
        with pytest.raises(ValueError):
            GenerationConfig(max_new_tokens=1000)

    def test_invalid_temperature_raises(self):
        """Test that invalid temperature raises error."""
        with pytest.raises(ValueError):
            GenerationConfig(temperature=3.0)

    def test_preset_conservative(self):
        """Test conservative preset."""
        config = GenerationConfig.from_preset(GenerationPreset.CONSERVATIVE)
        assert config.temperature < 0.5

    def test_preset_creative(self):
        """Test creative preset."""
        config = GenerationConfig.from_preset(GenerationPreset.CREATIVE)
        assert config.temperature > 0.5

    def test_to_dict(self):
        """Test conversion to dictionary."""
        config = GenerationConfig()
        d = config.to_dict()
        assert "max_new_tokens" in d
        assert "temperature" in d
        assert "top_p" in d


# ============================================
# Patient Profile Tests
# ============================================

class TestPatientProfiles:
    """Tests for patient profiles."""

    def test_profiles_exist(self):
        """Test that profiles are defined."""
        assert len(PATIENT_PROFILES) > 0

    def test_all_profiles_have_required_fields(self):
        """Test that all profiles have required fields."""
        required_fields = ["label", "chief_complaint", "pain", "location"]

        for key, profile in PATIENT_PROFILES.items():
            for field in required_fields:
                assert field in profile, f"Profile {key} missing field {field}"

    def test_get_profile_exists(self):
        """Test getting existing profile."""
        profile = get_profile("dental_caries")
        assert profile is not None
        assert profile["label"] == "Simple Caries / No Pulpal Involvement"

    def test_get_profile_not_exists(self):
        """Test getting non-existent profile."""
        profile = get_profile("fake_disease")
        assert profile is None

    def test_list_pathologies(self):
        """Test listing all pathologies."""
        pathologies = list_pathologies()
        assert len(pathologies) > 0
        assert "dental_caries" in pathologies


class TestPathologyEnum:
    """Tests for pathology enumeration."""

    def test_enum_values(self):
        """Test enum has values."""
        assert len(PathologyEnum) > 0

    def test_list_values(self):
        """Test listing enum values."""
        values = PathologyEnum.list_values()
        assert "dental_caries" in values
        assert "periodontal_abscess" in values

    def test_is_valid_true(self):
        """Test is_valid for valid pathology."""
        assert PathologyEnum.is_valid("dental_caries")

    def test_is_valid_false(self):
        """Test is_valid for invalid pathology."""
        assert not PathologyEnum.is_valid("fake_disease")


# ============================================
# Run Tests
# ============================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])

