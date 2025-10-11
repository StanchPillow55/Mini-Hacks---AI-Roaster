"""Toxicity checking using Detoxify (offline, no API key needed)"""

import re
from typing import Dict
from detoxify import Detoxify

# Global model instance (lazy loaded)
_MODEL = None


def _get_model() -> Detoxify:
    """
    Get or create Detoxify model instance (lazy loading).
    
    Returns:
        Detoxify model instance (unbiased)
    """
    global _MODEL
    if _MODEL is None:
        print("Loading Detoxify model (unbiased)...")
        _MODEL = Detoxify('unbiased')
        print("✅ Detoxify model loaded successfully")
    return _MODEL


def score_toxicity(text: str) -> Dict[str, float]:
    """
    Score toxicity using Detoxify (offline).
    
    Args:
        text: Text to analyze
        
    Returns:
        Dict with single key "toxicity" -> float score 0.0-1.0
    """
    model = _get_model()
    predictions = model.predict(text)
    return {"toxicity": float(predictions["toxicity"])}


def map_label(score: float, mode: str) -> str:
    """
    Map toxicity score to safety label based on mode threshold.
    
    Args:
        score: Toxicity score (0.0-1.0)
        mode: 'mild', 'normal', or 'brutal'
        
    Returns:
        'ok' if below threshold, 'too_hot' if above
    """
    # Mode thresholds
    thresholds = {
        "mild": 0.15,
        "normal": 0.30,
        "brutal": 0.50
    }
    
    threshold = thresholds.get(mode.lower(), 0.30)  # Default to normal
    return "ok" if score < threshold else "too_hot"


def enforce_mildness(text: str, target: str = "mild") -> str:
    """
    Reduce intensity by heuristics without altering core meaning.
    
    Uses simple heuristics:
    - Lowercase shout words (ALL CAPS)
    - Replace common profanity with hints
    - Soften intensifiers
    - Remove slurs from common list
    - Trim ad hominem attacks
    
    Args:
        text: Original text to soften
        target: Target level ('mild' applies all, others minimal)
        
    Returns:
        Softened text
    """
    if target.lower() in ["normal", "spicy", "brutal"]:
        # No changes for non-mild modes
        return text
    
    result = text
    
    # 1. Lower-case shout words (ALL CAPS -> Capitalized)
    def soften_caps(match):
        word = match.group(0)
        if len(word) <= 3:  # Keep acronyms
            return word
        return word.capitalize()
    
    result = re.sub(r'\b[A-Z]{4,}\b', soften_caps, result)
    
    # 2. Replace profanity with hints
    profanity_map = {
        r'\bfuck\w*\b': 'f***',
        r'\bshit\w*\b': 's***',
        r'\bdamn\w*\b': 'd***',
        r'\bcrap\w*\b': 'c***',
        r'\bass\b': 'a**',
        r'\bhell\b': 'h***',
    }
    for pattern, replacement in profanity_map.items():
        result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
    
    # 3. Soften intensifiers
    intensifier_map = {
        r'\babsolute(ly)?\b': 'somewhat',
        r'\btotally?\b': 'kind of',
        r'\bcompletely?\b': 'mostly',
        r'\bextremely?\b': 'quite',
        r'\bterrible\b': 'not great',
        r'\bawful\b': 'subpar',
        r'\bpathetic\b': 'disappointing',
        r'\bidiot\b': 'silly person',
        r'\bstupid\b': 'not the brightest',
        r'\bdumb\b': 'not too sharp',
    }
    for pattern, replacement in intensifier_map.items():
        result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
    
    # 4. Remove slurs list (common offensive terms)
    slurs = [
        r'\bloser\b',
        r'\bmoron\b',
        r'\bimbecile\b',
        r'\bretard\w*\b',
    ]
    for slur_pattern in slurs:
        result = re.sub(slur_pattern, '[removed]', result, flags=re.IGNORECASE)
    
    # 5. Trim ad hominems (personal attacks)
    ad_hominem_patterns = [
        r'\byou\'?re (a |an )?(terrible|awful|disgusting|pathetic)\b',
        r'\byou suck\b',
        r'\byou\'?re garbage\b',
    ]
    for pattern in ad_hominem_patterns:
        result = re.sub(pattern, "that's not ideal", result, flags=re.IGNORECASE)
    
    # 6. Remove excessive punctuation (!!! -> !)
    result = re.sub(r'!{2,}', '!', result)
    result = re.sub(r'\?{2,}', '?', result)
    
    return result


# Demo/test
if __name__ == "__main__":
    print("=" * 70)
    print("TOXICITY MODULE TEST - Step 7 Specification")
    print("=" * 70)
    print()
    
    # Three sample lines as requested
    samples = [
        "Your code is absolutely terrible and you're an idiot!",
        "This looks like a beginner made it, but keep trying.",
        "Nice work! Clean and efficient."
    ]
    
    for i, line in enumerate(samples, 1):
        print(f"Sample {i}: \"{line}\"")
        
        # Score
        result = score_toxicity(line)
        score = result["toxicity"]
        print(f"  Toxicity score: {score:.3f}")
        
        # Label for each mode
        for mode in ["mild", "normal", "brutal"]:
            label = map_label(score, mode)
            print(f"    {mode.capitalize()} mode: {label}")
        
        # Enforce mildness
        if score > 0.15:  # Only soften if needed
            softened = enforce_mildness(line, "mild")
            print(f"  Softened: \"{softened}\"")
        
        print()
