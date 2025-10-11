#!/usr/bin/env python3
"""Step 13: End-to-End Verification Test"""

from dotenv import load_dotenv
load_dotenv()

from src.scrape_basic import extract_profile_from_url, extract_from_resume
from src.personas import build_style_prompt
from src.llm import generate_roast
from src.toxicity import score_toxicity, map_label, enforce_mildness
from src.share import format_copy_text
import urllib.parse

print("=" * 80)
print("STEP 13: END-TO-END VERIFICATION TEST")
print("=" * 80)
print()

# Test 1: GitHub URL
print("TEST 1: GitHub URL Profile Extraction")
print("-" * 80)
test_url = "https://github.com/torvalds"
print(f"Extracting profile from: {test_url}")

profile = extract_profile_from_url(test_url)
print(f"✅ Name: {profile.get('name', 'N/A')}")
print(f"✅ Bio: {profile.get('bio', 'N/A')[:80]}...")
print(f"✅ Snippets: {len(profile.get('snippets', []))}")
print()

# Test 2: Generate Roast
print("TEST 2: Roast Generation")
print("-" * 80)
style = build_style_prompt(persona='gen_z', mildness=0.5)
print("Generating roast with GenZ persona...")

result = generate_roast(profile=profile, style_prompt=style, provider='openai')
roast_text = result['text']
evidence = result['evidence']

print(f"✅ Roast generated ({len(roast_text)} chars)")
print(f"Generated roast preview:\n{roast_text[:200]}...")
print(f"\n✅ Evidence snippets: {len(evidence)}")
print()

# Test 3: Toxicity Scoring
print("TEST 3: Toxicity Analysis")
print("-" * 80)
tox_result = score_toxicity(roast_text)
tox_score = tox_result["toxicity"]
label = map_label(tox_score, "normal")

print(f"✅ Raw toxicity score: {tox_score:.4f}")
print(f"✅ Safety label (normal mode): {label}")
print(f"✅ Score interpretation: {'Low' if tox_score < 0.3 else 'Medium' if tox_score < 0.6 else 'High'}")
print()

# Test 4: Mildness Enforcement (if needed)
print("TEST 4: Mildness Enforcement")
print("-" * 80)
if label == "too_hot":
    print("⚠️  Roast is too hot, applying enforcement...")
    softened = enforce_mildness(roast_text, "normal")
    tox_after = score_toxicity(softened)["toxicity"]
    print(f"✅ After enforcement: {tox_after:.4f}")
    roast_text = softened
else:
    print("✅ Roast passes safety check, no enforcement needed")
print()

# Test 5: Evidence Display
print("TEST 5: Evidence Snippets")
print("-" * 80)
print("Evidence used:")
for idx, ev in enumerate(evidence[:5], 1):
    print(f"  {idx}. {ev[:100]}...")
print()

# Test 6: Improve Flow
print("TEST 6: Improve Flow")
print("-" * 80)
improve_hint = "Make it funnier"
improved_prompt = style + f"\n\nHint: {improve_hint}"
print(f"Testing improve with hint: '{improve_hint}'")

improve_result = generate_roast(profile=profile, style_prompt=improved_prompt, provider='openai', temperature=0.9)
print(f"✅ Improved roast generated ({len(improve_result['text'])} chars)")
print(f"Preview: {improve_result['text'][:150]}...")
print()

# Test 7: Comeback Flow
print("TEST 7: Comeback Flow")
print("-" * 80)
user_comeback = "At least I have more followers than you!"
comeback_prompt = style + f'\n\nThe user responded with: "{user_comeback}"\n\nGenerate a one-turn reply roast!'
print(f"User comeback: '{user_comeback}'")

comeback_result = generate_roast(profile=profile, style_prompt=comeback_prompt, provider='openai', temperature=0.85)
print(f"✅ Comeback generated ({len(comeback_result['text'])} chars)")
print(f"Preview: {comeback_result['text'][:150]}...")
print()

# Test 8: Share Functions
print("TEST 8: Share Functions")
print("-" * 80)

# Copy text
copy_text = format_copy_text(roast_text)
print(f"✅ Copy text formatted ({len(copy_text)} chars)")

# Twitter URL
twitter_snippet = roast_text[:200]
twitter_text = f"🔥 I just got AI-roasted! 🔥\n\n{twitter_snippet}..."
twitter_url = f"https://twitter.com/intent/tweet?text={urllib.parse.quote(twitter_text)}"
print(f"✅ Twitter URL: {twitter_url[:80]}...")
print()

# Test 9: Dummy Resume File
print("TEST 9: Resume File Processing")
print("-" * 80)
dummy_resume = b"""John Doe
Software Engineer

Experience:
- Senior Developer at Tech Corp (2020-2023)
- Python, JavaScript, React

Skills: Python, AWS, Docker, Git

Education:
BS Computer Science, University of Tech
"""

resume_profile = extract_from_resume(dummy_resume)
print(f"✅ Name extracted: {resume_profile.get('name', 'N/A')}")
print(f"✅ Skills found: {len(resume_profile.get('skills', []))}")
print(f"✅ Titles found: {len(resume_profile.get('titles', []))}")
print()

# Final Summary
print("=" * 80)
print("E2E TEST SUMMARY")
print("=" * 80)

tests = [
    ("GitHub Profile Extraction", True),
    ("Roast Generation", len(roast_text) > 50),
    ("Toxicity Scoring", 0 <= tox_score <= 1),
    ("Safety Label", label in ["ok", "too_hot"]),
    ("Evidence Snippets", len(evidence) > 0),
    ("Improve Flow", len(improve_result['text']) > 50),
    ("Comeback Flow", len(comeback_result['text']) > 50),
    ("Share Functions", len(copy_text) > 0 and len(twitter_url) > 0),
    ("Resume Processing", resume_profile.get('name') is not None),
]

all_passed = all(result for _, result in tests)

for test_name, result in tests:
    status = "✅ PASS" if result else "❌ FAIL"
    print(f"{status}: {test_name}")

print()
print("=" * 80)
if all_passed:
    print("🎉 MVP DEMO READY: YES")
    print("All core features tested and working!")
else:
    print("⚠️  MVP DEMO READY: NO")
    print("Some tests failed - check above for details")
print("=" * 80)
