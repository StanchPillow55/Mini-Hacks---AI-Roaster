#!/usr/bin/env python3
"""Demo script to test the updated LLM wrapper"""

import sys
sys.path.insert(0, '/Users/bradleyharaguchi/Mini-Hacks---AI-Roaster')

from src.llm import generate_roast, get_available_providers

# Test profile
test_profile = {
    "name": "TechBro3000",
    "bio": "Full-stack developer, coffee enthusiast, and startup founder. Disrupting the industry one commit at a time.",
    "posts": [
        "Just deployed my new app built with React, Node, MongoDB, and 47 other dependencies. #blessed",
        "Anyone else think tabs are better than spaces? Fight me.",
        "Why use 10 lines when you can use 100? More code = more value."
    ],
    "interests": ["JavaScript", "Blockchain", "NFTs", "Productivity Hacks", "Standing Desks"]
}

# Test style prompt
style_prompt = "You are a witty comedian roasting a tech professional. Be clever and playful."

print("=" * 60)
print("LLM WRAPPER DEMO - Step 9")
print("=" * 60)

# Check available providers
providers = get_available_providers()
print(f"\n✅ Available providers: {providers if providers else 'None (dry-run mode)'}")

# Generate roast (will use dry-run if no keys)
print("\n🎭 Generating roast...")
result = generate_roast(test_profile, style_prompt, provider="openai")

print("\n📝 RESULT:")
print("-" * 60)
print(f"Roast Text:\n{result['text']}")
print("\n📋 Evidence Used:")
for i, evidence in enumerate(result['evidence'], 1):
    print(f"  {i}. {evidence}")

print("\n" + "=" * 60)
print("✅ Demo complete!")
print("=" * 60)
