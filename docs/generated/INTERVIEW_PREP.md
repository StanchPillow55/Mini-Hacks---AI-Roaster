# 🎯 Interview Prep - AI-Roaster

**Last Updated:** 2026-04-29
**Documentation Pointers:** All claims link to internal docs in `docs/generated/`

---

## 60-90 Second STAR Pitch

### Situation
Hackathon project for "Mini-Hacks" - needed a fun, viral-ready app that demonstrates AI safety principles while being entertaining.

### Task
Build an AI roast generator that's funny but not harmful - balancing entertainment value with responsible AI content filtering.

### Action
- Built **Streamlit web app** with modular Python backend
- Integrated **dual LLM providers** (OpenAI, Anthropic) with auto-fallback
- Implemented **offline toxicity detection** using Detoxify ML model
- Created **5 persona templates** with configurable mildness levels
- Added **profile scraping** for GitHub, generic URLs, and resume uploads
- Built **post-generation safety net** with heuristic text softening

### Result

| Metric | Status | Evidence |
|--------|--------|----------|
| MVP Demo Ready | **Confirmed** | `test_e2e.py` passes all 9 checks |
| Toxicity Detection | **Confirmed** | Detoxify scores 0.0-1.0 per text |
| Multi-provider LLM | **Confirmed** | OpenAI + Anthropic with fallback |
| 5 Persona Templates | **Confirmed** | `src/personas.py:34-75` |
| GitHub Scraping | **Confirmed** | API + HTML fallback |

---

## Technical Deep Dive

### Architecture
- **Frontend:** Streamlit (single-page app)
- **Backend:** Modular Python (personas, scraper, llm, toxicity, share)
- **ML:** Detoxify 'unbiased' model for toxicity scoring
- **LLM:** OpenAI GPT-3.5-turbo or Anthropic Claude

**Full details:** → `ARCHITECTURE.md`

### Key Tradeoffs

**Offline Toxicity (Detoxify vs Perspective API):**
- Chose Detoxify for zero API keys, faster, more private
- Trade-off: ~100MB model download, CPU-only

**Heuristic Mildness vs LLM Rewrite:**
- Chose regex heuristics for determinism and speed
- Trade-off: May alter phrasing, can't catch all edge cases

**Dual LLM Support:**
- Supports OpenAI and Anthropic with auto-detection
- Trade-off: More complex, different model behaviors

**Full details:** → `DECISIONS.md`

---

## Drill-Down Q&A

### Q1: "How do you prevent the AI from generating harmful content?"

**Answer (Confirmed):** Three-layer defense:
1. **System prompt** with explicit safety rules (`SAFETY_SYSTEM_PROMPT`)
2. **Toxicity scoring** via Detoxify after generation
3. **Heuristic enforcement** if score exceeds threshold

**Evidence:** `src/llm.py:9-26`, `src/toxicity.py:26-60`

### Q2: "What happens if the toxicity score is too high?"

**Answer (Confirmed):** 
1. `map_label(score, mode)` returns "too_hot"
2. `enforce_mildness()` applies regex transformations
3. Re-score after softening
4. Display with safety label

**Evidence:** `src/toxicity.py:41-60`, `streamlit_app.py:331-340`

### Q3: "How does the mildness enforcement work?"

**Answer (Confirmed):** Regex-based heuristics:
1. Lowercase ALL CAPS → Capitalized
2. Profanity → Hints (f***)
3. Intensifiers → Softer words (absolutely → somewhat)
4. Slurs → [removed]
5. Ad hominems → Neutral phrase
6. Excessive punctuation → Single

**Evidence:** `src/toxicity.py:63-147`

### Q4: "Why Detoxify instead of Perspective API?"

**Answer (Confirmed):**
- No API key needed (reduces setup friction)
- No network calls (faster, more private)
- No rate limits (unlimited checks)
- Works offline after initial download

**Trade-off:** Model quality may differ, ~100MB download.

**Evidence:** `README.md:88-106`, `src/toxicity.py:1-6`

### Q5: "How do you scrape GitHub profiles?"

**Answer (Confirmed):**
1. Regex match for github.com/username
2. Call GitHub API for user data + top 3 repos
3. Fallback to HTML scraping if API fails
4. Return dict with bio, titles, skills, snippets, sources

**Evidence:** `src/scrape_basic.py:42-104`

### Q6: "What personas are available?"

**Answer (Confirmed):** 5 personas with distinct styles:
- **gen_z:** Sarcastic, playful, meme-heavy
- **millennial:** Nostalgic, self-deprecating
- **boomer:** Grumpy, traditional
- **corporate:** Passive-aggressive, buzzword-heavy
- **shakespearean:** Eloquent, theatrical

Each has tone, slang, style notes, banned content, mildness multiplier.

**Evidence:** `src/personas.py:34-75`

### Q7: "How does the improve/comeback flow work?"

**Answer (Confirmed):**
- **Improve:** Append user instruction as "Hint" to style prompt, regenerate
- **Comeback:** Append user's comeback text, ask for one-turn reply

Both go through same toxicity pipeline after generation.

**Evidence:** `streamlit_app.py:401-487`

### Q8: "What if both LLM providers fail?"

**Answer (Confirmed):** System enters demo mode - returns realistic-looking stub roast with note that it's demo mode.

**Evidence:** `src/llm.py:183-206`, `src/llm.py:372-378`

### Q9: "How do you handle scrape failures?"

**Answer (Confirmed):**
1. Show warning banner to user
2. Use demo profile data (generic developer persona)
3. Continue with roast generation
4. Clear indication that data is demo

**Evidence:** `streamlit_app.py:116-129`, `streamlit_app.py:278-283`

### Q10: "What's the testing strategy?"

**Answer (Confirmed):** Manual test scripts (not pytest):
- `test_backend.py`: Module imports, API verification
- `test_e2e.py`: Full pipeline (GitHub → roast → toxicity → share)

9 test assertions covering core features.

**Evidence:** `test_e2e.py:145-155`

---

## Reflection

### Technical Debt (Confirmed)

| Item | Location | Issue |
|------|----------|-------|
| Legacy scraper | `src/scraper.py` | Unused, should remove |
| No pytest | `test_*.py` | Manual scripts only |
| No CI/CD | - | Tests run manually |

### What I'd Do Differently

| Change | Rationale |
|--------|-----------|
| Add pytest framework | Better test organization, CI integration |
| GPU support for Detoxify | Faster inference |
| Rate limiting on scraping | Prevent abuse |
| User accounts | Save roast history |

---

## Quick Reference Pointers

| Topic | Document |
|-------|----------|
| Architecture | `docs/generated/ARCHITECTURE.md` |
| Decisions/ADRs | `docs/generated/DECISIONS.md` |
| Testing | `docs/generated/TESTING.md` |
| Repo structure | `docs/generated/REPO_MAP.md` |
| Style conventions | `docs/generated/STYLE_NOTES.md` |
