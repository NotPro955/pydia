# 🎤 Wikipedia RAG Sales Pitch Generator

Turn any Wikipedia person page into a 30–45 second AI-powered audio sales pitch.

## Architecture

```
Wikipedia URL
    │
    ▼
[Phase 1] Scraper (requests + BeautifulSoup)
    │  → Extracts sections, cleans text, chunks into 200-word overlapping segments
    ▼
[Phase 2] Vector Store (ChromaDB + sentence-transformers)
    │  → Embeds chunks with all-MiniLM-L6-v2, stores in-memory ChromaDB
    ▼
[Phase 3] Retrieval
    │  → Queries DB with 5 sales-oriented prompts, deduplicates top chunks
    ▼
[Phase 4] Generation (Claude API via Anthropic SDK)
    │  → Generates 75-100 word punchy spoken sales script
    ▼
[Phase 5] TTS (gTTS)
    │  → Converts script to MP3 audio (~30-45 seconds)
    ▼
[Phase 6] Gradio Web UI
    └  → Real-time status log, script display, audio playback
```

## Setup

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Set your Anthropic API key
```bash
export ANTHROPIC_API_KEY=your_key_here
```

### 3. Run the app
```bash
python app.py
```

Then open `http://localhost:7860` in your browser.

## Usage

1. Paste any Wikipedia URL (e.g. `https://en.wikipedia.org/wiki/Nikola_Tesla`)
2. Click **Generate Pitch**
3. Watch the pipeline run step by step
4. Read the generated script and play the audio

## Output

- Audio saved to `output/<PersonName>_pitch.mp3`
- Script displayed in the UI

## Notes

- Uses **in-memory** ChromaDB — no disk persistence needed
- gTTS requires an internet connection (calls Google's TTS API)
- First run downloads the `all-MiniLM-L6-v2` model (~80MB)
