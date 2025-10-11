# Step 14: Commit Plan

**Branch:** `working`  
**Target:** Ready for PR to `main`

---

## 📋 Git Status Summary

```
On branch working
No commits yet
Untracked files: 25 files
```

---

## 🎯 Proposed Commit Breakdown

### **Commit 1: Initial project structure and documentation**
```bash
git add .gitignore README.md .env.example requirements.txt
git commit -m "feat: Initialize AI Roaster MVP project structure

- Add .gitignore for Python, venv, and sensitive files
- Add README with project overview and setup instructions
- Add .env.example template for API keys
- Add requirements.txt with all dependencies (streamlit, openai, detoxify, etc.)"
```

**Files:** `.gitignore`, `README.md`, `.env.example`, `requirements.txt`

---

### **Commit 2: Add core backend modules**
```bash
git add src/personas.py src/scrape_basic.py src/share.py
git commit -m "feat: Add core backend modules for personas, scraping, and sharing

- personas.py: 5 persona templates (gen_z, millennial, boomer, corporate, shakespearean)
- scrape_basic.py: GitHub API integration and generic webpage scraping
- share.py: Utility functions for sharing and copying roasts"
```

**Files:** `src/personas.py`, `src/scrape_basic.py`, `src/share.py`

---

### **Commit 3: Add toxicity detection with Detoxify**
```bash
git add src/toxicity.py
git commit -m "feat: Add offline toxicity detection using Detoxify

- score_toxicity(): Returns toxicity score 0-1
- map_label(): Maps score to 'ok' or 'too_hot' based on mode thresholds
- enforce_mildness(): Heuristic text softening (caps, profanity, intensifiers, slurs)
- Thresholds: mild=0.15, normal=0.30, brutal=0.50
- Fully offline, no API key required"
```

**Files:** `src/toxicity.py`

---

### **Commit 4: Add LLM integration with enhanced evidence**
```bash
git add src/llm.py
git commit -m "feat: Add LLM integration with OpenAI and Anthropic support

- generate_roast(): Main function with provider auto-detection
- Enhanced evidence extraction with quoted snippets
- OpenAI GPT-3.5-turbo integration with httpx client fix
- Anthropic Claude support as fallback
- Safety system prompt with evidence rules
- Demo mode for testing without API credits"
```

**Files:** `src/llm.py`

---

### **Commit 5: Add Streamlit UI with full backend integration**
```bash
git add streamlit_app.py
git commit -m "feat: Add Streamlit UI with complete backend integration

- Profile input via URL or file upload
- Persona selection (IShowSpeed, ElonMusk, Coworker, GenZ, Custom)
- Toxicity level selection (Mild, Normal, Brutal)
- Generate button with full pipeline (profile → style → LLM → toxicity → enforcement)
- Improve feature: Takes instruction hint, regenerates roast
- Comeback feature: Takes user response, generates one-turn reply
- Copy feature: Formatted text for clipboard
- Tweet button: Prefilled Twitter intent URL
- Discord placeholder
- Evidence display in expandable section
- Toxicity score with color coding and safety label"
```

**Files:** `streamlit_app.py`

---

### **Commit 6: Add test scripts and documentation**
```bash
git add test_backend.py test_conversation_mode.py test_e2e.py verify_step7.py \
        demo_scrape_basic.py test_openai_fix.py test_direct_api.py test_llm_demo.py \
        BACKEND_VERIFICATION_SUMMARY.md CONVERSATION_MODE_TEST_RESULTS.md \
        DETOXIFY_MIGRATION_SUMMARY.md STEP4_MVP_PLAN_COMPLETE.md \
        STEP7_COMPLETION_REPORT.md STEP10_STATUS.md STEP13_E2E_REPORT.md
git commit -m "docs: Add comprehensive test suite and documentation

Test Scripts:
- test_e2e.py: End-to-end verification of all features
- test_backend.py: Backend module verification
- test_conversation_mode.py: Toxicity and evidence extraction tests
- verify_step7.py: Toxicity module contract verification
- Demo scripts for scraping and LLM

Documentation:
- Backend verification summary with module contracts
- Conversation mode test results
- Detoxify migration documentation
- MVP plan completion report
- Step 7 toxicity module report
- Step 10 integration status
- Step 13 E2E test results

All tests passing, MVP demo-ready"
```

**Files:** All test scripts and markdown documentation

---

### **Commit 7: Add Step 10 patches (informational)**
```bash
git add STEP10_PATCH.md STEP10_INTEGRATION_PATCH.md STEP10_ENHANCED_PATCH.md
git commit -m "docs: Add Step 10 integration patches for reference

- STEP10_PATCH.md: Initial integration plan
- STEP10_INTEGRATION_PATCH.md: Core backend integration patch
- STEP10_ENHANCED_PATCH.md: Conversation mode + enhanced evidence patch

These documents show the evolution of the integration approach"
```

**Files:** `STEP10_PATCH.md`, `STEP10_INTEGRATION_PATCH.md`, `STEP10_ENHANCED_PATCH.md`

---

## ❌ Files to Exclude

**Do NOT commit:**
- `.env` - Contains actual API keys (already in .gitignore)
- `.env.bak` - Backup of .env with keys
- `streamlit.log` - Runtime logs
- `e2e_test_results.txt` - Test output (regenerable)
- `__pycache__/` - Python cache (in .gitignore)
- `venv/` - Virtual environment (in .gitignore)

---

## 📝 Exact Git Commands (DO NOT RUN YET)

```bash
# Commit 1: Project structure
git add .gitignore README.md .env.example requirements.txt
git commit -m "feat: Initialize AI Roaster MVP project structure

- Add .gitignore for Python, venv, and sensitive files
- Add README with project overview and setup instructions
- Add .env.example template for API keys
- Add requirements.txt with all dependencies (streamlit, openai, detoxify, etc.)"

# Commit 2: Core backend
git add src/personas.py src/scrape_basic.py src/share.py
git commit -m "feat: Add core backend modules for personas, scraping, and sharing

- personas.py: 5 persona templates (gen_z, millennial, boomer, corporate, shakespearean)
- scrape_basic.py: GitHub API integration and generic webpage scraping
- share.py: Utility functions for sharing and copying roasts"

# Commit 3: Toxicity detection
git add src/toxicity.py
git commit -m "feat: Add offline toxicity detection using Detoxify

- score_toxicity(): Returns toxicity score 0-1
- map_label(): Maps score to 'ok' or 'too_hot' based on mode thresholds
- enforce_mildness(): Heuristic text softening (caps, profanity, intensifiers, slurs)
- Thresholds: mild=0.15, normal=0.30, brutal=0.50
- Fully offline, no API key required"

# Commit 4: LLM integration
git add src/llm.py
git commit -m "feat: Add LLM integration with OpenAI and Anthropic support

- generate_roast(): Main function with provider auto-detection
- Enhanced evidence extraction with quoted snippets
- OpenAI GPT-3.5-turbo integration with httpx client fix
- Anthropic Claude support as fallback
- Safety system prompt with evidence rules
- Demo mode for testing without API credits"

# Commit 5: Streamlit UI
git add streamlit_app.py
git commit -m "feat: Add Streamlit UI with complete backend integration

- Profile input via URL or file upload
- Persona selection (IShowSpeed, ElonMusk, Coworker, GenZ, Custom)
- Toxicity level selection (Mild, Normal, Brutal)
- Generate button with full pipeline (profile → style → LLM → toxicity → enforcement)
- Improve feature: Takes instruction hint, regenerates roast
- Comeback feature: Takes user response, generates one-turn reply
- Copy feature: Formatted text for clipboard
- Tweet button: Prefilled Twitter intent URL
- Discord placeholder
- Evidence display in expandable section
- Toxicity score with color coding and safety label"

# Commit 6: Tests and docs
git add test_backend.py test_conversation_mode.py test_e2e.py verify_step7.py demo_scrape_basic.py test_openai_fix.py test_direct_api.py test_llm_demo.py BACKEND_VERIFICATION_SUMMARY.md CONVERSATION_MODE_TEST_RESULTS.md DETOXIFY_MIGRATION_SUMMARY.md STEP4_MVP_PLAN_COMPLETE.md STEP7_COMPLETION_REPORT.md STEP10_STATUS.md STEP13_E2E_REPORT.md
git commit -m "docs: Add comprehensive test suite and documentation

Test Scripts:
- test_e2e.py: End-to-end verification of all features
- test_backend.py: Backend module verification
- test_conversation_mode.py: Toxicity and evidence extraction tests
- verify_step7.py: Toxicity module contract verification
- Demo scripts for scraping and LLM

Documentation:
- Backend verification summary with module contracts
- Conversation mode test results
- Detoxify migration documentation
- MVP plan completion report
- Step 7 toxicity module report
- Step 10 integration status
- Step 13 E2E test results

All tests passing, MVP demo-ready"

# Commit 7: Integration patches
git add STEP10_PATCH.md STEP10_INTEGRATION_PATCH.md STEP10_ENHANCED_PATCH.md
git commit -m "docs: Add Step 10 integration patches for reference

- STEP10_PATCH.md: Initial integration plan
- STEP10_INTEGRATION_PATCH.md: Core backend integration patch
- STEP10_ENHANCED_PATCH.md: Conversation mode + enhanced evidence patch

These documents show the evolution of the integration approach"
```

---

## ✅ Summary

**Total Commits:** 7  
**Files to Commit:** 25  
**Files to Exclude:** 3-4 (sensitive/generated)

**Commit Order:**
1. Project structure
2. Core backend modules
3. Toxicity detection
4. LLM integration
5. Streamlit UI
6. Tests & documentation
7. Integration patches

**Ready for Step 15** upon your "commit now" command.
