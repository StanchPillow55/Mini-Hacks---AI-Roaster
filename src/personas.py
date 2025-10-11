"""
Personas module for AI Roaster.

Provides personality templates and style prompt construction for roast generation.
Each persona has distinct tone markers, slang, content guardrails, and mildness scaling.

Example usage:
    >>> from personas import build_style_prompt, PERSONAS
    >>> 
    >>> # Get available personas
    >>> list(PERSONAS.keys())
    ['gen_z', 'millennial', 'boomer', 'corporate', 'shakespearean']
    >>> 
    >>> # Build a mild Gen Z roast prompt
    >>> style = build_style_prompt('gen_z', 'loves pumpkin spice', mildness=0.3)
    >>> print(style)
    Tone: sarcastic, playful, self-aware
    Slang: no cap, fr fr, delulu, slay, bestie
    Target: loves pumpkin spice
    Intensity: mild (30%)
    Guardrails: No hate speech, slurs, sexual content, or attacks on protected classes.
    
    >>> # Build a spicy Shakespearean roast
    >>> style = build_style_prompt('shakespearean', 'terrible fashion sense', mildness=0.9)
    >>> print(style)
    Tone: eloquent, dramatic, theatrical
    Slang: thou, thee, dost, verily, forsooth
    Target: terrible fashion sense
    Intensity: spicy (90%)
    Guardrails: No hate speech, slurs, sexual content, or attacks on protected classes.
"""

# Persona style templates
PERSONAS = {
    'gen_z': {
        'name': 'Gen Z',
        'tone': 'sarcastic, playful, self-aware',
        'slang': ['no cap', 'fr fr', 'delulu', 'slay', 'bestie', 'ate', 'giving', 'main character energy'],
        'style_notes': 'Use internet culture, memes, lowercase aesthetic. Heavy on irony and self-deprecation.',
        'banned_content': 'No slurs, hate speech, or attacks on identity. Avoid sexual content.',
        'mildness_multiplier': 1.0,  # baseline
    },
    'millennial': {
        'name': 'Millennial',
        'tone': 'nostalgic, self-deprecating, exhausted',
        'slang': ['adulting', 'yeet', 'lit', 'lowkey', 'highkey', 'savage', 'salty'],
        'style_notes': 'Reference 90s/2000s culture, avocado toast, student loans, existential dread.',
        'banned_content': 'No slurs, hate speech, or attacks on identity. Avoid sexual content.',
        'mildness_multiplier': 0.9,  # slightly softer
    },
    'boomer': {
        'name': 'Boomer',
        'tone': 'grumpy, traditional, judgy',
        'slang': ['back in my day', 'kids these days', 'whippersnapper', 'malarkey', 'hogwash'],
        'style_notes': 'Complain about technology, work ethic, participation trophies. Old-school dad energy.',
        'banned_content': 'No slurs, hate speech, or attacks on identity. Avoid sexual content.',
        'mildness_multiplier': 0.8,  # more crotchety but ultimately harmless
    },
    'corporate': {
        'name': 'Corporate',
        'tone': 'passive-aggressive, buzzword-heavy, fake-polite',
        'slang': ['synergy', 'circle back', 'let\'s take this offline', 'low-hanging fruit', 'move the needle', 'bandwidth'],
        'style_notes': 'Frame roasts as performance reviews. Use corporate jargon. Backhanded compliments.',
        'banned_content': 'No slurs, hate speech, or attacks on identity. Avoid sexual content.',
        'mildness_multiplier': 0.7,  # subtle but cutting
    },
    'shakespearean': {
        'name': 'Shakespearean',
        'tone': 'eloquent, dramatic, theatrical',
        'slang': ['thou', 'thee', 'dost', 'verily', 'forsooth', 'prithee', 'varlet', 'knave'],
        'style_notes': 'Use iambic meter when possible. Reference classic insults (lout, cur, etc). Flowery language.',
        'banned_content': 'No slurs, hate speech, or attacks on identity. Avoid sexual content.',
        'mildness_multiplier': 1.2,  # can be more dramatic/intense
    },
}


def build_style_prompt(persona: str, custom_text: str = '', mildness: float = 0.5) -> str:
    """
    Build a compact style prompt for roast generation.
    
    Args:
        persona: Key from PERSONAS dict ('gen_z', 'millennial', etc.)
        custom_text: Optional custom roast target or context
        mildness: Float 0.0-1.0, where 0.0 is gentle and 1.0 is maximum spice
        
    Returns:
        Formatted style prompt string with tone, slang, target, intensity, and guardrails
        
    Raises:
        KeyError: If persona is not found in PERSONAS dict
        
    Examples:
        >>> build_style_prompt('gen_z', 'obsessed with crypto', 0.2)
        'Tone: sarcastic, playful, self-aware\\n...'
        
        >>> build_style_prompt('corporate', mildness=0.8)
        'Tone: passive-aggressive, buzzword-heavy, fake-polite\\n...'
    """
    if persona not in PERSONAS:
        raise KeyError(f"Persona '{persona}' not found. Available: {list(PERSONAS.keys())}")
    
    p = PERSONAS[persona]
    
    # Adjust mildness by persona multiplier
    adjusted_mildness = min(1.0, mildness * p['mildness_multiplier'])
    
    # Format intensity label
    if adjusted_mildness < 0.3:
        intensity_label = f"mild ({int(adjusted_mildness * 100)}%)"
    elif adjusted_mildness < 0.7:
        intensity_label = f"medium ({int(adjusted_mildness * 100)}%)"
    else:
        intensity_label = f"spicy ({int(adjusted_mildness * 100)}%)"
    
    # Build prompt
    slang_str = ', '.join(p['slang'][:5])  # limit to first 5 for brevity
    
    prompt_parts = [
        f"Tone: {p['tone']}",
        f"Slang: {slang_str}",
    ]
    
    if custom_text:
        prompt_parts.append(f"Target: {custom_text}")
    
    prompt_parts.extend([
        f"Intensity: {intensity_label}",
        f"Style notes: {p['style_notes']}",
        f"Guardrails: {p['banned_content']}",
    ])
    
    return '\n'.join(prompt_parts)


def get_persona_names() -> list[str]:
    """Return list of available persona keys."""
    return list(PERSONAS.keys())


def get_persona_display_name(persona: str) -> str:
    """Return human-readable name for a persona."""
    return PERSONAS.get(persona, {}).get('name', persona)
