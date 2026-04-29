# 🗺️ Repo Map - AI-Roaster

## Project Overview
Streamlit-based AI roast generator that creates personalized, safe, and entertaining roasts using public profile data.

## Directory Structure

```
Mini-Hacks---AI-Roaster/
├── streamlit_app.py          # Main Streamlit UI (528 lines)
├── requirements.txt          # Python dependencies
├── README.md                 # Project documentation
├── .env.example              # Environment variable template
│
├── src/                      # Backend modules
│   ├── __init__.py           # Package init
│   ├── personas.py           # Roast persona templates (144 lines)
│   ├── scrape_basic.py       # Profile scraping (360 lines)
│   ├── scraper.py            # Legacy scraper (unused)
│   ├── llm.py                # LLM integration (397 lines)
│   ├── toxicity.py           # Detoxify toxicity (183 lines)
│   ├── toxicity_perspective_backup.py  # Perspective API backup
│   └── share.py              # Share/copy utilities
│
├── test_backend.py           # Module verification tests
├── test_e2e.py               # End-to-end verification
├── test_conversation_mode.py # Conversation mode tests
├── test_llm_demo.py          # LLM demo tests
├── test_openai_fix.py        # OpenAI fix tests
├── test_direct_api.py        # Direct API tests
│
├── demo_scrape_basic.py      # Scraping demo script
│
├── venv/                     # Virtual environment (gitignored)
│
└── docs/
    └── generated/            # Generated documentation
```

## Core Files

### Entry Point
| File | Purpose |
|------|---------|
| `streamlit_app.py` | Main UI - handles input, config, roast generation, display |

### Backend Modules (`src/`)
| File | Purpose | Key Functions |
|------|---------|---------------|
| `personas.py` | Persona templates (GenZ, Millennial, Boomer, Corporate, Shakespearean) | `build_style_prompt()`, `PERSONAS` |
| `scrape_basic.py` | Profile extraction from URLs/resumes | `extract_profile_from_url()`, `extract_from_resume()` |
| `llm.py` | OpenAI/Anthropic roast generation | `generate_roast()`, `get_available_providers()` |
| `toxicity.py` | Detoxify toxicity detection | `score_toxicity()`, `map_label()`, `enforce_mildness()` |
| `share.py` | Share/copy utilities | `format_copy_text()` |

### Test Files
| File | Purpose |
|------|---------|
| `test_backend.py` | Module import and API verification |
| `test_e2e.py` | Full pipeline test (GitHub → roast → toxicity → share) |

## Dependencies
See `requirements.txt`:
- **Core:** streamlit
- **Scraping:** requests, beautifulsoup4, pypdf, httpx
- **ML:** detoxify, torch, transformers, sentencepiece
- **LLM APIs:** openai, anthropic
- **Utilities:** python-dotenv, lxml, pandas

## Configuration
| Variable | Required | Purpose |
|----------|----------|---------|
| `OPENAI_API_KEY` | One of these | LLM provider |
| `ANTHROPIC_API_KEY` | One of these | LLM provider |
| `GITHUB_TOKEN` | Optional | Higher rate limits |
| `USE_DEMO_MODE` | Optional | Force demo mode |
