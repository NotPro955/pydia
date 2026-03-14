# Pydia

Professional profiles and knowledge sources like GitHub and Wikipedia contain valuable information, but they are text-heavy and not easily shareable as engaging content.

## Architecture

```
Input (GitHub username or Wikipedia topic)
                   │
                   ▼
Data Collection (GitHub API / Wikipedia API)
                   │
                   ▼
Content Extraction (skills, projects, facts)
                   │
                   ▼
        Structured Profile Dataset
                   │
                   ▼
          AI Script Generation
                   │
                   ▼
            Video Creation
```

## Setup

### 1. Clone Repository
```bash
git clone https://github.com/NotPro955/pydia.git
cd pydia
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

Then open `http://localhost:7860` in your browser.

## Usage
Enter the username(GitHub/Wikipedia) in the Username Section.

## Output

- Audio saved to `output/<PersonName>_pitch.mp3`
- Script displayed in the UI

## Notes

- Uses **in-memory** ChromaDB — no disk persistence needed
- gTTS requires an internet connection (calls Google's TTS API)
- First run downloads the `all-MiniLM-L6-v2` model (~80MB)
