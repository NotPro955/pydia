"""
Phase 4: Generate a sarcastic infomercial pitch using Groq.

Primary:  Groq (llama-3.3-70b-versatile)
Fallback: Ollama (local llama3)
"""

import os
import re
import requests


GROQ_URL   = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama-3.3-70b-versatile"

OLLAMA_URL   = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3"


SYSTEM_PROMPT = """You are a sketchy black market dealer hawking rare goods. You're selling a HIGH-VALUE HUMAN SPECIMEN like contraband—not an employee, but a premium commodity.

YOUR JOB: Write a 30-45 second underground sales pitch for this rare item (a real human being).

THE TONE:
- Street-smart, hushed urgency—like you're moving hot merchandise
- Dark humor meets catalog copy: "Pre-owned with...", "Factory settings include...", "Inquire within", "Moving fast, limited availability"
- Sarcastic roast wrapped in commodity-speak. You're selling the THING, not hiring the person.

STRICT RULES:
1. Every joke must reference a SPECIFIC real fact from the context — real number, name, award, project.
2. Output ONLY the spoken script. No markdown, no asterisks, no headers, no stage directions.
3. EXACTLY 80-100 words. Count carefully. Not 279 words. Not 30 words. 80-100.
4. Short punchy sentences. Build urgency and intrigue.
5. End with a shady closer: fake contact method, underworld slang, or "ask for [codename]."
6. BANNED words: visionary, passionate, innovative, trailblazer, game-changer, revolutionary, journey."""


def _generate_with_groq(person_name: str, context: str, api_key: str) -> str:
    prompt = f"""Real facts about {person_name}:

---
{context}
---

Write the sarcastic infomercial pitch. Script only. Exactly 80-100 words."""

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
        "temperature": 0.92,
        "max_tokens": 200,   # hard cap — 100 words ≈ 130 tokens, 200 gives headroom
    }

    resp = requests.post(GROQ_URL, headers=headers, json=payload, timeout=30)
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"].strip()


def _ollama_running() -> bool:
    try:
        return requests.get("http://localhost:11434", timeout=2).status_code == 200
    except Exception:
        return False


def _generate_with_ollama(person_name: str, context: str) -> str:
    if not _ollama_running():
        raise RuntimeError("Ollama not running and no GROQ_API_KEY set")

    prompt = f"""{SYSTEM_PROMPT}

Facts about {person_name}:
---
{context}
---

Write the pitch now. Script only. 80-100 words."""

    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.92, "num_predict": 200},
    }
    resp = requests.post(OLLAMA_URL, json=payload, timeout=120)
    resp.raise_for_status()
    return resp.json()["response"].strip()


def _clean(text: str) -> str:
    lines = []
    skip = ("here is", "here's", "script:", "sure!", "of course", "absolutely")
    for line in text.splitlines():
        s = line.strip()
        if not s or s.lower().startswith(skip):
            continue
        s = s.replace("**", "").replace("*", "").replace("__", "").replace("##", "")
        s = re.sub(r"\[.*?\]", "", s)
        s = s.replace("—", ", ").replace("–", ", ")
        if s.strip():
            lines.append(s.strip())
    text = " ".join(lines)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def generate_pitch(person_name: str, context: str) -> str:
    groq_key = os.getenv("GROQ_API_KEY", "").strip()

    if groq_key:
        print(f"[Generator] Groq ({GROQ_MODEL})...")
        try:
            pitch = _generate_with_groq(person_name, context, groq_key)
        except Exception as e:
            print(f"[Generator] Groq failed: {e}, trying Ollama...")
            pitch = _generate_with_ollama(person_name, context)
    else:
        print(f"[Generator] Ollama ({OLLAMA_MODEL})...")
        pitch = _generate_with_ollama(person_name, context)

    pitch = _clean(pitch)
    words = len(pitch.split())
    print(f"[Generator] {words} words")

    # Warn if still too long — TTS will be slow
    if words > 120:
        print(f"[Generator] WARNING: {words} words is too long for fast TTS. Consider regenerating.")

    return pitch
