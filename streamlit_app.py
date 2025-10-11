"""AI Roaster MVP - Fully Integrated Backend"""

import streamlit as st
import urllib.parse
from typing import Dict, Any
import os

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Import backend modules
from src.scrape_basic import extract_profile_from_url, extract_from_resume
from src.personas import build_style_prompt
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
if 'scrape_failed' not in st.session_state:
    st.session_state.scrape_failed = False
if 'disallow_protected_class_insults' not in st.session_state:
    st.session_state.disallow_protected_class_insults = True
if 'harshness_slider' not in st.session_state:
    st.session_state.harshness_slider = 50


def build_profile(uploaded_file, profile_url):
    """Build profile data from upload or URL. Returns (profile_dict, success_flag)."""
    if uploaded_file:
        # Process uploaded file
        try:
            file_bytes = uploaded_file.read()
            profile = extract_from_resume(file_bytes)
            profile['name'] = uploaded_file.name
            return profile, True
        except Exception as e:
            st.warning(f"⚠️ Failed to process file: {e}")
            return _get_demo_profile(uploaded_file.name), False
    elif profile_url:
        # Process URL
        try:
            profile = extract_profile_from_url(profile_url)
            # Extract name from URL
            if 'github.com' in profile_url:
                username = profile_url.rstrip('/').split('/')[-1]
                profile['name'] = username
            else:
                profile['name'] = profile.get('titles', ['User'])[0] if profile.get('titles') else 'User'
            return profile, True
        except Exception as e:
            st.warning(f"⚠️ Failed to scrape URL: {e}")
            return _get_demo_profile(profile_url), False
    else:
        return {"name": "User", "bio": "No profile data", "snippets": [], "sources": []}, True


def _get_demo_profile(identifier: str) -> Dict[str, Any]:
    """Return demo profile data when scraping fails."""
    return {
        "name": identifier or "Demo User",
        "bio": "Generic developer who loves coding, coffee, and cats. Has strong opinions about tabs vs spaces.",
        "titles": ["Software Engineer", "Open Source Contributor"],
        "skills": ["Python", "JavaScript", "Procrastination"],
        "snippets": [
            "Commits directly to main branch without testing",
            "Uses 'fix' as a commit message",
            "Claims to read documentation but never does"
        ],
        "sources": ["Demo data - scrape failed"]
    }


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
    
    # Custom persona input
    custom_persona_text = ""
    if persona == "Custom":
        custom_persona_text = st.text_area(
            "Describe your custom persona",
            placeholder="e.g., A Victorian-era poet who speaks in rhymes and metaphors...",
            height=100
        )
    
    st.markdown("---")
    
    # Harshness slider
    st.subheader("Harshness Level")
    harshness_value = st.slider(
        "Adjust roast intensity",
        min_value=0,
        max_value=100,
        value=st.session_state.harshness_slider,
        step=5,
        help="0 = gentle & playful, 50 = standard roast, 100 = maximum spice"
    )
    st.session_state.harshness_slider = harshness_value
    
    # Show current mode description based on harshness
    if harshness_value < 30:
        mode_desc = "😊 Gentle mode: Family-friendly, playful roasting"
        derived_mode = "mild"
    elif harshness_value < 70:
        mode_desc = "🌶️ Standard mode: Clever roasting with some edge"
        derived_mode = "normal"
    else:
        mode_desc = "💀 Spicy mode: Maximum intensity roasting"
        derived_mode = "brutal"
    st.caption(mode_desc)
    
    # Safety checkbox
    st.markdown("---")
    st.subheader("Safety Settings")
    disallow_protected = st.checkbox(
        "🛡️ Disallow protected-class insults",
        value=st.session_state.disallow_protected_class_insults,
        help="Blocks attacks based on race, gender, religion, disability, sexual orientation, etc."
    )
    st.session_state.disallow_protected_class_insults = disallow_protected

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

# TASK 1: Generate roast with full backend integration
if generate_button:
    with st.spinner("🤖 Building profile..."):
        # Step a) Build profile via upload or URL
        profile_data, scrape_success = build_profile(uploaded_file, profile_url)
        st.session_state.profile_data = profile_data
        st.session_state.scrape_failed = not scrape_success
    
    # Show banner if scrape failed
    if st.session_state.scrape_failed:
        st.warning(
            "⚠️ **Scrape failed - using demo data**\n\n"
            "The profile could not be scraped. Generated roast will use generic demo profile data. "
            "This often happens with rate limits or inaccessible URLs."
        )
    
    with st.spinner("🎨 Building style prompt..."):
        # Step b) Build style via personas
        backend_persona = map_ui_persona_to_backend(persona)
        
        # Derive mode from harshness slider
        if harshness_value < 30:
            mode_backend = "mild"
        elif harshness_value < 70:
            mode_backend = "normal"
        else:
            mode_backend = "brutal"
        st.session_state.selected_mode = mode_backend
        
        # Map harshness slider (0-100) to mildness (0.0-1.0)
        mildness = harshness_value / 100.0
        
        style_prompt = build_style_prompt(
            persona=backend_persona,
            custom_text=custom_persona_text if persona == "Custom" else "",
            mildness=mildness
        )
        
        # Enforce protected-class safety in system prompt
        if st.session_state.disallow_protected_class_insults:
            style_prompt += "\n\nSTRICT SAFETY RULE: You MUST NOT make any attacks or insults based on race, ethnicity, gender, sexual orientation, religion, disability, age, or any other protected characteristics. Focus ONLY on behavior, choices, public persona, and skills."
        
        st.session_state.style_prompt = style_prompt
    
    with st.spinner("🔥 Generating roast..."):
        # Step c) Call generate_roast to get text and evidence
        roast_result = generate_roast(
            profile=profile_data,
            style_prompt=style_prompt,
            provider="openai",
            temperature=0.8
        )
        
        roast_text = roast_result['text']
        evidence = roast_result['evidence']
    
    with st.spinner("🛡️ Checking toxicity..."):
        # Step d) tox = score_toxicity(text)["toxicity"]
        tox_result = score_toxicity(roast_text)
        tox = tox_result["toxicity"]
        
        # Step e) If map_label(tox, mode) == "too_hot" or mode == "mild":
        label = map_label(tox, mode_backend)
        
        if label == "too_hot" or mode_backend == "mild":
            with st.spinner("🧼 Softening roast..."):
                # text = enforce_mildness(text, mode)
                roast_text = enforce_mildness(roast_text, mode_backend)
                # tox = score_toxicity(text)["toxicity"]
                tox_result = score_toxicity(roast_text)
                tox = tox_result["toxicity"]
                label = map_label(tox, mode_backend)
        
        # Store results
        st.session_state.current_roast = roast_text
        st.session_state.toxicity_score = tox
        st.session_state.toxicity_label = label
        st.session_state.sources_used = evidence
        st.session_state.roast_generated = True
        
        st.rerun()

# Display roast results
if st.session_state.roast_generated:
    st.markdown("---")
    st.header("🎭 Your Roast")
    
    # Display roast text
    st.markdown(f'<div class="roast-box">{st.session_state.current_roast}</div>', unsafe_allow_html=True)
    
    # Display numeric toxicity, label from map_label
    st.markdown("### 🛡️ Toxicity Analysis")
    cols = st.columns(2)
    
    score = st.session_state.toxicity_score
    label = st.session_state.toxicity_label
    
    with cols[0]:
        # Numeric toxicity score with color coding
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
                   f'{emoji}<br><strong>TOXICITY SCORE</strong><br>{score:.3f}<br>({level})</div>', 
                   unsafe_allow_html=True)
    
    with cols[1]:
        # Label from map_label
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
    
    # IMPROVE: take a short instruction, pass as extra hint
    with col1:
        if st.button("🔄 Improve", use_container_width=True, key="improve_btn_main"):
            st.session_state.show_improve = not st.session_state.get('show_improve', False)
        
        if st.session_state.get('show_improve', False):
            improve_instruction = st.text_input(
                "How to improve?",
                placeholder="Make it funnier, more clever, etc.",
                key="improve_input"
            )
            if st.button("Generate Improved", key="improve_btn"):
                if improve_instruction.strip():
                    with st.spinner("🔄 Improving roast..."):
                        # Pass instruction as extra hint to generate_roast
                        improved_prompt = st.session_state.style_prompt + f"\n\nHint: {improve_instruction.strip()}"
                        roast_result = generate_roast(
                            profile=st.session_state.profile_data,
                            style_prompt=improved_prompt,
                            provider="openai",
                            temperature=0.9
                        )
                        
                        roast_text = roast_result['text']
                        
                        # Toxicity check and enforcement
                        tox_result = score_toxicity(roast_text)
                        tox = tox_result["toxicity"]
                        label = map_label(tox, st.session_state.selected_mode)
                        
                        if label == "too_hot" or st.session_state.selected_mode == "mild":
                            roast_text = enforce_mildness(roast_text, st.session_state.selected_mode)
                            tox_result = score_toxicity(roast_text)
                            tox = tox_result["toxicity"]
                            label = map_label(tox, st.session_state.selected_mode)
                        
                        st.session_state.current_roast = roast_text
                        st.session_state.toxicity_score = tox
                        st.session_state.toxicity_label = label
                        st.session_state.show_improve = False
                        st.rerun()
                else:
                    st.warning("Please enter an instruction")
    
    # COMEBACK: take user comeback, generate one turn reply
    with col2:
        if st.button("↩️ Comeback", use_container_width=True, key="comeback_btn_main"):
            st.session_state.show_comeback = not st.session_state.get('show_comeback', False)
        
        if st.session_state.get('show_comeback', False):
            user_comeback = st.text_area(
                "Your comeback:",
                placeholder="Type your response here...",
                height=100,
                key="comeback_input"
            )
            if st.button("Generate Reply", key="comeback_btn"):
                if user_comeback.strip():
                    with st.spinner("↩️ Generating comeback reply..."):
                        # Generate one turn reply
                        comeback_prompt = st.session_state.style_prompt + f"\n\nThe user responded with: \"{user_comeback.strip()}\"\n\nGenerate a one-turn reply roast!"
                        roast_result = generate_roast(
                            profile=st.session_state.profile_data,
                            style_prompt=comeback_prompt,
                            provider="openai",
                            temperature=0.85
                        )
                        
                        roast_text = roast_result['text']
                        
                        # Toxicity check and enforcement
                        tox_result = score_toxicity(roast_text)
                        tox = tox_result["toxicity"]
                        label = map_label(tox, st.session_state.selected_mode)
                        
                        if label == "too_hot" or st.session_state.selected_mode == "mild":
                            roast_text = enforce_mildness(roast_text, st.session_state.selected_mode)
                            tox_result = score_toxicity(roast_text)
                            tox = tox_result["toxicity"]
                            label = map_label(tox, st.session_state.selected_mode)
                        
                        st.session_state.current_roast = roast_text
                        st.session_state.toxicity_score = tox
                        st.session_state.toxicity_label = label
                        st.session_state.show_comeback = False
                        st.rerun()
                else:
                    st.warning("Please enter your comeback")
    
    # SHARE: build copyable text and Twitter intent URL
    with col3:
        if st.button("📋 Copy", use_container_width=True, key="copy_btn_main"):
            st.session_state.show_copy = not st.session_state.get('show_copy', False)
        
        if st.session_state.get('show_copy', False):
            copy_text = format_copy_text(st.session_state.current_roast)
            st.text_area("Copy this:", copy_text, height=150, key="copy_area")
            st.caption("Select text above and copy (Cmd+C / Ctrl+C)")
    
    with col4:
        # Twitter intent URL
        roast_snippet = st.session_state.current_roast[:200]
        twitter_text = f"🔥 I just got AI-roasted! 🔥\n\n{roast_snippet}..."
        twitter_url = f"https://twitter.com/intent/tweet?text={urllib.parse.quote(twitter_text)}"
        st.markdown(f"[🐦 Tweet]({twitter_url})", unsafe_allow_html=True)
        
        # Discord webhook placeholder
        if st.button("💬 Discord", key="discord_btn"):
            st.info("🚧 Discord webhook integration - coming soon!")
    
    # Display evidence snippets in Sources used
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
st.markdown("""
<div style="text-align: center; color: #666;">
    <p>🔥 AI Roaster MVP | Fully Integrated Backend</p>
    <p><em>Step 10 Complete - All modules integrated</em></p>
</div>
""", unsafe_allow_html=True)
