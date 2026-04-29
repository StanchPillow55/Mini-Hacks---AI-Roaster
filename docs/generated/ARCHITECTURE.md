# 🏗️ Architecture - AI-Roaster

## System Overview

```
┌─────────────────┐
│  Streamlit UI   │  (streamlit_app.py)
│  - Input forms  │
│  - Config       │
│  - Display      │
└────────┬────────┘
         │
    ┌────┴────┐
    │ Pipeline│
    └────┬────┘
         │
┌────────┼────────────────────────────────────────┐
│        │           BACKEND MODULES              │
│  ┌─────▼─────┐   ┌──────────┐   ┌───────────┐  │
│  │  Scraper  │   │ Personas │   │    LLM    │  │
│  │ (GitHub/  │   │ (Style   │   │ (OpenAI/  │  │
│  │  URLs/    │   │  prompt  │   │ Anthropic)│  │
│  │  Resume)  │   │  builder)│   │           │  │
│  └─────┬─────┘   └────┬─────┘   └─────┬─────┘  │
│        │              │               │         │
│        └──────────────┼───────────────┘         │
│                       │                         │
│               ┌───────▼───────┐                 │
│               │   Toxicity    │                 │
│               │  (Detoxify +  │                 │
│               │   Mildness)   │                 │
│               └───────┬───────┘                 │
│                       │                         │
│               ┌───────▼───────┐                 │
│               │    Share      │                 │
│               │  (Copy/Tweet) │                 │
│               └───────────────┘                 │
└─────────────────────────────────────────────────┘
```

## Data Flow

### 1. Profile Extraction
```
Input URL/File → extract_profile_from_url() or extract_from_resume()
                         ↓
                 Dict{name, bio, titles, skills, snippets, sources}
```

**GitHub URL Path:**
1. Regex match for github.com/username pattern
2. Call GitHub API for user data
3. Fetch top 3 repos for snippets
4. Fallback to HTML scraping if API fails

**Generic URL Path:**
1. Fetch HTML with requests
2. Extract title + meaningful paragraphs
3. Readability heuristics (50-500 char paragraphs)

**Resume Path:**
1. Try UTF-8 decode
2. Fallback to pypdf extraction
3. Heuristic extraction (name, titles, skills)

### 2. Style Prompt Generation
```
persona + custom_text + mildness → build_style_prompt()
                                           ↓
                                   Style prompt string with:
                                   - Tone, Slang, Target
                                   - Intensity label
                                   - Style notes, Guardrails
```

**Personas:** gen_z, millennial, boomer, corporate, shakespearean
**Mildness:** 0.0 (gentle) → 1.0 (maximum spice)

### 3. Roast Generation
```
profile + style_prompt → generate_roast(provider)
                                 ↓
                         Dict{text, evidence, quoted_evidence}
```

**Safety System Prompt:** Embedded rules for:
- No slurs/hate speech
- No sexual content
- Focus on public info, choices, behaviors
- Evidence quoting rules

**Provider Selection:**
1. Check environment for API keys
2. Auto-fallback if primary unavailable
3. Demo mode if no keys

### 4. Toxicity Check & Enforcement
```
roast_text → score_toxicity() → toxicity float (0.0-1.0)
                 ↓
         map_label(score, mode) → "ok" | "too_hot"
                 ↓
         (if too_hot or mild mode)
         enforce_mildness() → softened text
```

**Thresholds:**
- Mild: < 0.15
- Normal: < 0.30
- Brutal: < 0.50

**Mildness Enforcement (Heuristics):**
1. Lowercase ALL CAPS words
2. Replace profanity with hints (f***)
3. Soften intensifiers (absolutely → somewhat)
4. Remove slurs list
5. Trim ad hominem attacks
6. Reduce excessive punctuation

### 5. Display & Actions
```
Final roast → UI display with:
             - Toxicity badge (Low/Medium/High)
             - Safety label (SAFE/TOO HOT)
             - Evidence snippets
             - Actions (Improve, Comeback, Copy, Tweet)
```

## Key Design Decisions

### Offline Toxicity Detection
- **Why:** No API keys needed, faster, more private, no rate limits
- **How:** Detoxify 'unbiased' model (~100MB, lazy loaded)
- **Trade-off:** Model quality vs external API (Perspective)

### Dual LLM Provider Support
- **Why:** Flexibility, redundancy
- **How:** Auto-detect from env vars, graceful fallback
- **Trade-off:** Complexity vs resilience

### Heuristic Mildness Enforcement
- **Why:** LLM output unpredictable, need safety net
- **How:** Regex-based text transformations
- **Trade-off:** May alter meaning, but safer

### Demo Mode
- **Why:** Allow testing without API keys
- **How:** Realistic-looking stub responses
- **Trade-off:** Not representative of real output quality
