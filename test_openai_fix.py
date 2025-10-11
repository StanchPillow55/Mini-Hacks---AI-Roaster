#!/usr/bin/env python3
"""Quick test to verify OpenAI client fix"""

from dotenv import load_dotenv
load_dotenv()

from src.llm import generate_roast
from src.personas import build_style_prompt

profile = {
    'name': 'TestUser',
    'bio': 'Python developer',
    'snippets': ['Repo: hello-world']
}

style = build_style_prompt('gen_z', mildness=0.5)
print('Testing OpenAI client...')
try:
    result = generate_roast(profile, style, provider='openai')
    print(f'✅ SUCCESS! Result: {result["text"][:150]}...')
    print(f'Evidence count: {len(result["evidence"])}')
except Exception as e:
    print(f'❌ ERROR: {e}')
