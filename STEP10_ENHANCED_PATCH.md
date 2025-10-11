# Step 10 ENHANCED: Conversation Mode + Highlighted Evidence

This patch adds:
1. **Conversation Mode**: True back-and-forth with user input
2. **Highlighted Evidence**: LLM quotes specific snippets that are highlighted in the evidence display

## Changes Required

### 1. Update `src/llm.py` - Enhanced Evidence Extraction

Add to the system prompt to request quoted evidence:

```python
# In src/llm.py, update SAFETY_SYSTEM_PROMPT

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
```

Add helper to extract quoted evidence:

```python
import re

def _extract_quoted_evidence(roast_text: str, profile: Dict[str, Any]) -> List[Dict[str, str]]:
    """
    Extract quoted snippets from roast text and match them to profile sources.
    
    Returns list of dicts with:
    - 'quote': The exact quote from the roast
    - 'source': Where it came from in the profile
    - 'context': Surrounding text for context
    """
    # Find all quoted text in roast
    quoted_pattern = r'"([^"]+)"'
    quotes = re.findall(quoted_pattern, roast_text)
    
    evidence = []
    
    for quote in quotes:
        # Try to find this quote in profile data
        source_found = None
        
        # Check bio
        if profile.get('bio') and quote.lower() in profile['bio'].lower():
            source_found = f"Bio: {profile['bio'][:150]}..."
        
        # Check posts/snippets
        for snippet in profile.get('snippets', []):
            if quote.lower() in snippet.lower():
                source_found = f"Profile data: {snippet[:150]}..."
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


# Update generate_roast_openai to return enhanced evidence
def generate_roast_openai(profile: Dict[str, Any], style_prompt: str, temperature: float = 0.8) -> Dict[str, Any]:
    """Generate roast using OpenAI API with enhanced evidence."""
    try:
        import openai
        
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            return {
                "text": f"🎭 [DRY RUN] This is a stub roast for {profile.get('name', 'User')}. Set OPENAI_API_KEY to generate real roasts!",
                "evidence": _extract_evidence(profile),
                "quoted_evidence": []
            }
        
        client = openai.OpenAI(api_key=api_key)
        user_prompt = _build_roast_prompt(profile, style_prompt)
        
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": SAFETY_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            temperature=temperature,
            max_tokens=300
        )
        
        roast_text = response.choices[0].message.content.strip()
        evidence = _extract_evidence(profile)
        quoted_evidence = _extract_quoted_evidence(roast_text, profile)
        
        return {
            "text": roast_text,
            "evidence": evidence,
            "quoted_evidence": quoted_evidence  # NEW
        }
    
    except Exception as e:
        return {
            "text": f"❌ Error generating roast with OpenAI: {str(e)}",
            "evidence": [],
            "quoted_evidence": []
        }


# Update generate_roast_anthropic similarly
def generate_roast_anthropic(profile: Dict[str, Any], style_prompt: str, temperature: float = 0.8) -> Dict[str, Any]:
    """Generate roast using Anthropic Claude API with enhanced evidence."""
    try:
        import anthropic
        
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            return {
                "text": f"🎭 [DRY RUN] This is a stub roast for {profile.get('name', 'User')}. Set ANTHROPIC_API_KEY to generate real roasts!",
                "evidence": _extract_evidence(profile),
                "quoted_evidence": []
            }
        
        client = anthropic.Anthropic(api_key=api_key)
        user_prompt = _build_roast_prompt(profile, style_prompt)
        
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
            "quoted_evidence": quoted_evidence  # NEW
        }
    
    except Exception as e:
        return {
            "text": f"❌ Error generating roast with Anthropic: {str(e)}",
            "evidence": [],
            "quoted_evidence": []
        }
```

### 2. Complete Enhanced `streamlit_app.py`

```python
"""AI Roaster MVP - Conversation Mode + Enhanced Evidence"""

import streamlit as st
import urllib.parse
from typing import Dict, Any, List

# Import backend modules
from src.scrape_basic import extract_profile_from_url, extract_from_resume
from src.personas import build_style_prompt, PERSONAS, get_persona_names
from src.llm import generate_roast
from src.toxicity import score_toxicity, map_label, enforce_mildness
from src.share import format_copy_text

# Page config
st.set_page_config(
    page_title="AI Roaster MVP",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS
st.markdown("""
<style>
    .roast-box {
        padding: 20px;
        border-radius: 10px;
        background-color: #f0f2f6;
        margin: 10px 0;
        font-size: 18px;
        line-height: 1.6;
    }
    .user-response-box {
        padding: 15px;
        border-radius: 10px;
        background-color: #e3f2fd;
        margin: 10px 0;
        font-size: 16px;
        border-left: 4px solid #2196f3;
    }
    .conversation-thread {
        max-height: 600px;
        overflow-y: auto;
        padding: 10px;
        margin: 10px 0;
    }
    .toxicity-badge {
        display: inline-block;
        padding: 5px 15px;
        border-radius: 20px;
        font-weight: bold;
        margin: 5px;
    }
    .toxicity-low {
        background-color: #28a745;
        color: white;
    }
    .toxicity-medium {
        background-color: #ffc107;
        color: black;
    }
    .toxicity-high {
        background-color: #dc3545;
        color: white;
    }
    .evidence-highlight {
        background-color: #fff59d;
        padding: 2px 4px;
        border-radius: 3px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'roast_generated' not in st.session_state:
    st.session_state.roast_generated = False
if 'conversation_mode' not in st.session_state:
    st.session_state.conversation_mode = False
if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = []  # List of {'role': 'ai'|'user', 'text': str}
if 'current_roast' not in st.session_state:
    st.session_state.current_roast = ""
if 'toxicity_score' not in st.session_state:
    st.session_state.toxicity_score = 0.0
if 'toxicity_label' not in st.session_state:
    st.session_state.toxicity_label = "ok"
if 'sources_used' not in st.session_state:
    st.session_state.sources_used = []
if 'quoted_evidence' not in st.session_state:
    st.session_state.quoted_evidence = []
if 'profile_data' not in st.session_state:
    st.session_state.profile_data = None
if 'style_prompt' not in st.session_state:
    st.session_state.style_prompt = ""
if 'selected_mode' not in st.session_state:
    st.session_state.selected_mode = "normal"
if 'generation_count' not in st.session_state:
    st.session_state.generation_count = 0


def build_profile(uploaded_file, profile_url) -> Dict[str, Any]:
    """Build profile data from upload or URL."""
    if uploaded_file:
        file_bytes = uploaded_file.read()
        profile = extract_from_resume(file_bytes)
        profile['name'] = uploaded_file.name
        return profile
    elif profile_url:
        profile = extract_profile_from_url(profile_url)
        if 'github.com' in profile_url:
            username = profile_url.rstrip('/').split('/')[-1]
            profile['name'] = username
        else:
            profile['name'] = profile.get('titles', ['User'])[0] if profile.get('titles') else 'User'
        return profile
    else:
        return {"name": "User", "bio": "No profile data", "snippets": [], "sources": []}


def map_ui_mode_to_backend(ui_mode: str) -> str:
    """Map UI mode strings to backend mode strings."""
    mode_mapping = {
        "Mild 😊": "mild",
        "Normal 🌶️": "normal",
        "Brutal 💀": "brutal"
    }
    return mode_mapping.get(ui_mode, "normal")


def map_ui_persona_to_backend(ui_persona: str) -> str:
    """Map UI persona names to backend persona keys."""
    persona_mapping = {
        "IShowSpeed": "gen_z",
        "ElonMusk": "gen_z",
        "Coworker": "corporate",
        "GenZ": "gen_z",
        "Custom": "gen_z"
    }
    return persona_mapping.get(ui_persona, "gen_z")


def generate_ai_response(user_message: str = None) -> Dict[str, Any]:
    """Generate AI roast response, optionally in response to user message."""
    if not st.session_state.profile_data or not st.session_state.style_prompt:
        return {"text": "Error: No profile data available", "evidence": [], "quoted_evidence": []}
    
    # Build prompt with conversation context
    prompt = st.session_state.style_prompt
    
    if user_message:
        # Add conversation context
        context = "\n\nCONVERSATION CONTEXT:\n"
        for msg in st.session_state.conversation_history[-3:]:  # Last 3 messages
            role = "AI Roaster" if msg['role'] == 'ai' else "User"
            context += f"{role}: {msg['text']}\n"
        context += f"User: {user_message}\n\n"
        context += "Now respond to the user's message with another roast. Reference their response if relevant!"
        prompt = prompt + context
    
    # Generate roast
    roast_result = generate_roast(
        profile=st.session_state.profile_data,
        style_prompt=prompt,
        provider="openai",
        temperature=0.85
    )
    
    roast_text = roast_result['text']
    evidence = roast_result.get('evidence', [])
    quoted_evidence = roast_result.get('quoted_evidence', [])
    
    # Toxicity check and enforcement
    tox_result = score_toxicity(roast_text)
    tox_score = tox_result["toxicity"]
    label = map_label(tox_score, st.session_state.selected_mode)
    
    if label == "too_hot" or st.session_state.selected_mode == "mild":
        roast_text = enforce_mildness(roast_text, st.session_state.selected_mode)
        tox_result = score_toxicity(roast_text)
        tox_score = tox_result["toxicity"]
        label = map_label(tox_score, st.session_state.selected_mode)
    
    return {
        "text": roast_text,
        "evidence": evidence,
        "quoted_evidence": quoted_evidence,
        "toxicity_score": tox_score,
        "toxicity_label": label
    }


# Header
st.title("🔥 AI Roaster MVP")
st.markdown("**Get roasted by AI with style and safety checks** 🌶️")
st.markdown("---")

# Main content
col1, col2 = st.columns([1, 1])

with col1:
    st.header("📤 Input")
    
    # File upload
    st.subheader("Upload File (Optional)")
    uploaded_file = st.file_uploader(
        "Upload profile screenshot or text file",
        type=["png", "jpg", "jpeg", "txt", "pdf"],
        help="Upload a screenshot or text file containing profile information"
    )
    
    if uploaded_file:
        st.success(f"✅ File uploaded: {uploaded_file.name}")
    
    st.markdown("---")
    
    # URL input
    st.subheader("Or Enter URL")
    profile_url = st.text_input(
        "Profile URL",
        placeholder="https://github.com/username",
        help="Enter a public profile URL to scrape"
    )
    
    if profile_url:
        st.info(f"🔗 URL entered: {profile_url}")

with col2:
    st.header("⚙️ Configuration")
    
    # Persona selection
    st.subheader("Roast Persona")
    persona = st.selectbox(
        "Choose your roaster",
        ["IShowSpeed", "ElonMusk", "Coworker", "GenZ", "Custom"],
        help="Select the personality style for your roast"
    )
    
    persona_descriptions = {
        "IShowSpeed": "⚡ High-energy, chaotic, and loud - no filter!",
        "ElonMusk": "🚀 Tech bro meets meme lord - sarcastic and visionary",
        "Coworker": "💼 Passive-aggressive office humor - professional shade",
        "GenZ": "😂 TikTok slang, emoji spam, and chronically online energy",
        "Custom": "✏️ Define your own style below"
    }
    st.caption(persona_descriptions[persona])
    
    custom_persona_text = ""
    if persona == "Custom":
        custom_persona_text = st.text_area(
            "Describe your custom persona",
            placeholder="e.g., A Victorian-era poet who speaks in rhymes...",
            height=100
        )
    
    st.markdown("---")
    
    # Toxicity level
    st.subheader("Toxicity Level")
    toxicity_level = st.radio(
        "Choose your spice level",
        ["Mild 😊", "Normal 🌶️", "Brutal 💀"],
        horizontal=True,
        help="Mild = PG-13, Normal = R-rated, Brutal = Unfiltered"
    )
    
    toxicity_descriptions = {
        "Mild 😊": "Family-friendly roasting. Safe for work.",
        "Normal 🌶️": "Standard roast. Some spice, but filtered.",
        "Brutal 💀": "No holds barred. Proceed with caution."
    }
    st.caption(toxicity_descriptions[toxicity_level])

# Mode toggle
st.markdown("---")
col_mode1, col_mode2 = st.columns(2)
with col_mode1:
    mode_choice = st.radio(
        "Choose mode:",
        ["Single Roast", "Conversation Mode"],
        horizontal=True,
        help="Single = one roast, Conversation = back-and-forth chat"
    )
    st.session_state.conversation_mode = (mode_choice == "Conversation Mode")

# Generate button
st.markdown("---")
col_btn = st.columns([1, 2, 1])
with col_btn[1]:
    generate_button = st.button(
        "🔥 Start Roasting",
        type="primary",
        use_container_width=True,
        disabled=not (uploaded_file or profile_url)
    )

if not (uploaded_file or profile_url):
    st.warning("⚠️ Please upload a file or enter a URL to continue")

# Generate initial roast
if generate_button:
    with st.spinner("🤖 Building profile..."):
        profile_data = build_profile(uploaded_file, profile_url)
        st.session_state.profile_data = profile_data
    
    with st.spinner("🎨 Building style prompt..."):
        backend_persona = map_ui_persona_to_backend(persona)
        mode_backend = map_ui_mode_to_backend(toxicity_level)
        st.session_state.selected_mode = mode_backend
        
        mildness_map = {"mild": 0.2, "normal": 0.5, "brutal": 0.9}
        mildness = mildness_map.get(mode_backend, 0.5)
        
        style_prompt = build_style_prompt(
            persona=backend_persona,
            custom_text=custom_persona_text if persona == "Custom" else "",
            mildness=mildness
        )
        st.session_state.style_prompt = style_prompt
    
    with st.spinner("🔥 Generating roast..."):
        result = generate_ai_response()
        
        st.session_state.current_roast = result['text']
        st.session_state.toxicity_score = result['toxicity_score']
        st.session_state.toxicity_label = result['toxicity_label']
        st.session_state.sources_used = result['evidence']
        st.session_state.quoted_evidence = result.get('quoted_evidence', [])
        st.session_state.roast_generated = True
        st.session_state.generation_count += 1
        
        # Initialize conversation
        st.session_state.conversation_history = [
            {'role': 'ai', 'text': result['text']}
        ]
        
        st.rerun()

# Display results
if st.session_state.roast_generated:
    st.markdown("---")
    
    # Conversation Mode
    if st.session_state.conversation_mode:
        st.header("💬 Conversation Thread")
        
        # Display conversation history
        with st.container():
            for msg in st.session_state.conversation_history:
                if msg['role'] == 'ai':
                    st.markdown(f'<div class="roast-box">🔥 <strong>AI Roaster:</strong><br>{msg["text"]}</div>', 
                               unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="user-response-box">👤 <strong>You:</strong><br>{msg["text"]}</div>', 
                               unsafe_allow_html=True)
        
        # User input for response
        st.markdown("### Your Response")
        user_input = st.text_area(
            "Type your comeback:",
            placeholder="Go ahead, roast them back...",
            height=100,
            key="user_comeback_input"
        )
        
        col_send1, col_send2, col_send3 = st.columns([1, 1, 1])
        with col_send2:
            send_button = st.button("📤 Send Response", use_container_width=True, type="primary")
        
        if send_button and user_input.strip():
            # Add user message to history
            st.session_state.conversation_history.append({
                'role': 'user',
                'text': user_input.strip()
            })
            
            # Generate AI response
            with st.spinner("🤖 AI is thinking..."):
                result = generate_ai_response(user_message=user_input.strip())
                
                # Add AI response to history
                st.session_state.conversation_history.append({
                    'role': 'ai',
                    'text': result['text']
                })
                
                st.session_state.current_roast = result['text']
                st.session_state.toxicity_score = result['toxicity_score']
                st.session_state.toxicity_label = result['toxicity_label']
                st.session_state.quoted_evidence = result.get('quoted_evidence', [])
                st.session_state.generation_count += 1
                
                st.rerun()
    
    # Single Roast Mode
    else:
        st.header("🎭 Your Roast")
        st.markdown(f'<div class="roast-box">{st.session_state.current_roast}</div>', unsafe_allow_html=True)
        
        # Action buttons for single mode
        st.markdown("### 🎬 Actions")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("🔄 Regenerate", use_container_width=True):
                with st.spinner("🔄 Regenerating..."):
                    result = generate_ai_response()
                    st.session_state.current_roast = result['text']
                    st.session_state.toxicity_score = result['toxicity_score']
                    st.session_state.toxicity_label = result['toxicity_label']
                    st.session_state.quoted_evidence = result.get('quoted_evidence', [])
                    st.session_state.generation_count += 1
                    st.rerun()
        
        with col2:
            if st.button("🎯 Make it Spicier", use_container_width=True):
                with st.spinner("🌶️ Adding spice..."):
                    spicy_prompt = st.session_state.style_prompt + "\n\nHint: Make it MORE savage and creative!"
                    st.session_state.style_prompt = spicy_prompt
                    result = generate_ai_response()
                    st.session_state.current_roast = result['text']
                    st.session_state.toxicity_score = result['toxicity_score']
                    st.session_state.toxicity_label = result['toxicity_label']
                    st.session_state.quoted_evidence = result.get('quoted_evidence', [])
                    st.rerun()
        
        with col3:
            if st.button("📋 Copy", use_container_width=True):
                copy_text = format_copy_text(st.session_state.current_roast)
                st.code(copy_text, language=None)
                st.success("✅ Ready to copy!")
        
        with col4:
            roast_snippet = st.session_state.current_roast[:200]
            twitter_text = f"🔥 I just got AI-roasted! 🔥\n\n{roast_snippet}..."
            twitter_url = f"https://twitter.com/intent/tweet?text={urllib.parse.quote(twitter_text)}"
            st.markdown(f"[🐦 Share]({twitter_url})", unsafe_allow_html=True)
    
    # Toxicity Analysis (both modes)
    st.markdown("---")
    st.markdown("### 🛡️ Safety Check")
    cols = st.columns(2)
    
    score = st.session_state.toxicity_score
    label = st.session_state.toxicity_label
    
    with cols[0]:
        if score < 0.3:
            badge_class, emoji, level = "toxicity-low", "🟢", "Low"
        elif score < 0.6:
            badge_class, emoji, level = "toxicity-medium", "🟡", "Medium"
        else:
            badge_class, emoji, level = "toxicity-high", "🔴", "High"
        
        st.markdown(f'<div class="{badge_class}" style="text-align: center; padding: 15px; border-radius: 10px;">'
                   f'{emoji}<br><strong>TOXICITY</strong><br>{score:.3f}<br>({level})</div>', 
                   unsafe_allow_html=True)
    
    with cols[1]:
        label_color = "#28a745" if label == "ok" else "#dc3545"
        label_text = "✅ SAFE" if label == "ok" else "⚠️ TOO HOT"
        st.markdown(f'<div style="text-align: center; padding: 15px; border-radius: 10px; '
                   f'background-color: {label_color}; color: white;">'
                   f'<strong>SAFETY CHECK</strong><br>{label_text}</div>', 
                   unsafe_allow_html=True)
    
    # Enhanced Evidence Display with Highlights
    st.markdown("---")
    with st.expander("🔍 Evidence Used (with Highlights)", expanded=False):
        if st.session_state.quoted_evidence:
            st.markdown("**The AI directly referenced these snippets from your profile:**")
            for idx, item in enumerate(st.session_state.quoted_evidence, 1):
                quote = item.get('quote', '')
                source = item.get('source', '')
                if quote:
                    st.markdown(f"{idx}. <span class='evidence-highlight'>\"{quote}\"</span>", unsafe_allow_html=True)
                    st.caption(f"   Source: {source}")
                else:
                    st.markdown(f"{idx}. {source}")
        elif st.session_state.sources_used:
            st.markdown("**Profile data used:**")
            for idx, source in enumerate(st.session_state.sources_used, 1):
                st.markdown(f"{idx}. {source}")
        else:
            st.info("No evidence available")

# Footer
st.markdown("---")
st.markdown(f"""
<div style="text-align: center; color: #666;">
    <p>🔥 AI Roaster MVP | Conversation Mode + Enhanced Evidence</p>
    <p><em>Roasts generated: {st.session_state.generation_count}</em></p>
</div>
""", unsafe_allow_html=True)
```

## Summary of Enhancements

### Option A: Conversation Mode
- ✅ Toggle between "Single Roast" and "Conversation Mode"
- ✅ Text input for user responses
- ✅ Conversation history display (threaded view)
- ✅ Context-aware AI responses (references last 3 messages)
- ✅ Different UI for each mode

### Option 3: Highlighted Evidence
- ✅ LLM instructed to quote specific data in double quotes ""
- ✅ `_extract_quoted_evidence()` function to parse quotes
- ✅ Evidence display shows highlighted quotes with yellow background
- ✅ Each quote mapped back to source (Bio, Profile data, etc.)
- ✅ Fallback to basic evidence if no quotes found

### Key Changes:
1. **llm.py**: Updated system prompt + new `_extract_quoted_evidence()` function
2. **streamlit_app.py**: Added conversation state + mode toggle + enhanced evidence display
3. **Better UX**: Clear distinction between single roast and conversation modes
