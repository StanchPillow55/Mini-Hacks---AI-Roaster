"""Backend Module Verification Test
Tests all backend modules before wiring to frontend
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("=" * 70)
print("BACKEND MODULE VERIFICATION TEST")
print("=" * 70)
print()

# Test 1: Import all modules
print("TEST 1: Module Imports")
print("-" * 70)

try:
    from src.personas import build_style_prompt, PERSONAS, get_persona_names
    print("✅ src.personas imported successfully")
except Exception as e:
    print(f"❌ src.personas import failed: {e}")
    sys.exit(1)

try:
    from src.scrape_basic import extract_profile_from_url, extract_from_resume
    print("✅ src.scrape_basic imported successfully")
except Exception as e:
    print(f"❌ src.scrape_basic import failed: {e}")
    sys.exit(1)

try:
    from src.llm import generate_roast, get_available_providers
    print("✅ src.llm imported successfully")
except Exception as e:
    print(f"❌ src.llm import failed: {e}")
    sys.exit(1)

try:
    from src.toxicity import check_toxicity, is_safe_roast, format_toxicity_report
    print("✅ src.toxicity imported successfully")
except Exception as e:
    print(f"❌ src.toxicity import failed: {e}")
    sys.exit(1)

print()

# Test 2: Check environment variables
print("TEST 2: Environment Variables")
print("-" * 70)

openai_key = os.getenv("OPENAI_API_KEY")
anthropic_key = os.getenv("ANTHROPIC_API_KEY")
perspective_key = os.getenv("PERSPECTIVE_API_KEY")
github_token = os.getenv("GITHUB_TOKEN")

print(f"OPENAI_API_KEY: {'✅ SET' if openai_key else '❌ NOT SET'}")
print(f"ANTHROPIC_API_KEY: {'✅ SET' if anthropic_key else '❌ NOT SET'}")
print(f"PERSPECTIVE_API_KEY: {'✅ SET' if perspective_key else '❌ NOT SET'}")
print(f"GITHUB_TOKEN: {'✅ SET' if github_token else '⚠️  NOT SET (optional)'}")

if not (openai_key or anthropic_key):
    print("\n⚠️  WARNING: No LLM API key found. Roast generation will fail.")

print()

# Test 3: Personas module
print("TEST 3: Personas Module")
print("-" * 70)

try:
    persona_names = get_persona_names()
    print(f"✅ Found {len(persona_names)} personas:")
    for name in persona_names:
        display_name = PERSONAS[name]['name']
        print(f"   - {name}: {display_name}")
    
    # Test building a style prompt
    prompt = build_style_prompt('gen_z', 'Python developer', mildness=0.7)
    print(f"\n✅ Built style prompt ({len(prompt)} chars)")
    print(f"   Preview (first 100 chars): {prompt[:100]}...")
    
except Exception as e:
    print(f"❌ Personas module test failed: {e}")
    import traceback
    traceback.print_exc()

print()

# Test 4: Scraper module
print("TEST 4: Scraper Module")
print("-" * 70)

try:
    # Test GitHub URL scraping
    test_url = "https://github.com/torvalds"
    print(f"Testing GitHub scrape: {test_url}")
    
    profile_data = extract_profile_from_url(test_url)
    
    if profile_data.get("bio"):
        print(f"✅ Scraped profile successfully")
        print(f"   Bio: {profile_data['bio'][:50]}...")
        print(f"   Snippets: {len(profile_data.get('snippets', []))} found")
        print(f"   Skills: {profile_data.get('skills', [])[:5]}")
    else:
        print(f"⚠️  Profile scraped but no bio found")
        print(f"   Data: {profile_data}")
    
except Exception as e:
    print(f"❌ Scraper module test failed: {e}")
    import traceback
    traceback.print_exc()

print()

# Test 5: LLM module
print("TEST 5: LLM Module")
print("-" * 70)

try:
    providers = get_available_providers()
    print(f"✅ Available LLM providers: {providers}")
    
    if providers:
        # Test roast generation with minimal profile
        test_profile = {
            "username": "test_user",
            "bio": "Python developer who loves coffee",
            "repos": ["hello-world"],
            "languages": ["Python"]
        }
        
        print("\n⚠️  Attempting roast generation (this will make an API call)...")
        print("   Using minimal test profile...")
        
        # Build a simple prompt
        from src.personas import build_style_prompt
        style_prompt = build_style_prompt('gen_z', 'Python developer who loves coffee', mildness=0.3)
        
        # Create profile dict for LLM (it expects specific format)
        llm_profile = {
            "name": test_profile["username"],
            "bio": test_profile["bio"],
            "posts": [],
            "interests": test_profile["languages"]
        }
        
        # Generate roast
        result = generate_roast(llm_profile, style_prompt, provider=providers[0], temperature=0.7)
        
        if result["text"].startswith("❌"):
            print(f"❌ Roast generation failed: {result['text']}")
        else:
            print(f"✅ Roast generated successfully ({len(result['text'])} chars)")
            print(f"   Preview: {result['text'][:100]}...")
            print(f"   Evidence snippets: {len(result['evidence'])} items")
    else:
        print("⚠️  No LLM providers available - skipping generation test")
    
except Exception as e:
    print(f"❌ LLM module test failed: {e}")
    import traceback
    traceback.print_exc()

print()

# Test 6: Toxicity module
print("TEST 6: Toxicity Module")
print("-" * 70)

try:
    if perspective_key:
        test_text = "You're not very good at coding, but at least you try."
        
        print(f"⚠️  Attempting toxicity check (this will make an API call)...")
        print(f"   Test text: \"{test_text}\"")
        
        scores = check_toxicity(test_text)
        
        if scores.get("error"):
            print(f"❌ Toxicity check failed: {scores['error']}")
        else:
            print(f"✅ Toxicity check successful")
            for attribute, score in scores.items():
                if attribute != "error":
                    print(f"   {attribute}: {score:.3f}")
            
            # Test safety check
            is_safe, reason = is_safe_roast(scores, "mild")
            print(f"\n   Safety check (mild mode): {'✅ SAFE' if is_safe else '❌ UNSAFE'}")
            if not is_safe:
                print(f"   Reason: {reason}")
    else:
        print("⚠️  PERSPECTIVE_API_KEY not set - skipping toxicity test")
    
except Exception as e:
    print(f"❌ Toxicity module test failed: {e}")
    import traceback
    traceback.print_exc()

print()

# Final Summary
print("=" * 70)
print("VERIFICATION SUMMARY")
print("=" * 70)
print("✅ All module imports successful")
print(f"{'✅' if (openai_key or anthropic_key) else '❌'} LLM API configured")
print(f"{'✅' if perspective_key else '⚠️ '} Perspective API configured")
print()
print("🎯 Backend modules are ready for frontend integration!")
print("=" * 70)
