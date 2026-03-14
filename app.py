"""
Phase 6: Gradio web UI — Pydia Studio.
Landing page injected directly into document.body via JS (outside Gradio DOM).
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


# ── Pipeline ───────────────────────────────────────────────────────────────────

def run_pipeline(person_name, chunks, image_url, speaker, instruct):
    logs = []
    try:
        os.environ["QWEN_TTS_SPEAKER"]  = speaker or "Ryan"
        os.environ["QWEN_TTS_INSTRUCT"] = instruct or "Fast-talking sarcastic infomercial host"

        logs.append(f"Data collected — {person_name} — {len(chunks)} chunks")
        yield "\n\n".join(logs), None, None, None

        logs.append("Building vector database...")
        yield "\n\n".join(logs), None, None, None
        collection = build_vector_store(person_name, chunks)
        logs.append(f"Vector DB ready — {collection.count()} vectors")
        yield "\n\n".join(logs), None, None, None

        logs.append("Retrieving sales context...")
        yield "\n\n".join(logs), None, None, None
        context = retrieve_sales_context(collection)
        logs.append("Context retrieved")
        yield "\n\n".join(logs), None, None, None

        logs.append("Generating pitch...")
        yield "\n\n".join(logs), None, None, None
        pitch = generate_pitch(person_name, context)
        logs.append("Pitch generated")
        yield "\n\n".join(logs), pitch, None, None

        logs.append(f"Generating audio — {os.environ['QWEN_TTS_SPEAKER']}...")
        yield "\n\n".join(logs), pitch, None, None
        audio_path = text_to_speech(pitch, person_name, output_dir=OUTPUT_DIR)
        logs.append("Audio ready")
        yield "\n\n".join(logs), pitch, audio_path, None

        if not image_url:
            logs.append("No image found — skipping video (will use Charlie Kirk)")
            yield "\n\n".join(logs), pitch, audio_path, None
        else:
            logs.append("Generating video with Charlie Kirk...")
            yield "\n\n".join(logs), pitch, audio_path, None
            video_path = generate_video(person_name, pitch, audio_path, spokesperson_image="charlie_kirk.jpg", output_dir=OUTPUT_DIR)
            if video_path:
                logs.append("Done.")
                yield "\n\n".join(logs), pitch, audio_path, video_path
            else:
                logs.append("Video failed — audio available")
                yield "\n\n".join(logs), pitch, audio_path, None

    except Exception as e:
        logs.append(f"Error: {str(e)}")
        yield "\n\n".join(logs), None, None, None


def run_wikipedia(wiki_url, speaker, instruct):
    logs = ["Scraping Wikipedia..."]
    yield "\n\n".join(logs), None, None, None
    try:
        person_name, chunks = scrape_and_chunk(wiki_url)
        image_url = None
        try:
            import requests as req
            from bs4 import BeautifulSoup
            import re as _re
            resp = req.get(wiki_url, headers={"User-Agent": "WikiRAGPitch/1.0"}, timeout=8)
            soup = BeautifulSoup(resp.text, "html.parser")
            img = soup.select_one(".infobox img, .thumb img")
            if img and img.get("src"):
                src = img["src"]
                if not src.startswith("http"):
                    src = "https:" + src
                full = _re.sub(
                    r"https://upload\.wikimedia\.org/wikipedia/([^/]+)/thumb/([^/]+/[^/]+/[^/]+)/[0-9]+px-[^/]+",
                    r"https://upload.wikimedia.org/wikipedia/\1/\2",
                    src
                )
                image_url = full
        except Exception:
            pass
    except Exception as e:
        yield f"Scrape failed: {e}", None, None, None
        return
    yield from run_pipeline(person_name, chunks, image_url, speaker, instruct)


def run_github(github_username, speaker, instruct):
    logs = [f"Scraping GitHub — {github_username}..."]
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
        yield f"Scrape failed: {e}", None, None, None
        return
    yield from run_pipeline(person_name, chunks, image_url, speaker, instruct)


# ── CSS (studio only — landing styles are in the JS below) ────────────────────

CSS = """
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Sans:ital,wght@0,300;0,400;0,500;0,600;1,300&display=swap');

:root {
    --bg:        #0d1117;
    --bg2:       #161b22;
    --teal:      #14b8a6;
    --teal-dim:  rgba(20,184,166,0.12);
    --teal-glow: rgba(20,184,166,0.4);
    --cyan:      #06b6d4;
    --text:      #e6edf3;
    --muted:     #8b949e;
    --border:    rgba(255,255,255,0.08);
    --radius:    12px;
    --fd: 'Bebas Neue', sans-serif;
    --fb: 'DM Sans', sans-serif;
}

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

.gradio-container {
    background: var(--bg) !important;
    font-family: var(--fb) !important;
    color: var(--text) !important;
    min-height: 100vh;
    padding: 0 !important;
    max-width: 100% !important;
}

/* studio nav */
.st-nav {
    display:flex;align-items:center;justify-content:space-between;
    padding:14px 32px;
    border-bottom:1px solid var(--border);
    background:rgba(13,17,23,.94);
    backdrop-filter:blur(12px);
    position:sticky;top:0;z-index:10;
}
.st-logo {
    font-family:var(--fd);font-size:1.25rem;letter-spacing:.14em;
    color:var(--text);background:none;border:none;cursor:pointer;transition:opacity .2s;
}
.st-logo:hover{opacity:.6;}
.st-back {
    font-size:.75rem;letter-spacing:.1em;text-transform:uppercase;
    color:var(--muted);background:none;border:none;cursor:pointer;
    font-family:var(--fb);transition:color .2s;
}
.st-back:hover{color:var(--teal);}

.st-body { padding:28px 32px; max-width:1400px; margin:0 auto; }

.sl {
    font-family:var(--fd);font-size:.68rem;letter-spacing:.26em;
    color:var(--teal);text-transform:uppercase;margin-bottom:10px;
}
.sd { border:none;border-top:1px solid var(--border);margin:18px 0; }

/* voice dropdown */
.vd-wrap { position:relative; }
.vd-trigger {
    display:flex;align-items:center;justify-content:space-between;
    padding:10px 14px;background:var(--bg2);
    border:1px solid var(--border);border-radius:10px;
    cursor:pointer;transition:all .2s;width:100%;
}
.vd-trigger:hover{border-color:rgba(20,184,166,.4);}
.vd-trigger.open{border-color:var(--teal);box-shadow:0 0 0 3px var(--teal-dim);}
.vd-sel{display:flex;align-items:center;gap:10px;}
.vd-badge{
    width:32px;height:32px;border-radius:8px;
    display:flex;align-items:center;justify-content:center;
    font-size:.7rem;font-weight:700;
    background:linear-gradient(135deg,var(--teal),var(--cyan));
    color:#0d1117;flex-shrink:0;
}
.vd-name{font-size:.95rem;color:var(--text);}
.vd-gender{font-size:.7rem;color:var(--muted);}
.vd-arr{font-size:.7rem;color:var(--muted);transition:transform .2s;flex-shrink:0;}
.vd-trigger.open .vd-arr{transform:rotate(180deg);}
.vd-menu{
    display:none;position:absolute;top:calc(100% + 6px);left:0;right:0;
    background:#1c2333;border:1px solid var(--border);border-radius:12px;
    overflow:hidden;z-index:9000;
    box-shadow:0 16px 48px rgba(0,0,0,.6);
    animation:vdOpen .2s ease-out;
}
.vd-menu.open{display:block;}
@keyframes vdOpen{from{opacity:0;transform:translateY(-6px);}to{opacity:1;transform:translateY(0);}}
.vd-hdr{
    padding:8px 14px 4px;font-size:.62rem;letter-spacing:.2em;
    color:var(--muted);text-transform:uppercase;font-family:var(--fd);
    border-top:1px solid var(--border);
}
.vd-hdr:first-child{border-top:none;}
.vd-item{
    display:flex;align-items:center;gap:10px;
    padding:10px 14px;cursor:pointer;transition:background .15s;
    border:1px solid transparent;margin:2px 6px;border-radius:8px;
}
.vd-item:hover{background:var(--teal-dim);border-color:rgba(20,184,166,.2);}
.vd-item.active{background:var(--teal-dim);border-color:rgba(20,184,166,.4);}
.vd-ibadge{
    width:28px;height:28px;border-radius:6px;
    display:flex;align-items:center;justify-content:center;
    font-size:.65rem;font-weight:700;flex-shrink:0;
}
.vd-ibadge.m{background:linear-gradient(135deg,#1d4ed8,#0891b2);color:#fff;}
.vd-ibadge.f{background:linear-gradient(135deg,#9333ea,#ec4899);color:#fff;}
.vd-iname{font-size:.88rem;color:var(--text);}
.vd-itag{margin-left:auto;font-size:.65rem;color:var(--muted);}
.vd-dot{margin-left:auto;width:6px;height:6px;border-radius:50%;background:var(--teal);
    animation:dotP 1s ease-in-out infinite;}
@keyframes dotP{0%,100%{opacity:1;}50%{opacity:.3;}}

/* output rule */
.out-rule{display:flex;align-items:center;gap:14px;margin:4px 0 18px;}
.orl{flex:1;height:1px;background:linear-gradient(90deg,var(--teal-glow),transparent);}
.orlr{flex:1;height:1px;background:linear-gradient(90deg,transparent,var(--teal-glow));}
.ort{font-family:var(--fd);font-size:.82rem;letter-spacing:.2em;color:var(--teal);}

/* gradio overrides */
label,.gr-label{font-family:var(--fb) !important;color:var(--muted) !important;
    font-size:.73rem !important;letter-spacing:.06em;text-transform:uppercase;}
textarea,input[type="text"],input[type="url"]{
    background:var(--bg2) !important;border:1px solid var(--border) !important;
    border-radius:10px !important;color:var(--text) !important;
    font-family:var(--fb) !important;font-size:.95rem !important;
    transition:border-color .25s,box-shadow .25s !important;caret-color:var(--teal) !important;}
textarea:focus,input:focus{border-color:var(--teal) !important;
    box-shadow:0 0 0 3px var(--teal-dim) !important;outline:none !important;}
textarea::placeholder,input::placeholder{color:var(--muted) !important;opacity:.4 !important;}
button.primary,.gr-button-primary{
    background:linear-gradient(135deg,var(--teal),var(--cyan)) !important;
    border:none !important;border-radius:999px !important;
    color:#0d1117 !important;font-family:var(--fd) !important;
    font-size:1rem !important;letter-spacing:.12em !important;
    padding:11px 28px !important;cursor:pointer !important;
    transition:transform .2s,box-shadow .2s !important;
    box-shadow:0 0 18px var(--teal-glow) !important;}
button.primary:hover{transform:scale(1.04) !important;}
.tab-nav button{background:transparent !important;border:none !important;
    border-bottom:2px solid transparent !important;color:var(--muted) !important;
    font-family:var(--fd) !important;font-size:.88rem !important;
    letter-spacing:.12em !important;padding:10px 18px !important;
    transition:all .2s !important;border-radius:0 !important;}
.tab-nav button.selected,.tab-nav button:hover{color:var(--teal) !important;
    border-bottom-color:var(--teal) !important;background:transparent !important;}
.tabs{border-color:var(--border) !important;}
.gr-markdown,.gr-prose{background:var(--bg2) !important;border:1px solid var(--border) !important;
    border-radius:var(--radius) !important;padding:14px 18px !important;
    color:var(--muted) !important;font-family:var(--fb) !important;
    font-size:.84rem !important;line-height:1.75 !important;
    min-height:68px !important;font-style:italic;}
audio{filter:invert(.85) hue-rotate(155deg) saturate(1.4);width:100%;border-radius:8px;}
.gr-video video,video{border-radius:var(--radius) !important;
    border:1px solid var(--border) !important;width:100% !important;}
.gr-examples table{background:transparent !important;border:none !important;}
.gr-examples td{background:var(--bg2) !important;border:1px solid var(--border) !important;
    border-radius:8px !important;color:var(--muted) !important;
    font-size:.77rem !important;transition:background .2s !important;cursor:pointer !important;}
.gr-examples td:hover{background:var(--teal-dim) !important;color:var(--teal) !important;}
.gr-block,.gr-box,.gr-panel,.contain,.wrap{background:transparent !important;border:none !important;}
::-webkit-scrollbar{width:5px;height:5px;}
::-webkit-scrollbar-track{background:transparent;}
::-webkit-scrollbar-thumb{background:rgba(20,184,166,.25);border-radius:3px;}
::-webkit-scrollbar-thumb:hover{background:rgba(20,184,166,.5);}
"""

# ── HTML fragments ─────────────────────────────────────────────────────────────

STUDIO_NAV_HTML = """
<div class="st-nav">
  <button class="st-logo" id="st-logo-btn">PYDIA STUDIO&reg;</button>
  <button class="st-back" id="st-back-btn">&#8592; Back</button>
</div>
"""

VOICE_DROPDOWN_HTML = """
<div class="sl">Voice</div>
<div class="vd-wrap">
  <div class="vd-trigger" id="vd-trigger">
    <div class="vd-sel">
      <div class="vd-badge" id="vd-badge">RY</div>
      <div>
        <div class="vd-name" id="vd-name">Ryan</div>
        <div class="vd-gender" id="vd-gender">Male &middot; Energetic</div>
      </div>
    </div>
    <span class="vd-arr">&#9660;</span>
  </div>
  <div class="vd-menu" id="vd-menu">
    <div class="vd-hdr">Male</div>
    <div class="vd-item active" data-v="Ryan"   data-g="m" data-d="Energetic"><div class="vd-ibadge m">RY</div><span class="vd-iname">Ryan</span><span class="vd-itag">Energetic</span><div class="vd-dot"></div></div>
    <div class="vd-item"        data-v="Brian"  data-g="m" data-d="Deep">    <div class="vd-ibadge m">BR</div><span class="vd-iname">Brian</span><span class="vd-itag">Deep</span></div>
    <div class="vd-item"        data-v="Thomas" data-g="m" data-d="Clear">   <div class="vd-ibadge m">TH</div><span class="vd-iname">Thomas</span><span class="vd-itag">Clear</span></div>
    <div class="vd-item"        data-v="George" data-g="m" data-d="Warm">    <div class="vd-ibadge m">GE</div><span class="vd-iname">George</span><span class="vd-itag">Warm</span></div>
    <div class="vd-hdr">Female</div>
    <div class="vd-item"        data-v="Vivian" data-g="f" data-d="Bright">  <div class="vd-ibadge f">VI</div><span class="vd-iname">Vivian</span><span class="vd-itag">Bright</span></div>
    <div class="vd-item"        data-v="Serena" data-g="f" data-d="Smooth">  <div class="vd-ibadge f">SE</div><span class="vd-iname">Serena</span><span class="vd-itag">Smooth</span></div>
    <div class="vd-item"        data-v="Claire" data-g="f" data-d="Crisp">   <div class="vd-ibadge f">CL</div><span class="vd-iname">Claire</span><span class="vd-itag">Crisp</span></div>
    <div class="vd-item"        data-v="Nova"   data-g="f" data-d="Bold">    <div class="vd-ibadge f">NO</div><span class="vd-iname">Nova</span><span class="vd-itag">Bold</span></div>
    <div class="vd-item"        data-v="Luna"   data-g="f" data-d="Soft">    <div class="vd-ibadge f">LU</div><span class="vd-iname">Luna</span><span class="vd-itag">Soft</span></div>
  </div>
</div>
"""

OUTPUT_RULE_HTML = """
<div class="out-rule">
  <div class="orl"></div><div class="ort">OUTPUT</div><div class="orlr"></div>
</div>
"""

# ── The entire landing page + all JS injected into document.body ───────────────
# This bypasses Gradio's DOM entirely. Nothing here is inside a Gradio component.

BODY_INJECT = """
<script>
(function(){

// ── 1. Inject landing page HTML directly into document.body ──────────────────
var landing = document.createElement('div');
landing.id = 'pydia-landing';
landing.innerHTML = `
  <style>
    #pydia-landing {
      position: fixed; inset: 0; z-index: 99999;
      background: linear-gradient(135deg,#0f172a 0%,#1e293b 50%,#0f172a 100%);
      overflow: hidden;
      transition: opacity .5s ease, transform .5s ease;
    }
    #pydia-landing.hidden {
      opacity: 0; transform: translateY(-20px); pointer-events: none;
    }
    .lp-blob {
      position:absolute;border-radius:50%;
      filter:blur(80px);mix-blend-mode:screen;pointer-events:none;
      animation:lpB 10s ease-in-out infinite;
    }
    @keyframes lpB {
      0%,100%{transform:translate(0,0) scale(1);}
      33%{transform:translate(30px,-50px) scale(1.1);}
      66%{transform:translate(-20px,20px) scale(0.9);}
    }
    #pydia-landing .lp-b1{width:384px;height:384px;top:0;left:0;
      background:linear-gradient(135deg,rgba(59,130,246,.3),rgba(6,182,212,.2));}
    #pydia-landing .lp-b2{width:384px;height:384px;top:0;right:0;
      background:linear-gradient(135deg,rgba(168,85,247,.3),rgba(236,72,153,.2));animation-delay:2s;}
    #pydia-landing .lp-b3{width:384px;height:384px;bottom:0;left:50%;
      background:linear-gradient(135deg,rgba(6,182,212,.3),rgba(59,130,246,.2));animation-delay:4s;}
    .lp-grid{position:absolute;inset:0;pointer-events:none;opacity:.15;
      background-image:linear-gradient(rgba(100,150,255,.08) 1px,transparent 1px),
        linear-gradient(90deg,rgba(100,150,255,.08) 1px,transparent 1px);
      background-size:50px 50px;}
    .lp-overlay{position:absolute;inset:0;pointer-events:none;
      background:linear-gradient(to top,rgba(15,23,42,.7),transparent);}
    .lp-streak{position:absolute;left:0;width:100%;pointer-events:none;
      animation:lpStr 8s linear infinite;}
    .lp-s1{top:0;height:2px;background:linear-gradient(90deg,transparent,#14b8a6,transparent);}
    .lp-s2{top:33%;height:1px;background:linear-gradient(90deg,transparent,rgba(6,182,212,.5),transparent);animation-delay:2s;animation-duration:10s;opacity:.6;}
    .lp-s3{top:67%;height:1px;background:linear-gradient(90deg,transparent,rgba(20,184,166,.3),transparent);animation-delay:5s;animation-duration:12s;opacity:.4;}
    @keyframes lpStr{0%{transform:translateX(-100%);opacity:0;}50%{opacity:1;}100%{transform:translateX(100%);opacity:0;}}
    .lp-nav{
      position:absolute;top:0;left:0;right:0;z-index:10;
      background:rgba(255,255,255,.97);border-bottom:1px solid rgba(229,231,235,.5);
      display:flex;align-items:center;justify-content:space-between;padding:16px 48px;
    }
    .lp-nav-logo{font-size:1.1rem;font-weight:700;color:#111;background:none;border:none;
      cursor:pointer;letter-spacing:.03em;transition:opacity .2s;}
    .lp-nav-logo:hover{opacity:.65;}
    .lp-nav-links{display:flex;align-items:center;gap:28px;}
    .lp-nav-link{font-size:.875rem;color:#374151;font-weight:500;background:none;
      border:none;cursor:pointer;transition:color .2s;font-family:inherit;}
    .lp-nav-link:hover{color:#111;}
    .lp-cta{padding:10px 20px;background:#0d9488;color:#fff;border:none;border-radius:999px;
      font-size:.875rem;font-weight:700;cursor:pointer;transition:all .2s;}
    .lp-cta:hover{background:#0f766e;transform:scale(1.05);}
    .lp-body{position:relative;z-index:1;height:100vh;display:flex;align-items:center;padding-top:64px;}
    .lp-inner{width:100%;max-width:1280px;margin:0 auto;padding:0 48px;
      display:grid;grid-template-columns:1fr 1fr;gap:64px;align-items:center;}
    .lp-left{display:flex;flex-direction:column;justify-content:center;}
    .lp-hero-btn{
      display:inline-flex;align-items:center;gap:8px;padding:16px 32px;
      background:linear-gradient(90deg,#0d9488,#0891b2);border:none;border-radius:999px;
      color:#fff;font-weight:700;font-size:1rem;cursor:pointer;width:fit-content;
      box-shadow:0 10px 40px rgba(20,184,166,.5);transition:all .3s;
      animation:lpFade .8s ease-out, btnG 3s ease-in-out 1s infinite;
    }
    .lp-hero-btn:hover{transform:scale(1.1);box-shadow:0 16px 48px rgba(20,184,166,.8);}
    @keyframes lpFade{from{opacity:0;transform:translateY(40px);}to{opacity:1;transform:translateY(0);}}
    @keyframes btnG{0%,100%{box-shadow:0 10px 40px rgba(20,184,166,.5);}50%{box-shadow:0 10px 60px rgba(20,184,166,.8);}}
    .lp-right{display:flex;flex-direction:column;align-items:flex-end;gap:24px;
      animation:lpFade .8s ease-out .2s backwards;}
    .lp-icons{display:flex;gap:12px;padding:16px;
      background:rgba(255,255,255,.1);backdrop-filter:blur(8px);
      border:1px solid rgba(255,255,255,.2);border-radius:16px;
      animation:lpFloat 3s ease-in-out .3s infinite;}
    @keyframes lpFloat{0%,100%{transform:translateY(0);}50%{transform:translateY(-10px);}}
    .lp-icon{width:44px;height:44px;border:1px solid rgba(255,255,255,.3);border-radius:50%;
      background:none;display:flex;align-items:center;justify-content:center;
      color:#fff;cursor:default;font-size:.85rem;font-weight:600;transition:all .3s;}
    .lp-icon:hover{background:rgba(255,255,255,.2);border-color:rgba(255,255,255,.5);transform:scale(1.25) rotate(6deg);}
    .lp-card{background:linear-gradient(135deg,rgba(71,85,105,.6),rgba(51,65,85,.4));
      backdrop-filter:blur(8px);border:1px solid rgba(255,255,255,.2);border-radius:12px;
      padding:24px;width:220px;text-align:center;transition:all .3s;
      animation:lpFloat 4s ease-in-out .6s infinite;}
    .lp-card:hover{transform:scale(1.05);box-shadow:0 20px 60px rgba(20,184,166,.3);border-color:rgba(20,184,166,.5);}
    .lp-note{font-size:3rem;margin-bottom:12px;animation:noteP 2s ease-in-out infinite;}
    @keyframes noteP{0%,100%{transform:scale(1);opacity:1;}50%{transform:scale(1.1);opacity:.8;}}
    .lp-card-label{font-size:.875rem;font-weight:700;color:#fff;letter-spacing:.05em;}
    @media(max-width:768px){
      .lp-inner{grid-template-columns:1fr;}
      .lp-right{display:none;}
      .lp-nav{padding:14px 20px;}
    }
  </style>

  <div class="lp-blob lp-b1"></div>
  <div class="lp-blob lp-b2"></div>
  <div class="lp-blob lp-b3"></div>
  <div class="lp-grid"></div>
  <div class="lp-overlay"></div>
  <div class="lp-streak lp-s1"></div>
  <div class="lp-streak lp-s2"></div>
  <div class="lp-streak lp-s3"></div>

  <nav class="lp-nav">
    <button class="lp-nav-logo" id="lp-logo">PYDIA STUDIO&reg;</button>
    <div class="lp-nav-links">
      <button class="lp-nav-link">Home</button>
      <button class="lp-nav-link">About</button>
      <button class="lp-nav-link">Projects</button>
      <button class="lp-nav-link">Contact</button>
      <button class="lp-cta" id="lp-nav-cta">Get started</button>
    </div>
  </nav>

  <div class="lp-body">
    <div class="lp-inner">
      <div class="lp-left">
        <button class="lp-hero-btn" id="lp-hero-btn">
          Get started <span style="font-size:1.25rem">&#8599;</span>
        </button>
      </div>
      <div class="lp-right">
        <div class="lp-icons">
          <div class="lp-icon">IG</div>
          <div class="lp-icon">&#9835;</div>
          <div class="lp-icon">in</div>
        </div>
        <div class="lp-card">
          <div class="lp-note">&#9836;</div>
          <div class="lp-card-label">PYDIA STUDIO</div>
        </div>
      </div>
    </div>
  </div>
`;

document.body.appendChild(landing);

// ── 2. Page switching ────────────────────────────────────────────────────────
function goStudio() {
  document.getElementById('pydia-landing').classList.add('hidden');
  // after transition remove so studio is fully interactive
  setTimeout(function(){
    document.getElementById('pydia-landing').style.display = 'none';
  }, 520);
}

function goLanding() {
  var lp = document.getElementById('pydia-landing');
  lp.style.display = '';
  setTimeout(function(){ lp.classList.remove('hidden'); }, 10);
}

['lp-hero-btn','lp-nav-cta'].forEach(function(id){
  document.getElementById(id).addEventListener('click', goStudio);
});

// ── 3. Wire studio back buttons (retry until Gradio renders them) ─────────────
function wireBack() {
  var back = document.getElementById('st-back-btn');
  var logo = document.getElementById('st-logo-btn');
  if (!back) { setTimeout(wireBack, 300); return; }
  back.addEventListener('click', goLanding);
  if (logo) logo.addEventListener('click', goLanding);
}
wireBack();

// ── 4. Voice dropdown ────────────────────────────────────────────────────────
function wireVoice() {
  var trigger = document.getElementById('vd-trigger');
  var menu    = document.getElementById('vd-menu');
  var badge   = document.getElementById('vd-badge');
  var nameEl  = document.getElementById('vd-name');
  var genEl   = document.getElementById('vd-gender');
  if (!trigger || !menu) { setTimeout(wireVoice, 300); return; }

  trigger.addEventListener('click', function(e){
    e.stopPropagation();
    var open = menu.classList.toggle('open');
    trigger.classList.toggle('open', open);
  });
  document.addEventListener('click', function(){
    menu.classList.remove('open');
    trigger.classList.remove('open');
  });
  menu.addEventListener('click',function(e){e.stopPropagation();});

  menu.querySelectorAll('.vd-item').forEach(function(item){
    item.addEventListener('click', function(){
      var v = item.dataset.v, g = item.dataset.g, d = item.dataset.d;
      badge.textContent = v.slice(0,2).toUpperCase();
      badge.style.background = g==='m'
        ? 'linear-gradient(135deg,#1d4ed8,#0891b2)'
        : 'linear-gradient(135deg,#9333ea,#ec4899)';
      nameEl.textContent = v;
      genEl.textContent  = (g==='m'?'Male':'Female')+' \u00b7 '+d;

      menu.querySelectorAll('.vd-item').forEach(function(i){
        i.classList.remove('active');
        var dot = i.querySelector('.vd-dot');
        if(dot) dot.remove();
      });
      item.classList.add('active');
      var dot = document.createElement('div');
      dot.className = 'vd-dot';
      item.appendChild(dot);

      // sync hidden Gradio textarea
      var wrap = document.getElementById('speaker-hidden');
      if(wrap){
        var tb = wrap.querySelector('textarea')||wrap.querySelector('input');
        if(tb){
          tb.value = v;
          tb.dispatchEvent(new Event('input',{bubbles:true}));
          tb.dispatchEvent(new Event('change',{bubbles:true}));
        }
      }
      menu.classList.remove('open');
      trigger.classList.remove('open');
    });
  });
}
wireVoice();

})();
</script>
"""


# ── Gradio UI ──────────────────────────────────────────────────────────────────

with gr.Blocks(title="PYDIA STUDIO", css=CSS, theme=gr.themes.Base()) as demo:

    # Studio page (visible from the start under the landing overlay)
    with gr.Column(elem_id="ps-studio"):

        gr.HTML(STUDIO_NAV_HTML)

        with gr.Row(elem_classes=["st-body"]):

            with gr.Column(scale=1, min_width=280):

                gr.HTML(VOICE_DROPDOWN_HTML)

                speaker_input = gr.Textbox(
                    value="Ryan", visible=False, elem_id="speaker-hidden",
                )

                gr.HTML('<div class="sl" style="margin-top:18px">Delivery Style</div>')
                instruct_input = gr.Textbox(
                    value="Fast-talking sarcastic infomercial host, excited and breathless, comedic timing",
                    label="", lines=3,
                    placeholder="Describe how the voice should sound...",
                )

                gr.HTML('<hr class="sd"/>')
                gr.HTML('<div class="sl">Source</div>')

                with gr.Tabs():
                    with gr.Tab("Wikipedia"):
                        wiki_url = gr.Textbox(label="URL",
                            placeholder="https://en.wikipedia.org/wiki/Nikola_Tesla", lines=1)
                        wiki_btn = gr.Button("GENERATE PITCH", variant="primary")
                        gr.Examples(
                            examples=[
                                ["https://en.wikipedia.org/wiki/Nikola_Tesla"],
                                ["https://en.wikipedia.org/wiki/Serena_Williams"],
                                ["https://en.wikipedia.org/wiki/Steve_Jobs"],
                            ],
                            inputs=wiki_url, label="Examples",
                        )

                    with gr.Tab("GitHub"):
                        gh_username = gr.Textbox(label="Username",
                            placeholder="spirizeon", lines=1)
                        github_btn = gr.Button("GENERATE PITCH", variant="primary")
                        gr.Examples(
                            examples=[["spirizeon"], ["Nithish-Sri-Ram"], ["lviffy"]],
                            inputs=gh_username, label="Examples",
                        )

            with gr.Column(scale=2):

                gr.HTML(OUTPUT_RULE_HTML)

                gr.HTML('<div class="sl">Pipeline</div>')
                status_box = gr.Markdown(value="_Waiting for input..._")

                gr.HTML('<hr class="sd"/>')
                gr.HTML('<div class="sl">Script</div>')
                pitch_output = gr.Textbox(label="", lines=6, interactive=False,
                    placeholder="Generated pitch will appear here...")

                gr.HTML('<hr class="sd"/>')
                gr.HTML('<div class="sl">Media</div>')
                with gr.Row(equal_height=True):
                    audio_output = gr.Audio(label="Audio", type="filepath")
                    video_output = gr.Video(label="Video")

    # Inject landing + all JS into document.body — runs after Gradio renders
    gr.HTML(BODY_INJECT)

    wiki_btn.click(
        fn=run_wikipedia,
        inputs=[wiki_url, speaker_input, instruct_input],
        outputs=[status_box, pitch_output, audio_output, video_output],
    )
    github_btn.click(
        fn=run_github,
        inputs=[gh_username, speaker_input, instruct_input],
        outputs=[status_box, pitch_output, audio_output, video_output],
    )


if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    demo.launch(share=True, show_error=True)
