#!/usr/bin/env python3
"""Test conversation mode and enhanced evidence extraction"""

import os
from src.llm import generate_roast, _extract_quoted_evidence
from src.personas import build_style_prompt
from src.toxicity import score_toxicity, map_label, enforce_mildness

print("=" * 70)
print("CONVERSATION MODE + ENHANCED EVIDENCE TEST")
print("=" * 70)
print()

# Test profile data
test_profile = {
    'name': 'TestUser',
    'bio': 'Python developer with 5 years experience. Love coffee and cats.',
    'snippets': [
        'Repo: my-awesome-project - A simple todo app',
        'Repo: hello-world - Learning Python basics',
        'Recent activity: Pushed code once this month'
    ],
    'interests': ['Python', 'Machine Learning', 'Coffee'],
    'posts': [
        'Just deployed my first app!',
        'Why is debugging so hard?'
    ]
}

print("📋 Test Profile:")
print(f"   Name: {test_profile['name']}")
print(f"   Bio: {test_profile['bio']}")
print(f"   Snippets: {len(test_profile['snippets'])}")
print()

# Test 1: Basic roast generation with quoted evidence
print("=" * 70)
print("TEST 1: Enhanced Evidence Extraction")
print("=" * 70)
print()

# Build style prompt
style_prompt = build_style_prompt(persona='gen_z', mildness=0.5)

print("🔥 Generating roast...")
result = generate_roast(
    profile=test_profile,
    style_prompt=style_prompt,
    provider='openai',
    temperature=0.8
)

print("\n📝 Generated Roast:")
print(result['text'])
print()

print("🔍 Basic Evidence (what was sent to LLM):")
for i, evidence in enumerate(result['evidence'], 1):
    print(f"   {i}. {evidence}")
print()

print("✨ Quoted Evidence (what LLM actually referenced):")
quoted = result.get('quoted_evidence', [])
if quoted:
    for i, item in enumerate(quoted, 1):
        quote = item.get('quote', '')
        source = item.get('source', '')
        if quote:
            print(f"   {i}. Quote: \"{quote}\"")
            print(f"      Source: {source}")
        else:
            print(f"   {i}. {source}")
else:
    print("   (No quoted evidence found - fallback to basic evidence)")
print()

# Test 2: Toxicity check
print("=" * 70)
print("TEST 2: Toxicity Check")
print("=" * 70)
print()

tox_result = score_toxicity(result['text'])
tox_score = tox_result['toxicity']
label = map_label(tox_score, 'normal')

print(f"Toxicity Score: {tox_score:.3f}")
print(f"Safety Label: {label}")
print()

if label == 'too_hot':
    print("⚠️ Roast is too hot! Applying mildness enforcement...")
    softened = enforce_mildness(result['text'], 'normal')
    tox_result_after = score_toxicity(softened)
    print(f"Softened Text: {softened}")
    print(f"New Toxicity: {tox_result_after['toxicity']:.3f}")
else:
    print("✅ Roast passes safety check!")
print()

# Test 3: Conversation simulation
print("=" * 70)
print("TEST 3: Conversation Mode Simulation")
print("=" * 70)
print()

conversation_history = [
    {'role': 'ai', 'text': result['text']}
]

print("💬 Conversation Thread:")
print(f"🔥 AI: {conversation_history[0]['text']}")
print()

# Simulate user response
user_response = "Oh yeah? Well at least I write code that works!"
conversation_history.append({'role': 'user', 'text': user_response})
print(f"👤 User: {user_response}")
print()

# Generate AI counter-response with context
print("🤖 Generating AI counter-response with conversation context...")
context_prompt = style_prompt + "\n\nCONVERSATION CONTEXT:\n"
for msg in conversation_history[-3:]:
    role = "AI Roaster" if msg['role'] == 'ai' else "User"
    context_prompt += f"{role}: {msg['text']}\n"
context_prompt += "\nNow respond to the user's message with another roast!"

counter_result = generate_roast(
    profile=test_profile,
    style_prompt=context_prompt,
    provider='openai',
    temperature=0.85
)

conversation_history.append({'role': 'ai', 'text': counter_result['text']})
print(f"🔥 AI: {counter_result['text']}")
print()

# Test 4: Verify evidence extraction function directly
print("=" * 70)
print("TEST 4: Direct Evidence Extraction Test")
print("=" * 70)
print()

test_roast_with_quotes = '''Your bio says "Python developer" but your repos look like 
"hello-world" level. You claim "5 years experience" but pushed code once this month?'''

print("Test Roast Text:")
print(test_roast_with_quotes)
print()

extracted = _extract_quoted_evidence(test_roast_with_quotes, test_profile)
print("Extracted Quotes:")
for i, item in enumerate(extracted, 1):
    quote = item.get('quote', '')
    source = item.get('source', '')
    if quote:
        print(f"   {i}. \"{quote}\" → {source}")
print()

print("=" * 70)
print("✅ ALL TESTS COMPLETE")
print("=" * 70)
print()

# Show API status
has_openai = bool(os.environ.get('OPENAI_API_KEY'))
has_anthropic = bool(os.environ.get('ANTHROPIC_API_KEY'))

print("📊 API Configuration Status:")
print(f"   OpenAI API Key: {'✅ Set' if has_openai else '❌ Not set (using stub roasts)'}")
print(f"   Anthropic API Key: {'✅ Set' if has_anthropic else '❌ Not set'}")
print()

if not has_openai and not has_anthropic:
    print("💡 TIP: Set OPENAI_API_KEY or ANTHROPIC_API_KEY to generate real roasts")
    print("   The tests above used stub roasts which still demonstrate the features")
