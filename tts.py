"""
TTS using Qwen3-TTS-12Hz-1.7B-CustomVoice.
Fixed for GTX 1080 (float16, sdpa, explicit cuda device_map).

Key fix: squeeze each chunk to 1D before concatenating.
generate_custom_voice returns shape (1, N) per chunk — different N per chunk
means np.concatenate fails on axis=1. Squeezing to (N,) then concatenating
on axis=0 works correctly.
"""

import os
import re
import torch
import numpy as np
import soundfile as sf
from qwen_tts import Qwen3TTSModel


MODEL_ID = "Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice"

DEFAULT_SPEAKER = "Ryan"

DEFAULT_INSTRUCT = (
    "Fast talking sarcastic infomercial host. "
    "Energetic delivery. Slightly breathless excitement. "
    "Punchy comedic timing."
)

_model = None


def _load_model():
    global _model
    if _model is not None:
        return _model

    print("[TTS] Loading Qwen3-TTS model onto GPU...")
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"[TTS] Device: {device}")

    _model = Qwen3TTSModel.from_pretrained(
        MODEL_ID,
        dtype=torch.float16 if device == "cuda" else torch.float32,
        device_map=device,
        attn_implementation="sdpa",
    )
    print("[TTS] Model loaded.")
    return _model


def _split_sentences(text: str):
    """Split on sentence boundaries, ~15 words per chunk."""
    raw = re.split(r"(?<=[.!?])\s+", text.strip())
    chunks, current = [], []
    for sentence in raw:
        current.append(sentence)
        if len(" ".join(current).split()) >= 15:
            chunks.append(" ".join(current))
            current = []
    if current:
        chunks.append(" ".join(current))
    return [c for c in chunks if c.strip()]


def text_to_speech(text: str, person_name: str, output_dir: str = "output") -> str:

    os.makedirs(output_dir, exist_ok=True)
    safe = "".join(c if c.isalnum() or c in "-_" else "_" for c in person_name)
    output_path = os.path.join(output_dir, f"{safe}_pitch.wav")

    speaker  = os.getenv("QWEN_TTS_SPEAKER",  DEFAULT_SPEAKER).strip()
    instruct = os.getenv("QWEN_TTS_INSTRUCT", DEFAULT_INSTRUCT).strip()

    try:
        model = _load_model()
        sentences = _split_sentences(text)
        print(f"[TTS] Generating {len(sentences)} chunk(s) — speaker: {speaker}")

        audio_parts = []
        sample_rate = None

        for i, chunk in enumerate(sentences):
            print(f"[TTS] Chunk {i+1}/{len(sentences)}: {chunk[:60]}...")

            wavs, sr = model.generate_custom_voice(
                text=chunk,
                language="English",
                speaker=speaker,
                instruct=instruct,
            )

            if sample_rate is None:
                sample_rate = sr

            # wavs may be shape (1, N) or (N,) depending on model version
            # squeeze to 1D (N,) so concatenation works regardless of chunk length
            arr = np.array(wavs, dtype=np.float32)
            arr = arr.squeeze()          # (1, N) → (N,)  or  (N,) → (N,)
            if arr.ndim == 0:            # edge case: single sample
                arr = arr.reshape(1)
            audio_parts.append(arr)
            print(f"[TTS] Chunk {i+1} shape: {arr.shape}")

        combined = np.concatenate(audio_parts, axis=0)
        print(f"[TTS] Combined shape: {combined.shape} — writing to {output_path}")
        sf.write(output_path, combined, sample_rate)
        print(f"[TTS] Saved → {output_path}")
        return output_path

    except Exception as e:
        print(f"[TTS] Qwen3-TTS failed: {e}")
        print("[TTS] Falling back to Kokoro / pyttsx3...")
        return _fallback(text, output_path)


# ── Fallback ───────────────────────────────────────────────────────────────────

_BASE_DIR  = os.path.dirname(os.path.abspath(__file__))
ONNX_MODEL = os.path.join(_BASE_DIR, "kokoro-v1.0.onnx")
VOICES_BIN = os.path.join(_BASE_DIR, "voices-v1.0.bin")


def _fallback(text: str, output_path: str) -> str:
    clean = re.sub(r"\[.*?\]", "", text).strip()
    clean = re.sub(r"\s+", " ", clean)

    if (os.path.exists(ONNX_MODEL) and os.path.exists(VOICES_BIN)
            and _try_import("kokoro_onnx")):
        from kokoro_onnx import Kokoro
        voice = os.getenv("KOKORO_VOICE", "af_heart").strip()
        kokoro = Kokoro(ONNX_MODEL, VOICES_BIN)
        samples, sr = kokoro.create(clean, voice=voice, speed=1.05, lang="en-us")
        sf.write(output_path, samples, sr)
        print(f"[TTS] Kokoro saved → {output_path}")
    else:
        import pyttsx3
        engine = pyttsx3.init()
        engine.setProperty("rate", 165)
        engine.setProperty("volume", 1.0)
        voices = engine.getProperty("voices")
        if voices:
            en = [v for v in voices if "en" in (v.languages[0] if v.languages else "")]
            engine.setProperty("voice", en[0].id if en else voices[0].id)
        engine.save_to_file(clean, output_path)
        engine.runAndWait()
        print(f"[TTS] pyttsx3 saved → {output_path}")

    return output_path


def _try_import(mod: str) -> bool:
    try:
        __import__(mod)
        return True
    except ImportError:
        return False
