"""
PathologyEnum - Enumeration of supported dental pathologies.

This provides type-safe pathology selection and validation.
"""

from enum import Enum


class PathologyEnum(str, Enum):
    """
    Enumeration of dental pathologies supported by the patient simulator.

    Each value corresponds to a key in PATIENT_PROFILES.
    Inherits from str for JSON serialization compatibility.
    """

    PERIODONTAL_ABSCESS = "periodontal_abscess"
    DENTAL_CARIES = "dental_caries"
    PULPAL_NECROSIS = "pulpal_necrosis"
    CHRONIC_APICAL_PERIODONTITIS = "chronic_apical_periodontitis"
    ACUTE_APICAL_PERIODONTITIS = "acute_apical_periodontitis"
    PERICORONITIS = "pericoronitis"
    REVERSIBLE_PULPITIS = "reversible_pulpitis"
    ACUTE_TOTAL_PULPITIS = "acute_total_pulpitis"

    @classmethod
    def list_values(cls) -> list[str]:
        """Get all pathology values as strings."""
        return [p.value for p in cls]

    @classmethod
    def is_valid(cls, value: str) -> bool:
        """Check if a value is a valid pathology."""
        return value.lower() in cls.list_values()

