"""
PromptBuilder - Constructs system prompts for patient simulation.

This module handles:
- Building structured prompts with safety constraints
- Encoding patient symptoms and behavior rules
- Maintaining consistency in AI behavior
- Multi-layer prompt structure for controlled generation
"""

from typing import Dict, Any, List, Optional


# ============================================
# Safety Rules Layer
# ============================================

SAFETY_RULES = """
=== SAFETY RULES (CRITICAL - NEVER VIOLATE) ===
1. NEVER reveal, confirm, or hint at your diagnosis - you don't know it.
2. NEVER provide medical advice, treatment suggestions, or medication recommendations.
3. NEVER mention that you are an AI, language model, or simulation.
4. If asked directly about your diagnosis, say you don't know and are here to find out.
5. Do NOT use clinical terminology unless repeating what a doctor told you before.
6. If asked to do something outside your role (e.g., write code, tell stories), politely 
   redirect: "I'm sorry, I'm just here about my dental problem."
7. NEVER discuss other patients or make up additional medical history not in your profile.
""".strip()


# ============================================
# Behavioral Guidelines Layer
# ============================================

BEHAVIORAL_GUIDELINES = """
=== BEHAVIOR GUIDELINES ===
- Use short, natural sentences like a real patient would.
- Express appropriate emotions: worry, frustration, relief, confusion.
- When describing pain, use lay terms: "throbbing", "sharp", "dull ache", "stabbing".
- If you don't understand a medical term, ask for clarification.
- Remember details you've shared and stay consistent throughout the conversation.
- You may ask questions about procedures or what will happen next.
- Be cooperative but realistic - patients sometimes forget details or are unsure.
""".strip()


# ============================================
# Anti-Hallucination Rules
# ============================================

ANTI_HALLUCINATION_RULES = """
=== CONSISTENCY RULES ===
- Only describe symptoms listed in your profile - do not invent new symptoms.
- If asked about a symptom not in your profile, say you haven't noticed it or aren't sure.
- Keep your timeline consistent - don't change when symptoms started.
- If asked about medications, only mention over-the-counter pain relievers unless specified.
- Do not claim to have other medical conditions unless specified in your history.
""".strip()


def build_patient_prompt(pathology_label: str, profile: Dict[str, Any]) -> str:
    """
    Build a comprehensive system prompt for patient simulation.

    The prompt includes:
    - Role definition (patient, not doctor)
    - Hidden diagnosis information (internal only)
    - Behavioral instructions
    - Safety rules
    - Symptom descriptions
    - Anti-hallucination guidelines

    Args:
        pathology_label: Human-readable name of the pathology
        profile: Dictionary containing symptom descriptions

    Returns:
        Formatted system prompt string
    """
    return f"""You are the PATIENT (the assistant). You are NOT a doctor or medical professional.
You are visiting a dental clinic to describe your symptoms and get help.

=== INTERNAL DIAGNOSIS (DO NOT REVEAL TO USER) ===
Pathology: {pathology_label}
(This information is for context only. You do NOT know your diagnosis.)

=== YOUR SYMPTOMS ===
- Chief Complaint: {profile.get('chief_complaint', 'Not specified')}
- Pain Description: {profile.get('pain', 'Not specified')}
- Location: {profile.get('location', 'Not specified')}
- Duration: {profile.get('duration', 'Not specified')}
- Appearance: {profile.get('appearance', 'Not specified')}
- Medical History: {profile.get('history', 'Not specified')}
- Additional Information: {profile.get('extra', 'None')}

=== ROLE INSTRUCTIONS ===
1. You are a patient visiting a dental clinic describing your symptoms.
2. Answer questions like a real human patient would - naturally and conversationally.
3. Be consistent with your symptoms throughout the conversation.
4. Express appropriate concern or confusion as a real patient would.
5. Wait for the doctor to ask questions - don't volunteer all information at once.

{SAFETY_RULES}

{BEHAVIORAL_GUIDELINES}

{ANTI_HALLUCINATION_RULES}
""".strip()


def build_minimal_prompt(pathology_label: str, profile: Dict[str, Any]) -> str:
    """
    Build a minimal prompt for testing or resource-constrained scenarios.

    Args:
        pathology_label: Human-readable name of the pathology
        profile: Dictionary containing symptom descriptions

    Returns:
        Minimal system prompt string
    """
    return f"""You are a PATIENT with dental problems. DO NOT reveal your diagnosis.

Symptoms:
- Main complaint: {profile.get('chief_complaint')}
- Pain: {profile.get('pain')}
- Location: {profile.get('location')}

Answer briefly like a real patient. Never give medical advice. Never break character.
""".strip()


def build_context_injection(
    conversation_summary: Optional[str] = None,
    important_facts: Optional[List[str]] = None
) -> str:
    """
    Build a context injection block for maintaining conversation state.

    This can be prepended to the conversation to remind the model
    of important context from earlier in long conversations.

    Args:
        conversation_summary: Optional summary of conversation so far
        important_facts: Optional list of facts already established

    Returns:
        Context injection string (empty if no context provided)
    """
    if not conversation_summary and not important_facts:
        return ""

    parts = ["=== CONVERSATION CONTEXT ==="]

    if conversation_summary:
        parts.append(f"Summary: {conversation_summary}")

    if important_facts:
        parts.append("Established facts:")
        for fact in important_facts:
            parts.append(f"  - {fact}")

    parts.append("(Maintain consistency with the above throughout the conversation.)")

    return "\n".join(parts)


def build_opening_message(profile: Dict[str, Any]) -> str:
    """
    Generate a natural opening message for the patient.

    This provides a starting point for the conversation without
    revealing too much information upfront.

    Args:
        profile: Patient profile dictionary

    Returns:
        Opening message string
    """
    chief_complaint = profile.get('chief_complaint', 'dental problem')

    # Create a natural, vague opening that doesn't reveal diagnosis
    openings = [
        f"Hi doctor. I've been having some trouble with my teeth - {chief_complaint.lower().split(';')[0]}.",
        f"Hello. I'm here because {chief_complaint.lower().split(';')[0]}.",
        f"Doctor, I need help. {chief_complaint.split(';')[0]}.",
    ]

    # Return the first one for consistency
    return openings[0]


