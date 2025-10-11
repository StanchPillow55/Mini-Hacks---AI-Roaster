# AI Roaster MVP

A Streamlit-based AI roast generator that creates personalized, safe, and entertaining roasts using public profile data.

## Features

- 🎭 **Persona Templates**: Choose from multiple roast styles (IShowSpeed, ElonMusk, Coworker, GenZ, Custom)
- 🔍 **Public Profile Scraping**: Fetches data from GitHub profiles and generic URLs
- 📄 **Resume Upload**: Parse PDFs or text files for roast generation
- 🤖 **LLM Integration**: Uses OpenAI or Anthropic for creative roast generation
- 🛡️ **Offline Toxicity Detection**: Uses Detoxify (no API keys needed)
- 😊 **Mild Mode**: Generate gentler, family-friendly roasts with automatic softening
- 📋 **Transparency**: Shows source snippets used for roast generation
- 📤 **Share & Copy**: Easy sharing with copy-to-clipboard and Twitter integration
- 🔄 **Improve & Comeback**: Iteratively refine roasts or generate comebacks

## Safety Features

- **Offline toxicity detection** via Detoxify (no external API calls)
- Blocks hateful content about protected classes (identity attacks, threats, sexual content)
- Filters severe toxicity with configurable thresholds (mild/normal/brutal modes)
- Automatic mildness enforcement with heuristic softening
- Provides transparency with source data snippets shown to users
- Real-time toxicity scoring displayed for every generated roast

## Quick Start

```bash
# Clone repository
git clone https://github.com/StanchPillow55/Mini-Hacks---AI-Roaster.git
cd Mini-Hacks---AI-Roaster

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies (this may take a few minutes for PyTorch)
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your API keys (see below)

# Run the app
streamlit run streamlit_app.py
```

The app will open in your browser at `http://localhost:8501`

## Environment Setup

### Required API Keys

Create a `.env` file with at least one LLM provider key:

```bash
# Choose at least one:
OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here

# Optional:
DEFAULT_LLM_PROVIDER=openai  # or anthropic
GITHUB_TOKEN=your_token_here  # Higher rate limits for GitHub scraping
```

**Where to get API keys:**
- **OpenAI**: https://platform.openai.com/api-keys
- **Anthropic**: https://console.anthropic.com/
- **GitHub Token** (optional): https://github.com/settings/tokens

### No Toxicity API Key Required! 🎉

This app uses **Detoxify**, an offline toxicity detection model. No external API keys or network calls needed for safety checks.

## Run Commands

```bash
# Standard run
streamlit run streamlit_app.py

# Run with custom port
streamlit run streamlit_app.py --server.port 8502

# Run with auto-reload on code changes
streamlit run streamlit_app.py --server.runOnSave true
```

## Offline Toxicity via Detoxify

This MVP uses **Detoxify** for toxicity detection instead of external APIs like Perspective API.

**Advantages:**
- ✅ No API keys required for toxicity checking
- ✅ No network calls = faster and more private
- ✅ No rate limits or quotas
- ✅ Works offline once model is downloaded

**How it works:**
- First run downloads the model (~100MB) automatically
- Subsequent runs use the cached local model
- Scores returned: toxicity, severe_toxicity, obscene, threat, insult, identity_attack, sexual_explicit

**Thresholds by mode:**
- **Mild**: toxicity < 0.15
- **Normal**: toxicity < 0.30
- **Brutal**: toxicity < 0.50

## Usage

1. **Choose input method**:
   - Upload a resume file (PDF/TXT)
   - Enter a GitHub profile URL
   - Enter any public URL

2. **Select roast persona**:
   - IShowSpeed (energetic gamer style)
   - ElonMusk (tech mogul sarcasm)
   - Coworker (office banter)
   - GenZ (modern internet slang)
   - Custom (provide your own style URL/description)

3. **Choose intensity**:
   - **Mild**: Family-friendly, softened language
   - **Normal**: Balanced roasting
   - **Brutal**: Maximum intensity (still filtered for hate speech)

4. **Generate & iterate**:
   - Click "Generate Roast"
   - View toxicity scores and source snippets
   - Use "Improve" to refine with instructions
   - Use "Comeback" to generate a response
   - Copy or share via Twitter

## Project Structure

```
.
├── streamlit_app.py       # Main Streamlit UI
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variable template
├── README.md             # This file
└── src/
    ├── __init__.py       # Package initialization
    ├── personas.py       # Roast persona templates and style building
    ├── scraper.py        # Profile scraping (GitHub, URLs, resumes)
    ├── llm.py           # LLM integration (OpenAI/Anthropic)
    ├── toxicity.py      # Detoxify integration with mildness enforcement
    └── utils.py         # Share/copy utilities
```

## Safety Notes and Limitations

### What This App Does ✅
- Generates playful, creative roasts for entertainment
- Filters hateful content about protected classes
- Blocks severe toxicity, threats, and sexual content
- Provides mild mode for family-friendly roasts
- Shows transparency with source data

### What This App Does NOT Do ⚠️
- Cannot guarantee 100% appropriate output (LLMs can be unpredictable)
- Not suitable for harassment or bullying
- Should not be used for harmful purposes
- May contain subjective humor that some find offensive
- Scraping is limited to publicly available data only

### Limitations
- **Scraping**: Limited to public profiles; respects robots.txt
- **LLM Output**: May occasionally bypass filters; always review before sharing
- **Toxicity Model**: Detoxify is good but not perfect; edge cases may occur
- **Resume Parsing**: Best-effort extraction; complex PDFs may not parse fully
- **Rate Limits**: GitHub scraping without token limited to 60 requests/hour

### Ethical Use Guidelines
- ✅ Use for fun roasts among consenting friends
- ✅ Use for self-roasting and entertainment
- ✅ Always review output before sharing
- ❌ Do not use for harassment or bullying
- ❌ Do not target individuals without consent
- ❌ Do not use to spread hateful content

## Troubleshooting

**Issue**: "Module not found" errors
- **Solution**: Ensure virtual environment is activated and run `pip install -r requirements.txt`

**Issue**: Slow first run
- **Solution**: Detoxify downloads model on first run (~100MB). Subsequent runs are fast.

**Issue**: "API key not set" warnings
- **Solution**: Add at least one LLM provider key to your `.env` file

**Issue**: GitHub rate limiting
- **Solution**: Add a GitHub token to `.env` for 5000 requests/hour instead of 60

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Test your changes thoroughly
4. Submit a pull request with clear description

## License

MIT License - See LICENSE file for details

---

**Built with ❤️ for safe, entertaining AI roasts**
