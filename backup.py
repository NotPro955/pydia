"""
Phase 6: Gradio web UI — Pydia Studio aesthetic + full RAG pipeline.
Run: python app.py
"""

import os
import sys

APP_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = APP_DIR
sys.path.insert(0, SRC_DIR)

from dotenv import load_dotenv
ENV_PATH = os.path.join(APP_DIR, ".env")
loaded = load_dotenv(ENV_PATH, override=True)
print(f"[.env] {'Loaded' if loaded else 'NOT FOUND'}: {ENV_PATH}")

import gradio as gr

from scraper import scrape_and_chunk
from github_adapter import scrape_github_and_chunk
from vector_store import build_vector_store, retrieve_sales_context
from generator import generate_pitch
from tts import text_to_speech
from video_gen import generate_video

OUTPUT_DIR = os.path.join(APP_DIR, "output")

KOKORO_VOICES = [
    "af_heart", "af_bella", "af_sarah", "af_nicole", "af_sky", "af_nova",
    "am_adam", "am_michael", "bm_lewis", "bm_george",
]


# ── Pipeline ───────────────────────────────────────────────────────────────────

def run_pipeline(person_name, chunks, image_url, voice):
    logs = []
    try:
        os.environ["KOKORO_VOICE"] = voice
        logs.append(f" Data collected for **{person_name}** — {len(chunks)} chunks")
        yield "\n\n".join(logs), None, None, None

        logs.append(" Building vector database...")
        yield "\n\n".join(logs), None, None, None
        collection = build_vector_store(person_name, chunks)
        logs.append(f" Vector DB ready ({collection.count()} vectors)")
        yield "\n\n".join(logs), None, None, None

        logs.append(" Retrieving sales-relevant context...")
        yield "\n\n".join(logs), None, None, None
        context = retrieve_sales_context(collection)
        logs.append(" Context retrieved")
        yield "\n\n".join(logs), None, None, None

        logs.append(" Generating pitch with Ollama...")
        yield "\n\n".join(logs), None, None, None
        pitch = generate_pitch(person_name, context)
        logs.append(" Pitch generated")
        yield "\n\n".join(logs), pitch, None, None

        logs.append(f" Generating audio (voice: {voice})...")
        yield "\n\n".join(logs), pitch, None, None
        audio_path = text_to_speech(pitch, person_name, output_dir=OUTPUT_DIR)
        logs.append(" Audio ready")
        yield "\n\n".join(logs), pitch, audio_path, None

        fal_key = os.getenv("FAL_KEY", "").strip()
        if not fal_key:
            logs.append(" FAL_KEY not in .env — skipping video")
            yield "\n\n".join(logs), pitch, audio_path, None
        elif not image_url:
            logs.append(" No image found — skipping video")
            yield "\n\n".join(logs), pitch, audio_path, None
        else:
            logs.append(" Generating video with fal.ai (~30 sec)...")
            yield "\n\n".join(logs), pitch, audio_path, None
            video_path = generate_video(person_name, pitch, audio_path, image_url, output_dir=OUTPUT_DIR)
            if video_path:
                logs.append("✅ Video ready!")
                yield "\n\n".join(logs), pitch, audio_path, video_path
            else:
                logs.append("⚠️ Video failed — audio still available above")
                yield "\n\n".join(logs), pitch, audio_path, None

    except Exception as e:
        logs.append(f"❌ Error: {str(e)}")
        yield "\n\n".join(logs), None, None, None


def run_wikipedia(wiki_url, voice):
    logs = ["🔍 Scraping Wikipedia..."]
    yield "\n\n".join(logs), None, None, None
    try:
        person_name, chunks = scrape_and_chunk(wiki_url)
        image_url = None
        try:
            import requests as req
            from bs4 import BeautifulSoup
            resp = req.get(wiki_url, headers={"User-Agent": "WikiRAGPitch/1.0"}, timeout=8)
            soup = BeautifulSoup(resp.text, "html.parser")
            img = soup.select_one(".infobox img, .thumb img")
            if img and img.get("src"):
                src = img["src"]
                image_url = src if src.startswith("http") else "https:" + src
        except Exception:
            pass
    except Exception as e:
        yield f"❌ Scrape failed: {e}", None, None, None
        return
    yield from run_pipeline(person_name, chunks, image_url, voice)


def run_github(github_username, voice):
    logs = [f"🐙 Scraping GitHub: **{github_username}**..."]
    yield "\n\n".join(logs), None, None, None
    try:
        github_token = os.getenv("GITHUB_TOKEN", "").strip() or None
        person_name, chunks = scrape_github_and_chunk(github_username.strip(), token=github_token)
        image_url = None
        try:
            import requests as req
            resp = req.get(f"https://api.github.com/users/{github_username.strip()}", timeout=8).json()
            image_url = resp.get("avatar_url")
        except Exception:
            pass
    except Exception as e:
        yield f"❌ Scrape failed: {e}", None, None, None
        return
    yield from run_pipeline(person_name, chunks, image_url, voice)


# ── CSS ────────────────────────────────────────────────────────────────────────

CSS = """
/* ── Google Fonts ── */
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Sans:wght@300;400;500;600&display=swap');

/* ── Root tokens ── */
:root {
    --bg:        #0d1117;
    --bg2:       #161b22;
    --bg3:       #1c2333;
    --teal:      #14b8a6;
    --teal-dim:  rgba(20,184,166,0.15);
    --teal-glow: rgba(20,184,166,0.4);
    --cyan:      #06b6d4;
    --text:      #e6edf3;
    --muted:     #8b949e;
    --border:    rgba(255,255,255,0.08);
    --glass:     rgba(22,27,34,0.85);
    --radius:    14px;
    --font-display: 'Bebas Neue', sans-serif;
    --font-body:    'DM Sans', sans-serif;
}

/* ── Reset & base ── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

.gradio-container {
    background: var(--bg) !important;
    font-family: var(--font-body) !important;
    color: var(--text) !important;
    min-height: 100vh;
}

/* ── Animated background blobs ── */
.gradio-container::before,
.gradio-container::after {
    content: '';
    position: fixed;
    border-radius: 50%;
    filter: blur(80px);
    pointer-events: none;
    z-index: 0;
    mix-blend-mode: screen;
    animation: blob 10s ease-in-out infinite;
}
.gradio-container::before {
    width: 500px; height: 500px;
    top: -100px; left: -100px;
    background: radial-gradient(circle, rgba(20,184,166,0.18), transparent 70%);
}
.gradio-container::after {
    width: 400px; height: 400px;
    bottom: -80px; right: -80px;
    background: radial-gradient(circle, rgba(6,182,212,0.15), transparent 70%);
    animation-delay: 4s;
}
@keyframes blob {
    0%,100% { transform: translate(0,0) scale(1); }
    33%      { transform: translate(30px,-40px) scale(1.08); }
    66%      { transform: translate(-20px,20px) scale(0.95); }
}

/* ── Mesh grid overlay ── */
.pydia-header {
    position: relative;
    text-align: center;
    padding: 48px 24px 36px;
    overflow: hidden;
    z-index: 1;
}
.pydia-header::before {
    content: '';
    position: absolute;
    inset: 0;
    background-image:
        linear-gradient(rgba(20,184,166,0.06) 1px, transparent 1px),
        linear-gradient(90deg, rgba(20,184,166,0.06) 1px, transparent 1px);
    background-size: 48px 48px;
    pointer-events: none;
}

/* ── Light streak ── */
.pydia-header::after {
    content: '';
    position: absolute;
    top: 0; left: 0;
    width: 100%; height: 2px;
    background: linear-gradient(90deg, transparent, var(--teal), transparent);
    animation: lightStreak 6s linear infinite;
}
@keyframes lightStreak {
    0%   { transform: translateX(-100%); opacity: 0; }
    50%  { opacity: 1; }
    100% { transform: translateX(100%); opacity: 0; }
}

/* ── Wordmark ── */
.pydia-wordmark {
    font-family: var(--font-display);
    font-size: clamp(2.8rem, 6vw, 5rem);
    letter-spacing: 0.12em;
    color: var(--text);
    line-height: 1;
    text-shadow: 0 0 40px var(--teal-glow);
    animation: fadeInDown 0.8s ease-out;
}
@keyframes fadeInDown {
    from { opacity:0; transform:translateY(-20px); }
    to   { opacity:1; transform:translateY(0); }
}

.pydia-sub {
    margin-top: 10px;
    font-size: 0.9rem;
    color: var(--muted);
    letter-spacing: 0.08em;
    text-transform: uppercase;
    animation: fadeInDown 0.8s ease-out 0.15s backwards;
}

.pydia-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    margin-top: 16px;
    padding: 6px 16px;
    background: var(--teal-dim);
    border: 1px solid var(--teal-glow);
    border-radius: 999px;
    font-size: 0.75rem;
    color: var(--teal);
    letter-spacing: 0.06em;
    font-weight: 600;
    animation: fadeInDown 0.8s ease-out 0.3s backwards;
}
.pydia-badge::before { content: '●'; font-size: 0.5rem; animation: pulse 2s infinite; }
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.3} }

/* ── Section labels ── */
.section-label {
    font-family: var(--font-display);
    font-size: 0.75rem;
    letter-spacing: 0.2em;
    color: var(--teal);
    text-transform: uppercase;
    margin-bottom: 8px;
    padding-left: 2px;
}

/* ── Glass panel ── */
.glass-panel {
    background: var(--glass);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 24px;
    backdrop-filter: blur(12px);
    position: relative;
    z-index: 1;
    transition: border-color 0.3s;
}
.glass-panel:hover { border-color: rgba(20,184,166,0.25); }

/* ── Gradio component overrides ── */

/* Labels */
label, .gr-label, span.svelte-1gfkn6j {
    font-family: var(--font-body) !important;
    color: var(--muted) !important;
    font-size: 0.78rem !important;
    letter-spacing: 0.06em;
    text-transform: uppercase;
}

/* Textboxes & inputs */
textarea, input[type="text"], input[type="url"] {
    background: var(--bg2) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    color: var(--text) !important;
    font-family: var(--font-body) !important;
    font-size: 0.95rem !important;
    transition: border-color 0.25s, box-shadow 0.25s !important;
    caret-color: var(--teal) !important;
}
textarea:focus, input:focus {
    border-color: var(--teal) !important;
    box-shadow: 0 0 0 3px var(--teal-dim) !important;
    outline: none !important;
}
textarea::placeholder, input::placeholder { color: var(--muted) !important; }

/* Primary button */
button.primary, .gr-button-primary, button[variant="primary"] {
    background: linear-gradient(135deg, var(--teal), var(--cyan)) !important;
    border: none !important;
    border-radius: 999px !important;
    color: #0d1117 !important;
    font-family: var(--font-display) !important;
    font-size: 1.05rem !important;
    letter-spacing: 0.1em !important;
    padding: 12px 32px !important;
    cursor: pointer !important;
    transition: transform 0.2s, box-shadow 0.2s !important;
    box-shadow: 0 0 20px var(--teal-glow) !important;
}
button.primary:hover, .gr-button-primary:hover {
    transform: scale(1.04) !important;
    box-shadow: 0 0 32px var(--teal-glow) !important;
}

/* Tabs */
.tab-nav button {
    background: transparent !important;
    border: none !important;
    border-bottom: 2px solid transparent !important;
    color: var(--muted) !important;
    font-family: var(--font-display) !important;
    font-size: 0.95rem !important;
    letter-spacing: 0.1em !important;
    padding: 10px 20px !important;
    transition: color 0.2s, border-color 0.2s !important;
    border-radius: 0 !important;
}
.tab-nav button.selected, .tab-nav button:hover {
    color: var(--teal) !important;
    border-bottom-color: var(--teal) !important;
    background: transparent !important;
}
.tabs { border-color: var(--border) !important; }

/* Dropdown */
select, .gr-dropdown {
    background: var(--bg2) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    color: var(--text) !important;
    font-family: var(--font-body) !important;
}

/* Markdown status box */
.gr-markdown, .gr-prose {
    background: var(--bg2) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    padding: 16px 20px !important;
    color: var(--text) !important;
    font-family: var(--font-body) !important;
    font-size: 0.9rem !important;
    line-height: 1.7 !important;
    min-height: 80px !important;
}

/* Audio player */
.gr-audio {
    background: var(--bg2) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    padding: 12px !important;
}
audio {
    filter: invert(0.85) hue-rotate(155deg) saturate(1.5);
    width: 100%;
    border-radius: 8px;
}

/* Video player */
.gr-video video, video {
    border-radius: var(--radius) !important;
    border: 1px solid var(--border) !important;
    width: 100% !important;
}

/* Examples */
.gr-examples table {
    background: transparent !important;
    border: none !important;
}
.gr-examples td {
    background: var(--bg2) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    color: var(--muted) !important;
    font-size: 0.8rem !important;
    transition: background 0.2s !important;
    cursor: pointer !important;
}
.gr-examples td:hover {
    background: var(--teal-dim) !important;
    color: var(--teal) !important;
}

/* Block backgrounds */
.gr-block, .gr-box, .gr-panel, .contain, .wrap {
    background: transparent !important;
    border: none !important;
}

/* Scrollbar */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(20,184,166,0.3); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: rgba(20,184,166,0.6); }

/* Divider */
.pydia-divider {
    border: none;
    border-top: 1px solid var(--border);
    margin: 8px 0;
}

/* Output section header */
.output-header {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 16px;
}
.output-header-line {
    flex: 1;
    height: 1px;
    background: linear-gradient(90deg, var(--teal-glow), transparent);
}
.output-header-text {
    font-family: var(--font-display);
    font-size: 1rem;
    letter-spacing: 0.15em;
    color: var(--teal);
}

/* Animate in */
@keyframes fadeInUp {
    from { opacity:0; transform:translateY(16px); }
    to   { opacity:1; transform:translateY(0); }
}
.block { animation: fadeInUp 0.5s ease-out backwards; }
"""

# ── HTML fragments ─────────────────────────────────────────────────────────────

HEADER_HTML = """
<div class="pydia-header">
    <div class="pydia-wordmark">PYDIA STUDIO</div>
</div>
"""

OUTPUT_DIVIDER = """
<div class="output-header">
    <div class="output-header-line"></div>
    <div class="output-header-text">OUTPUT</div>
    <div class="output-header-line" style="background:linear-gradient(90deg,transparent,rgba(20,184,166,0.4))"></div>
</div>
"""

# ── Gradio UI ──────────────────────────────────────────────────────────────────

with gr.Blocks(title="PYDIA STUDIO", css=CSS, theme=gr.themes.Base()) as demo:

    gr.HTML(HEADER_HTML)

    with gr.Row():
        with gr.Column(scale=1):

            # Voice selector
            gr.HTML('<div class="section-label">🎙 Voice</div>')
            voice_selector = gr.Dropdown(
                choices=KOKORO_VOICES,
                value="af_heart",
                label="Kokoro Voice",
                info="af_ = female  ·  am_ bm_ = male",
                container=True,
            )

            gr.HTML('<hr class="pydia-divider"/>')

            # Input tabs
            gr.HTML('<div class="section-label">📡 Source</div>')
            with gr.Tabs():

                with gr.Tab("🌐  Wikipedia"):
                    wiki_url = gr.Textbox(
                        label="Wikipedia URL",
                        placeholder="https://en.wikipedia.org/wiki/Nikola_Tesla",
                        lines=1,
                    )
                    wiki_btn = gr.Button("GENERATE PITCH", variant="primary")
                    gr.Examples(
                        examples=[
                            ["https://en.wikipedia.org/wiki/Nikola_Tesla"],
                            ["https://en.wikipedia.org/wiki/Serena_Williams"],
                            ["https://en.wikipedia.org/wiki/Steve_Jobs"],
                        ],
                        inputs=wiki_url,
                        label="Quick load",
                    )

                with gr.Tab("🐙  GitHub"):
                    gh_username = gr.Textbox(
                        label="GitHub Username",
                        placeholder="spirizeon",
                        lines=1,
                    )
                    github_btn = gr.Button("GENERATE PITCH", variant="primary")
                    gr.Examples(
                        examples=[["spirizeon"], ["Nithish-Sri-Ram"], ["lviffy"]],
                        inputs=gh_username,
                        label="Quick load",
                    )

        with gr.Column(scale=2):

            gr.HTML(OUTPUT_DIVIDER)

            # Pipeline status
            gr.HTML('<div class="section-label">⚡ Pipeline</div>')
            status_box = gr.Markdown(value="_Waiting for input..._")

            gr.HTML('<hr class="pydia-divider"/>')

            # Script
            gr.HTML('<div class="section-label">📝 Sales Script</div>')
            pitch_output = gr.Textbox(
                label="Generated Script",
                lines=6,
                interactive=False,
                placeholder="Your pitch will appear here...",
            )

            gr.HTML('<hr class="pydia-divider"/>')

            # Audio + Video side by side
            gr.HTML('<div class="section-label">🎬 Media Output</div>')
            with gr.Row(equal_height=True):
                audio_output = gr.Audio(
                    label="🔊 Audio Pitch",
                    type="filepath",
                )
                video_output = gr.Video(
                    label="🎬 Video Pitch",
                )

    # ── Wire up ────────────────────────────────────────────────────────────────
    wiki_btn.click(
        fn=run_wikipedia,
        inputs=[wiki_url, voice_selector],
        outputs=[status_box, pitch_output, audio_output, video_output],
    )
    github_btn.click(
        fn=run_github,
        inputs=[gh_username, voice_selector],
        outputs=[status_box, pitch_output, audio_output, video_output],
    )


if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    demo.launch(share=True, show_error=True)
