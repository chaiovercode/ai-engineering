# Tone modifiers for different content styles
# These are appended to the base prompts to adjust the output style

from enum import Enum


class Tone(str, Enum):
    PROFESSIONAL = "professional"
    CONVERSATIONAL = "conversational"
    PUNCHY = "punchy"


TONE_MODIFIERS = {
    Tone.PROFESSIONAL: """
Tone: Professional
- Use formal, data-driven language
- Emphasize expertise and authority
- Include specific numbers and metrics
- Maintain a measured, analytical voice
- Focus on credibility and institutional perspective
""",
    Tone.CONVERSATIONAL: """
Tone: Conversational
- Use friendly, approachable language
- Write as if explaining to a smart friend
- Include relatable analogies where appropriate
- Keep sentences natural and flowing
- Balance information with engagement
""",
    Tone.PUNCHY: """
Tone: Punchy
- Lead with bold, attention-grabbing statements
- Use short, impactful sentences
- Create urgency without being alarmist
- Make every word count
- End with a strong call to action or takeaway
""",
}


def get_tone_modifier(tone: Tone) -> str:
    """Get the tone modifier string for a given tone."""
    return TONE_MODIFIERS.get(tone, TONE_MODIFIERS[Tone.PROFESSIONAL])
