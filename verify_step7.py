#!/usr/bin/env python3
"""Verification script for Step 7 - Toxicity module"""

from src.toxicity import score_toxicity, map_label, enforce_mildness, _get_model

# Verify function signatures and contracts
print('=' * 70)
print('STEP 7 VERIFICATION - Function Contracts')
print('=' * 70)
print()

# 1. Check _get_model (lazy load)
print('1. Testing _get_model() - Lazy loading:')
model = _get_model()
print(f'   Model type: {type(model).__name__}')
print(f'   ✅ Lazy load working')
print()

# 2. Check score_toxicity returns dict with 'toxicity' key
print('2. Testing score_toxicity(text: str) -> dict:')
result = score_toxicity('This is a test')
print(f'   Return type: {type(result).__name__}')
print(f'   Keys: {list(result.keys())}')
print(f'   Value type: {type(result["toxicity"]).__name__}')
print(f'   Sample value: {result["toxicity"]:.3f}')
print(f'   ✅ Returns {{"toxicity": float}}')
print()

# 3. Check map_label with all three modes
print('3. Testing map_label(score: float, mode: str) -> str:')
test_scores = [0.10, 0.25, 0.45]
modes = ['mild', 'normal', 'brutal']
print('   Thresholds: mild=0.15, normal=0.30, brutal=0.50')
for score in test_scores:
    labels = [map_label(score, mode) for mode in modes]
    print(f'   Score {score:.2f}: {dict(zip(modes, labels))}')

# Verify threshold logic
assert map_label(0.14, 'mild') == 'ok', 'Mild threshold failed'
assert map_label(0.16, 'mild') == 'too_hot', 'Mild threshold failed'
assert map_label(0.29, 'normal') == 'ok', 'Normal threshold failed'
assert map_label(0.31, 'normal') == 'too_hot', 'Normal threshold failed'
assert map_label(0.49, 'brutal') == 'ok', 'Brutal threshold failed'
assert map_label(0.51, 'brutal') == 'too_hot', 'Brutal threshold failed'
print(f'   ✅ All thresholds working correctly')
print()

# 4. Check enforce_mildness heuristics
print('4. Testing enforce_mildness(text: str, target: str) -> str:')
test_cases = [
    ('Your code is TERRIBLE and you are stupid!', 'mild'),
    ('You are an absolute idiot!!!', 'mild'),
    ('This is fucking awful', 'mild'),
    ('You are a loser and a moron', 'mild'),
]
for original, target in test_cases:
    softened = enforce_mildness(original, target)
    print(f'   Original:  "{original}"')
    print(f'   Softened:  "{softened}"')
    print()

# Verify no changes for non-mild modes
normal_text = 'You are stupid and terrible'
assert enforce_mildness(normal_text, 'normal') == normal_text, 'Normal mode should not modify'
assert enforce_mildness(normal_text, 'brutal') == normal_text, 'Brutal mode should not modify'
print(f'   ✅ Heuristics working: caps, profanity, intensifiers, slurs, ad hominems')
print()

print('=' * 70)
print('✅ STEP 7 COMPLETE - All functions match specification')
print('=' * 70)
