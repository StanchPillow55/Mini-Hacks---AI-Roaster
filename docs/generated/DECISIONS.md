# 📋 Decisions - AI-Roaster

## ADR-001: Offline Toxicity Detection with Detoxify

### Status
Accepted

### Context
Need to filter toxic content from LLM-generated roasts. Options:
1. Google Perspective API (external, requires API key)
2. Detoxify (local, offline ML model)

### Decision
Use Detoxify with the 'unbiased' model variant.

### Rationale
- **No API keys needed** for toxicity (reduces setup friction)
- **No network calls** = faster response, better privacy
- **No rate limits** = unlimited checks
- **Works offline** once model downloaded

### Consequences
- First run downloads ~100MB model
- CPU-only inference (no GPU optimization)
- Model quality may differ from Perspective API
- Backup implementation kept in `toxicity_perspective_backup.py`

### Evidence
`src/toxicity.py:1-6`, `README.md:88-106`

---

## ADR-002: Heuristic Mildness Enforcement

### Status
Accepted

### Context
LLM output is unpredictable. Even with safety prompts, roasts may exceed toxicity thresholds.

### Decision
Implement `enforce_mildness()` with regex-based heuristics:
1. Lowercase ALL CAPS words
2. Replace profanity with hints (f***)
3. Soften intensifiers
4. Remove slurs from blocklist
5. Trim ad hominem patterns

### Rationale
- Deterministic (unlike LLM rewrite)
- Fast (no API call)
- Preserves core meaning

### Consequences
- May alter intended phrasing
- Regex patterns require maintenance
- Only applied in mild mode or when too_hot

### Evidence
`src/toxicity.py:63-147`

---

## ADR-003: Dual LLM Provider Support

### Status
Accepted

### Context
Dependency on single LLM provider creates risk.

### Decision
Support both OpenAI and Anthropic with auto-detection and fallback.

### Rationale
- User choice
- Redundancy
- Cost flexibility

### Consequences
- More complex provider logic
- Different model behaviors
- Demo mode when no keys available

### Evidence
`src/llm.py:337-378`

---

## ADR-004: Session State for UI Persistence

### Status
Accepted

### Context
Streamlit reruns script on every interaction.

### Decision
Use `st.session_state.*` for all UI state variables.

### Evidence
`streamlit_app.py:61-83`

---

## ADR-005: Evidence Quoting in Roasts

### Status
Accepted

### Context
Users should see what data the AI used (transparency).

### Decision
LLM instructed to quote profile data. Post-processing extracts and matches quotes.

### Evidence
`src/llm.py:99-162`

---

## ADR-006: Graceful Scrape Failure

### Status
Accepted

### Decision
On scrape failure: show warning, use demo profile, continue.

### Evidence
`streamlit_app.py:116-129`
