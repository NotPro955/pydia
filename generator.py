"""
Phase 4: Generate a sarcastic, funny infomercial pitch using Groq.

No emotion bracket tags needed — Qwen3-TTS handles expression via
its natural language `instruct` parameter instead.

Primary:  Groq (llama-3.3-70b-versatile) — free at console.groq.com
Fallback: Ollama (local llama3)
"""

import os
import requests


GROQ_URL   = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama-3.3-70b-versatile"

OLLAMA_URL   = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3"


SYSTEM_PROMPT = """You are a fast-talking, unhinged TV infomercial host from the 90s who sells PEOPLE like products on a home shopping channel.

YOUR JOB: Write a 30-45 second spoken sales pitch for a real human being.

THE TONE:
- Sarcastic but affectionate — roasting them while being their biggest fan
- QVC host meets stand-up comedian who just Wikipedia'd their subject
- Absurd product-pitch language: "Factory-installed with...", "Ships pre-loaded with...", "Call now!", "Limited stock!", "But wait, there's more!"
- Treat real achievements like ridiculous product features
- Build energy toward an absurd punchline closer

RULES:
1. Every joke must reference a SPECIFIC real fact from the context — real numbers, names, awards, projects, dates.
2. Output ONLY the spoken script. No stage directions, no markdown, no asterisks, no headers, no bracket tags.
3. 80-110 words. Punchy sentences. Escalating energy.
4. End with a fake absurd tagline or call-to-action.
5. BANNED words: "visionary", "passionate", "innovative", "trailblazer", "game-changer", "revolutionary", "journey"."""


def _generate_with_groq(person_name: str, context: str, api_key: str) -> str:
    prompt = f"""Real facts about {person_name} pulled from their public profile:

---
{context}
---

Write the sarcastic infomercial pitch for {person_name}.
Ground every joke in the real facts above. Script only, no preamble."""

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": GROQ_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": prompt},
        ],
        "temperature": 0.93,
        "max_tokens": 400,
        "top_p": 0.95,
    }
    resp = requests.post(GROQ_URL, headers=headers, json=payload, timeout=30)
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"].strip()


def _ollama_running() -> bool:
    try:
        return requests.get("http://localhost:11434", timeout=3).status_code == 200
    except Exception:
        return False


def _generate_with_ollama(person_name: str, context: str) -> str:
    if not _ollama_running():
        raise RuntimeError(
            "No GROQ_API_KEY set and Ollama is not running.\n"
            "Add GROQ_API_KEY to .env (free at console.groq.com) or run: ollama serve"
        )
    prompt = f"""{SYSTEM_PROMPT}

Facts about {person_name}:
---
{context}
---

Write the sarcastic infomercial pitch now. Script only."""

    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.93, "num_predict": 400, "repeat_penalty": 1.2},
    }
    resp = requests.post(OLLAMA_URL, json=payload, timeout=120)
    resp.raise_for_status()
    return resp.json().get("response", "").strip()


def _clean(text: str) -> str:
    """Strip preamble/markdown the model may have added."""
    import re
    skip = ("here is", "here's", "script:", "pitch:", "---", "sure!", "of course", "absolutely", "okay,")
    lines = []
    for line in text.splitlines():
        s = line.strip()
        if not s:
            continue
        if s.lower().startswith(skip):
            continue
        # Remove markdown but keep regular punctuation
        s = s.replace("**", "").replace("*", "").replace("__", "").replace("##", "")
        # Remove any bracket tags in case model still adds them
        s = re.sub(r'\[.*?\]', '', s).strip()
        if s:
            lines.append(s)
    return " ".join(lines)


def generate_pitch(person_name: str, context: str) -> str:
    """Generate sarcastic sales pitch. Uses Groq if key set, else Ollama."""
    groq_key = os.getenv("GROQ_API_KEY", "").strip()

    if groq_key:
        print(f"[Generator] Groq ({GROQ_MODEL})...")
        try:
            pitch = _generate_with_groq(person_name, context, groq_key)
            pitch = _clean(pitch)
            print(f"[Generator] {len(pitch.split())} words")
            return pitch
        except Exception as e:
            print(f"[Generator] Groq failed ({e}), trying Ollama...")

    print(f"[Generator] Ollama ({OLLAMA_MODEL})...")
    pitch = _generate_with_ollama(person_name, context)
    pitch = _clean(pitch)
    print(f"[Generator] {len(pitch.split())} words")
    return pitch
