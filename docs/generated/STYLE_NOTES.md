# 🎨 Style Notes - AI-Roaster

## Language & Ecosystem
- **Primary Language:** Python 3.12+
- **Framework:** Streamlit (web UI)
- **ML/AI:** Detoxify (toxicity detection), OpenAI/Anthropic APIs (roast generation)
- **Scraping:** requests, BeautifulSoup4, pypdf

## Code Conventions

### Module Structure
```
src/
├── __init__.py         # Package initialization
├── personas.py         # Roast persona templates
├── scraper.py          # Legacy scraper (unused)
├── scrape_basic.py     # Active scraper implementation
├── llm.py              # LLM integration (OpenAI/Anthropic)
├── toxicity.py         # Detoxify integration
└── share.py            # Share/copy utilities
```

### Naming Conventions
- **Functions:** `snake_case` (e.g., `build_style_prompt`, `score_toxicity`)
- **Constants:** `UPPER_SNAKE_CASE` (e.g., `PERSONAS`, `SAFETY_SYSTEM_PROMPT`)
- **Classes:** Minimal - mostly functional style
- **Private functions:** Prefix with `_` (e.g., `_get_model`, `_extract_evidence`)

### Type Hints
- All public functions use type hints
- Dict returns documented with docstrings
- Example:
```python
def score_toxicity(text: str) -> Dict[str, float]:
    """Returns: Dict with single key "toxicity" -> float score 0.0-1.0"""
```

### Docstrings
- All modules and public functions have docstrings
- Format: Brief description + Args/Returns sections
- Example code in module docstrings (`personas.py:1-31`)

## Error Handling
- Try/except blocks around external API calls
- Graceful fallbacks (demo mode for missing API keys)
- User-visible errors prefixed with emoji (❌, ⚠️)

## Streamlit Patterns
- Session state for all UI state (`st.session_state.*`)
- Custom CSS via `st.markdown(..., unsafe_allow_html=True)`
- `st.rerun()` after state changes
- Columns for layout (`st.columns([1, 1])`)

## Testing Style
- Manual test scripts (not pytest)
- Print-based verification (`print("✅ ...")`)
- E2E tests cover full pipeline
