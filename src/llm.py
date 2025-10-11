"""LLM integration for roast generation using OpenAI or Anthropic"""

import os
import re
from typing import Dict, List, Optional, Any


# Safety system prompt to prevent harmful content
SAFETY_SYSTEM_PROMPT = """You are a witty roast generator. Your task is to create humorous, creative roasts based on user profiles.

SAFETY RULES (CRITICAL):
- NO slurs, hate speech, or derogatory language about protected classes (race, ethnicity, religion, gender, sexual orientation, disability, age)
- NO sexual or explicit content
- Focus on public information, choices, and behaviors - not immutable characteristics
- Keep it playful and clever, not cruel or personally attacking
- If you cannot generate a safe roast, respond with "Unable to generate appropriate roast for this profile."

EVIDENCE RULES (IMPORTANT):
- When you reference specific profile information in your roast, quote it EXACTLY in double quotes ""
- Examples:
  * Good: Your bio says "Python developer" but your repos are basic
  * Good: You posted "I love pumpkin spice" like it's a personality trait
  * Bad: Your bio mentions Python (no quotes)
- This helps users see what evidence you used

Your roast should be funny, creative, and based on the evidence provided."""


def _build_roast_prompt(profile: Dict[str, Any], style_prompt: str) -> str:
    """
    Build the complete roast prompt from profile data and style.
    
    Args:
        profile: Dictionary with profile data (name, bio, posts, etc.)
        style_prompt: Persona/style instructions for the roast
        
    Returns:
        Complete prompt string
    """
    # Extract profile information
    name = profile.get('name', 'User')
    bio = profile.get('bio', '')
    posts = profile.get('posts', [])
    interests = profile.get('interests', [])
    
    # Build evidence section
    evidence_parts = []
    if bio:
        evidence_parts.append(f"Bio: {bio}")
    if posts:
        evidence_parts.append(f"Recent posts: {posts[:3]}")  # Limit to first 3
    if interests:
        evidence_parts.append(f"Interests: {', '.join(interests[:5])}")
    
    evidence_text = "\n".join(evidence_parts) if evidence_parts else "Limited profile information available."
    
    # Combine style prompt with profile data
    full_prompt = f"""{style_prompt}

TARGET PROFILE:
Name: {name}
{evidence_text}

Generate a roast based on this profile information. Be witty and creative!"""
    
    return full_prompt


def _extract_evidence(profile: Dict[str, Any]) -> List[str]:
    """
    Extract evidence snippets used from the profile.
    
    Args:
        profile: Dictionary with profile data
        
    Returns:
        List of evidence snippets
    """
    evidence = []
    
    if profile.get('bio'):
        evidence.append(f"Bio: {profile['bio'][:100]}...")
    
    posts = profile.get('posts', [])
    for i, post in enumerate(posts[:3]):  # First 3 posts
        evidence.append(f"Post {i+1}: {post[:80]}...")
    
    interests = profile.get('interests', [])
    if interests:
        evidence.append(f"Interests: {', '.join(interests[:5])}")
    
    snippets = profile.get('snippets', [])
    for i, snippet in enumerate(snippets[:3]):  # First 3 snippets
        evidence.append(f"Snippet {i+1}: {snippet[:80]}...")
    
    return evidence if evidence else ["Limited profile data available"]


def _extract_quoted_evidence(roast_text: str, profile: Dict[str, Any]) -> List[Dict[str, str]]:
    """
    Extract quoted snippets from roast text and match them to profile sources.
    
    Args:
        roast_text: The generated roast text
        profile: Dictionary with profile data
        
    Returns:
        List of dicts with:
        - 'quote': The exact quote from the roast
        - 'source': Where it came from in the profile
        - 'context': Surrounding text for context
    """
    # Find all quoted text in roast using double quotes
    quoted_pattern = r'"([^"]+)"'
    quotes = re.findall(quoted_pattern, roast_text)
    
    evidence = []
    
    for quote in quotes:
        if len(quote) < 5:  # Skip very short quotes (likely not evidence)
            continue
            
        # Try to find this quote in profile data
        source_found = None
        
        # Check bio
        if profile.get('bio') and quote.lower() in profile['bio'].lower():
            source_found = f"Bio: {profile['bio'][:150]}..."
        
        # Check posts
        if not source_found:
            for post in profile.get('posts', []):
                if quote.lower() in str(post).lower():
                    source_found = f"Post: {str(post)[:150]}..."
                    break
        
        # Check snippets
        if not source_found:
            for snippet in profile.get('snippets', []):
                if quote.lower() in str(snippet).lower():
                    source_found = f"Profile data: {str(snippet)[:150]}..."
                    break
        
        # Check interests
        if not source_found:
            for interest in profile.get('interests', []):
                if quote.lower() in str(interest).lower():
                    source_found = f"Interest: {interest}"
                    break
        
        if source_found:
            evidence.append({
                'quote': quote,
                'source': source_found,
                'context': f'The AI referenced: "{quote}"'
            })
    
    # Fallback: if no quotes found, return basic evidence
    if not evidence:
        return [{'quote': '', 'source': s, 'context': s} for s in _extract_evidence(profile)]
    
    return evidence


def generate_roast_openai(profile: Dict[str, Any], style_prompt: str, temperature: float = 0.8) -> Dict[str, Any]:
    """
    Generate roast using OpenAI API.
    
    Args:
        profile: Profile dictionary with user data
        style_prompt: Persona/style instructions
        temperature: Creativity level (0.0-1.0)
        
    Returns:
        Dict with 'text' (roast) and 'evidence' (snippets used)
    """
    try:
        import openai
        import httpx
        
        api_key = os.environ.get("OPENAI_API_KEY")
        
        # Check if we should use demo mode
        use_demo = os.environ.get("USE_DEMO_MODE", "false").lower() == "true"
        
        if not api_key or use_demo:
            # Demo mode: return realistic-looking roast
            name = profile.get('name', 'User')
            bio = profile.get('bio', 'no bio')[:50]
            snippets = profile.get('snippets', [])
            
            demo_roast = f'''Yo, let's talk about "{name}" real quick... 😂

Your bio says "{bio}" - okay cool, and? That's giving "I made this profile in 5 minutes" energy. 

Looking at your activity, you got like {len(snippets)} things going on. Not even trying to flex or anything, just... existing. That's the vibe I'm getting.

But hey, at least you showed up, right? That's more than some people can say. Still roasting you though because why not? 🔥

[Note: DEMO MODE - Add API credits to get AI-generated roasts!]'''
            
            return {
                "text": demo_roast,
                "evidence": _extract_evidence(profile),
                "quoted_evidence": _extract_quoted_evidence(demo_roast, profile)
            }
        
        # Create httpx client without proxies to avoid the TypeError
        http_client = httpx.Client()
        
        # Initialize OpenAI client with custom http_client
        try:
            client = openai.OpenAI(api_key=api_key, http_client=http_client)
        except TypeError as e:
            # If that fails, try without http_client
            try:
                client = openai.OpenAI(api_key=api_key)
            except TypeError:
                # Fallback for older openai versions
                openai.api_key = api_key
                client = openai
        
        user_prompt = _build_roast_prompt(profile, style_prompt)
        
        # Try new API style first, fallback to old style
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": SAFETY_SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temperature,
                max_tokens=300
            )
            roast_text = response.choices[0].message.content.strip()
        except AttributeError:
            # Fallback to old API style
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": SAFETY_SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temperature,
                max_tokens=300
            )
            roast_text = response['choices'][0]['message']['content'].strip()
        
        evidence = _extract_evidence(profile)
        quoted_evidence = _extract_quoted_evidence(roast_text, profile)
        
        return {
            "text": roast_text,
            "evidence": evidence,
            "quoted_evidence": quoted_evidence
        }
    
    except ImportError:
        return {
            "text": "❌ Error: openai package not installed. Run: pip install openai",
            "evidence": [],
            "quoted_evidence": []
        }
    except Exception as e:
        return {
            "text": f"❌ Error generating roast with OpenAI: {str(e)}",
            "evidence": [],
            "quoted_evidence": []
        }


def generate_roast_anthropic(profile: Dict[str, Any], style_prompt: str, temperature: float = 0.8) -> Dict[str, Any]:
    """
    Generate roast using Anthropic Claude API.
    
    Args:
        profile: Profile dictionary with user data
        style_prompt: Persona/style instructions
        temperature: Creativity level (0.0-1.0)
        
    Returns:
        Dict with 'text' (roast) and 'evidence' (snippets used)
    """
    try:
        import anthropic
        
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            # Dry-run mode: return stub roast
            stub_roast = f"🎭 [DRY RUN] Your bio says \"{profile.get('bio', 'nothing')[:50]}\" but let's be real - this is just a placeholder roast. Set ANTHROPIC_API_KEY to get the real deal!"
            return {
                "text": stub_roast,
                "evidence": _extract_evidence(profile),
                "quoted_evidence": _extract_quoted_evidence(stub_roast, profile)
            }
        
        client = anthropic.Anthropic(api_key=api_key)
        
        user_prompt = _build_roast_prompt(profile, style_prompt)
        
        # Anthropic uses system parameter separately
        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=300,
            temperature=temperature,
            system=SAFETY_SYSTEM_PROMPT,
            messages=[
                {"role": "user", "content": user_prompt}
            ]
        )
        
        roast_text = message.content[0].text.strip()
        evidence = _extract_evidence(profile)
        quoted_evidence = _extract_quoted_evidence(roast_text, profile)
        
        return {
            "text": roast_text,
            "evidence": evidence,
            "quoted_evidence": quoted_evidence
        }
    
    except ImportError:
        return {
            "text": "❌ Error: anthropic package not installed. Run: pip install anthropic",
            "evidence": [],
            "quoted_evidence": []
        }
    except Exception as e:
        return {
            "text": f"❌ Error generating roast with Anthropic: {str(e)}",
            "evidence": [],
            "quoted_evidence": []
        }


def generate_roast(profile: Dict[str, Any], style_prompt: str, provider: str = "openai", temperature: float = 0.8) -> Dict[str, Any]:
    """
    Generate roast using specified LLM provider (or auto-detect).
    
    Args:
        profile: Profile dictionary with user data (name, bio, posts, interests, etc.)
        style_prompt: Persona/style instructions for the roast
        provider: 'openai' or 'anthropic' (defaults to 'openai')
        temperature: Creativity level (0.0-1.0)
        
    Returns:
        Dict with:
            - 'text': Generated roast text
            - 'evidence': List of profile snippets used as evidence
            - 'quoted_evidence': List of dicts with quoted snippets and their sources
    """
    # Auto-detect provider from environment if default requested
    if provider == "openai" and not os.environ.get("OPENAI_API_KEY"):
        # Try Anthropic as fallback
        if os.environ.get("ANTHROPIC_API_KEY"):
            provider = "anthropic"
    
    provider = provider.lower()
    
    if provider == "openai":
        return generate_roast_openai(profile, style_prompt, temperature)
    elif provider == "anthropic":
        return generate_roast_anthropic(profile, style_prompt, temperature)
    else:
        # Fallback: try OpenAI first, then Anthropic
        if os.environ.get("OPENAI_API_KEY"):
            return generate_roast_openai(profile, style_prompt, temperature)
        elif os.environ.get("ANTHROPIC_API_KEY"):
            return generate_roast_anthropic(profile, style_prompt, temperature)
        else:
            # Dry-run mode: no keys available
            stub_roast = f"🎭 [DRY RUN] Your bio says \"{profile.get('bio', 'nothing')[:50]}\" but let's be real - this is just a placeholder roast. Set OPENAI_API_KEY or ANTHROPIC_API_KEY to get the real deal!"
            return {
                "text": stub_roast,
                "evidence": _extract_evidence(profile),
                "quoted_evidence": _extract_quoted_evidence(stub_roast, profile)
            }


def get_available_providers() -> List[str]:
    """
    Check which LLM providers are configured.
    
    Returns:
        List of available provider names
    """
    providers = []
    
    if os.environ.get("OPENAI_API_KEY"):
        providers.append("openai")
    
    if os.environ.get("ANTHROPIC_API_KEY"):
        providers.append("anthropic")
    
    return providers
