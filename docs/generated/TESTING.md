# 🧪 Testing - AI-Roaster

## Test Structure

### Test Files
| File | Purpose | Type |
|------|---------|------|
| `test_backend.py` | Module imports, API verification | Integration |
| `test_e2e.py` | Full pipeline verification | E2E |
| `test_conversation_mode.py` | Conversation features | Feature |
| `test_llm_demo.py` | LLM demo mode | Unit |
| `test_openai_fix.py` | OpenAI client fix | Regression |
| `test_direct_api.py` | Direct API calls | Integration |

### Running Tests

```bash
# Activate virtual environment
source venv/bin/activate

# Run backend verification
python test_backend.py

# Run E2E test (requires API keys)
python test_e2e.py

# Run with demo mode (no API keys needed)
USE_DEMO_MODE=true python test_e2e.py
```

## Test Coverage

### test_backend.py
**Purpose:** Verify all backend modules load and basic functions work

**Tests:**
1. Module imports (personas, scrape_basic, llm, toxicity)
2. Environment variable checks (API keys)
3. Personas module (get_persona_names, build_style_prompt)
4. Scraper module (extract_profile_from_url with GitHub)
5. LLM module (generate_roast with minimal profile)
6. Toxicity module (check_toxicity, is_safe_roast)

**Sample Output:**
```
TEST 1: Module Imports
✅ src.personas imported successfully
✅ src.scrape_basic imported successfully
✅ src.llm imported successfully
✅ src.toxicity imported successfully
```

### test_e2e.py
**Purpose:** Full pipeline verification from input to output

**Tests:**
1. GitHub URL Profile Extraction
2. Roast Generation
3. Toxicity Scoring
4. Mildness Enforcement (if needed)
5. Evidence Snippets
6. Improve Flow
7. Comeback Flow
8. Share Functions
9. Resume File Processing

**Expected Results:**
```
E2E TEST SUMMARY
✅ PASS: GitHub Profile Extraction
✅ PASS: Roast Generation
✅ PASS: Toxicity Scoring
✅ PASS: Safety Label
✅ PASS: Evidence Snippets
✅ PASS: Improve Flow
✅ PASS: Comeback Flow
✅ PASS: Share Functions
✅ PASS: Resume Processing

🎉 MVP DEMO READY: YES
```

## Manual Testing

### Streamlit App
```bash
streamlit run streamlit_app.py
```

**Test Cases:**
1. **GitHub URL:** Enter `https://github.com/torvalds`, generate roast
2. **Generic URL:** Enter any public profile URL
3. **Resume Upload:** Upload PDF or TXT file
4. **Persona Selection:** Test each persona (IShowSpeed, ElonMusk, etc.)
5. **Harshness Slider:** Test 0%, 50%, 100%
6. **Safety Toggle:** Test with/without protected-class filter
7. **Improve:** Generate, then improve with instruction
8. **Comeback:** Generate, then test comeback flow

### Toxicity Module
```bash
python -c "
from src.toxicity import score_toxicity, map_label, enforce_mildness

# Test samples
samples = [
    'Your code is absolutely terrible and you are an idiot!',
    'This looks like a beginner made it, but keep trying.',
    'Nice work! Clean and efficient.'
]

for s in samples:
    score = score_toxicity(s)['toxicity']
    print(f'{s[:50]}... → {score:.3f}')
"
```

## Detoxify Model Scores

The `unbiased` model returns these attributes:
- toxicity (primary)
- severe_toxicity
- obscene
- threat
- insult
- identity_attack
- sexual_explicit

Only `toxicity` is used for gating; others available for detailed analysis.

## Known Limitations

1. **No pytest:** Tests are manual scripts with print verification
2. **API Dependency:** Full E2E requires OpenAI/Anthropic keys
3. **Rate Limits:** GitHub scraping limited to 60/hour without token
4. **Model Download:** First Detoxify run downloads ~100MB model

## CI/CD Status
**Not Configured** - Tests run manually. No GitHub Actions or CI pipeline.
