# Step 10: Streamlit Backend Integration - PATCH

This patch integrates all backend modules into the Streamlit UI:
- Profile building (upload/URL)
- Style prompt (personas)
- LLM roast generation
- Toxicity scoring and enforcement
- Evidence display
- Improve/Comeback features
- Share functionality

## Complete Replacement for streamlit_app.py

```python
"""AI Roaster MVP - Fully Integrated Backend"""

import streamlit as st
import urllib.parse
from typing import Dict, Any

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
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'roast_generated' not in st.session_state:
    st.session_state.roast_generated = False
if 'current_roast' not in st.session_state:
    st.session_state.current_roast = ""
if 'toxicity_score' not in st.session_state:
    st.session_state.toxicity_score = 0.0
if 'toxicity_label' not in st.session_state:
    st.session_state.toxicity_label = "ok"
if 'sources_used' not in st.session_state:
    st.session_state.sources_used = []
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
        # Process uploaded file
        file_bytes = uploaded_file.read()
        profile = extract_from_resume(file_bytes)
        profile['name'] = uploaded_file.name
        return profile
    elif profile_url:
        # Process URL
        profile = extract_profile_from_url(profile_url)
        # Extract name from URL
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
        "ElonMusk": "gen_z",  # Could add specific elon persona later
        "Coworker": "corporate",
        "GenZ": "gen_z",
        "Custom": "gen_z"  # Default for custom
    }
    return persona_mapping.get(ui_persona, "gen_z")


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
        placeholder="https://github.com/username or https://twitter.com/username",
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
    
    # Persona descriptions
    persona_descriptions = {
        "IShowSpeed": "⚡ High-energy, chaotic, and loud - no filter!",
        "ElonMusk": "🚀 Tech bro meets meme lord - sarcastic and visionary",
        "Coworker": "💼 Passive-aggressive office humor - professional shade",
        "GenZ": "😂 TikTok slang, emoji spam, and chronically online energy",
        "Custom": "✏️ Define your own style below"
    }
    st.caption(persona_descriptions[persona])
    
    # Custom persona input (only if Custom is selected)
    custom_persona_text = ""
    if persona == "Custom":
        custom_persona_text = st.text_area(
            "Describe your custom persona",
            placeholder="e.g., A Victorian-era poet who speaks in rhymes and metaphors...",
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
    
    # Toxicity level descriptions
    toxicity_descriptions = {
        "Mild 😊": "Family-friendly roasting. Safe for work.",
        "Normal 🌶️": "Standard roast. Some spice, but filtered.",
        "Brutal 💀": "No holds barred. Proceed with caution."
    }
    st.caption(toxicity_descriptions[toxicity_level])

# Generate button (full width)
st.markdown("---")
col_btn = st.columns([1, 2, 1])
with col_btn[1]:
    generate_button = st.button(
        "🔥 Generate Roast",
        type="primary",
        use_container_width=True,
        disabled=not (uploaded_file or profile_url)
    )

# Show input requirement message
if not (uploaded_file or profile_url):
    st.warning("⚠️ Please upload a file or enter a URL to continue")

# Generate roast with full backend integration
if generate_button:
    with st.spinner("🤖 Building profile..."):
        # Step a) Build profile
        profile_data = build_profile(uploaded_file, profile_url)
        st.session_state.profile_data = profile_data
    
    with st.spinner("🎨 Building style prompt..."):
        # Step b) Build style prompt
        backend_persona = map_ui_persona_to_backend(persona)
        mode_backend = map_ui_mode_to_backend(toxicity_level)
        st.session_state.selected_mode = mode_backend
        
        # Map mode to mildness (0.0-1.0)
        mildness_map = {"mild": 0.2, "normal": 0.5, "brutal": 0.9}
        mildness = mildness_map.get(mode_backend, 0.5)
        
        style_prompt = build_style_prompt(
            persona=backend_persona,
            custom_text=custom_persona_text if persona == "Custom" else "",
            mildness=mildness
        )
        st.session_state.style_prompt = style_prompt
    
    with st.spinner("🔥 Generating roast..."):
        # Step c) Call generate_roast
        roast_result = generate_roast(
            profile=profile_data,
            style_prompt=style_prompt,
            provider="openai",  # or "anthropic"
            temperature=0.8
        )
        
        roast_text = roast_result['text']
        evidence = roast_result['evidence']
    
    with st.spinner("🛡️ Checking toxicity..."):
        # Step d) Score toxicity
        tox_result = score_toxicity(roast_text)
        tox_score = tox_result["toxicity"]
        
        # Step e) Check if too_hot or mild mode
        label = map_label(tox_score, mode_backend)
        
        if label == "too_hot" or mode_backend == "mild":
            with st.spinner("🧼 Softening roast..."):
                # Enforce mildness
                roast_text = enforce_mildness(roast_text, mode_backend)
                # Rescore once
                tox_result = score_toxicity(roast_text)
                tox_score = tox_result["toxicity"]
                label = map_label(tox_score, mode_backend)
        
        st.session_state.current_roast = roast_text
        st.session_state.toxicity_score = tox_score
        st.session_state.toxicity_label = label
        st.session_state.sources_used = evidence
        st.session_state.roast_generated = True
        st.session_state.generation_count += 1
        
        st.rerun()

# Display roast results
if st.session_state.roast_generated:
    st.markdown("---")
    st.header("🎭 Your Roast")
    
    # Roast display
    st.markdown(f'<div class="roast-box">{st.session_state.current_roast}</div>', unsafe_allow_html=True)
    
    # Toxicity score display
    st.markdown("### 🛡️ Toxicity Analysis")
    cols = st.columns(2)
    
    score = st.session_state.toxicity_score
    label = st.session_state.toxicity_label
    
    with cols[0]:
        if score < 0.3:
            badge_class = "toxicity-low"
            emoji = "🟢"
            level = "Low"
        elif score < 0.6:
            badge_class = "toxicity-medium"
            emoji = "🟡"
            level = "Medium"
        else:
            badge_class = "toxicity-high"
            emoji = "🔴"
            level = "High"
        
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
    
    st.markdown("---")
    
    # Action buttons
    st.markdown("### 🎬 Actions")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("🔄 Improve", use_container_width=True):
            # Improve: regenerate with hint to be "more creative and clever"
            if st.session_state.profile_data and st.session_state.style_prompt:
                with st.spinner("🔄 Improving roast..."):
                    improved_prompt = st.session_state.style_prompt + "\n\nHint: Make it MORE creative, clever, and witty!"
                    roast_result = generate_roast(
                        profile=st.session_state.profile_data,
                        style_prompt=improved_prompt,
                        provider="openai",
                        temperature=0.9  # Higher creativity
                    )
                    
                    roast_text = roast_result['text']
                    
                    # Toxicity check and enforce
                    tox_result = score_toxicity(roast_text)
                    tox_score = tox_result["toxicity"]
                    label = map_label(tox_score, st.session_state.selected_mode)
                    
                    if label == "too_hot" or st.session_state.selected_mode == "mild":
                        roast_text = enforce_mildness(roast_text, st.session_state.selected_mode)
                        tox_result = score_toxicity(roast_text)
                        tox_score = tox_result["toxicity"]
                        label = map_label(tox_score, st.session_state.selected_mode)
                    
                    st.session_state.current_roast = roast_text
                    st.session_state.toxicity_score = tox_score
                    st.session_state.toxicity_label = label
                    st.session_state.generation_count += 1
                    st.rerun()
    
    with col2:
        if st.button("↩️ Comeback", use_container_width=True):
            # Comeback: generate a counter-roast
            if st.session_state.profile_data and st.session_state.style_prompt:
                with st.spinner("↩️ Generating comeback..."):
                    comeback_prompt = st.session_state.style_prompt + f"\n\nHint: Generate a COMEBACK roast in response to: \"{st.session_state.current_roast[:100]}...\""
                    roast_result = generate_roast(
                        profile=st.session_state.profile_data,
                        style_prompt=comeback_prompt,
                        provider="openai",
                        temperature=0.85
                    )
                    
                    roast_text = roast_result['text']
                    
                    # Toxicity check and enforce
                    tox_result = score_toxicity(roast_text)
                    tox_score = tox_result["toxicity"]
                    label = map_label(tox_score, st.session_state.selected_mode)
                    
                    if label == "too_hot" or st.session_state.selected_mode == "mild":
                        roast_text = enforce_mildness(roast_text, st.session_state.selected_mode)
                        tox_result = score_toxicity(roast_text)
                        tox_score = tox_result["toxicity"]
                        label = map_label(tox_score, st.session_state.selected_mode)
                    
                    st.session_state.current_roast = roast_text
                    st.session_state.toxicity_score = tox_score
                    st.session_state.toxicity_label = label
                    st.session_state.generation_count += 1
                    st.rerun()
    
    with col3:
        if st.button("📋 Copy", use_container_width=True):
            copy_text = format_copy_text(st.session_state.current_roast)
            st.code(copy_text, language=None)
            st.success("✅ Roast ready to copy above!")
    
    with col4:
        # Twitter/X share button
        roast_snippet = st.session_state.current_roast[:200]  # Twitter char limit
        twitter_text = f"🔥 I just got AI-roasted! 🔥\n\n{roast_snippet}..."
        twitter_url = f"https://twitter.com/intent/tweet?text={urllib.parse.quote(twitter_text)}"
        st.markdown(f"[🐦 Share on X]({twitter_url})", unsafe_allow_html=True)
    
    # Source transparency
    st.markdown("---")
    with st.expander("🔍 Sources Used"):
        if st.session_state.sources_used:
            st.markdown("**Evidence snippets used for this roast:**")
            for idx, source in enumerate(st.session_state.sources_used, 1):
                st.markdown(f"{idx}. {source}")
        else:
            st.info("No sources available yet")

# Footer
st.markdown("---")
st.markdown(f"""
<div style="text-align: center; color: #666;">
    <p>🔥 AI Roaster MVP | Fully Integrated Backend</p>
    <p><em>Roasts generated: {st.session_state.generation_count}</em></p>
</div>
""", unsafe_allow_html=True)
```

## Key Changes Summary

1. **Import all backend modules** at the top
2. **`build_profile()`** function to handle uploads and URLs
3. **`map_ui_mode_to_backend()`** and **`map_ui_persona_to_backend()`** for UI-backend mapping
4. **Generate button** now:
   - Builds profile from upload/URL
   - Builds style prompt with persona
   - Calls `generate_roast()` from llm.py
   - Calls `score_toxicity()` and `map_label()`
   - Calls `enforce_mildness()` if needed and rescores
5. **Improve button**: Regenerates with "more creative" hint
6. **Comeback button**: Generates counter-roast
7. **Copy button**: Uses `format_copy_text()` from share.py
8. **Twitter share**: Generates prefilled Twitter intent URL
9. **Sources Used**: Displays evidence snippets from LLM

## Notes

- Removed style_url input (not in MVP scope)
- Uses OpenAI by default (can switch to Anthropic by changing provider parameter)
- Toxicity enforcement happens automatically for "too_hot" or "mild" mode
- Profile data and style prompt stored in session state for Improve/Comeback reuse
