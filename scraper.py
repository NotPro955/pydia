"""
Phase 1: Scrape Wikipedia and chunk text into RAG-ready segments.
"""

import re
import requests
from bs4 import BeautifulSoup


# Sections to skip — not useful for a sales pitch
SKIP_SECTIONS = {
    "references", "external links", "further reading", "notes",
    "see also", "bibliography", "footnotes", "sources", "citations"
}


def scrape_wikipedia(url: str) -> dict:
    """Scrape a Wikipedia page and return structured sections."""
    headers = {"User-Agent": "WikiRAGPitch/1.0 (educational project)"}
    resp = requests.get(url, headers=headers, timeout=10)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")

    # Extract person name from title
    title_tag = soup.find("h1", {"id": "firstHeading"})
    person_name = title_tag.get_text(strip=True) if title_tag else "Unknown"

    # Get the main content div
    content_div = soup.find("div", {"id": "mw-content-text"})
    if not content_div:
        raise ValueError("Could not find Wikipedia content — is this a valid Wikipedia URL?")

    sections = {}

    # --- Intro paragraph (before first h2) ---
    intro_paras = []
    for elem in content_div.find("div", {"class": "mw-parser-output"}).children:
        if elem.name == "h2":
            break
        if elem.name == "p":
            text = elem.get_text(strip=True)
            # Remove citation brackets like [1], [2]
            text = re.sub(r"\[\d+\]", "", text).strip()
            if text:
                intro_paras.append(text)

    if intro_paras:
        sections["Introduction"] = " ".join(intro_paras)

    # --- All h2 sections ---
    current_section = None
    current_text = []

    for elem in content_div.find_all(["h2", "h3", "p"]):
        if elem.name in ("h2", "h3"):
            # Save previous section
            if current_section and current_text:
                combined = " ".join(current_text).strip()
                if combined:
                    sections[current_section] = combined
            raw_heading = elem.get_text(strip=True).lower().replace("[edit]", "").strip()
            current_section = raw_heading if raw_heading not in SKIP_SECTIONS else None
            current_text = []
        elif elem.name == "p" and current_section:
            text = elem.get_text(strip=True)
            text = re.sub(r"\[\d+\]", "", text).strip()
            if text:
                current_text.append(text)

    # Save last section
    if current_section and current_text:
        combined = " ".join(current_text).strip()
        if combined:
            sections[current_section] = combined

    return {"name": person_name, "url": url, "sections": sections}


def chunk_text(text: str, chunk_size: int = 200, overlap: int = 40) -> list[str]:
    """Split text into overlapping word-level chunks."""
    words = text.split()
    chunks = []
    start = 0
    while start < len(words):
        end = start + chunk_size
        chunk = " ".join(words[start:end])
        chunks.append(chunk)
        start += chunk_size - overlap
    return chunks


def scrape_and_chunk(url: str) -> tuple[str, list[dict]]:
    """
    Full Phase 1 pipeline.
    Returns (person_name, list of {text, section, chunk_id}).
    """
    data = scrape_wikipedia(url)
    person_name = data["name"]
    all_chunks = []

    for section, text in data["sections"].items():
        for i, chunk in enumerate(chunk_text(text)):
            all_chunks.append({
                "text": chunk,
                "section": section,
                "chunk_id": f"{section}_{i}"
            })

    print(f"[Scraper] '{person_name}' → {len(data['sections'])} sections → {len(all_chunks)} chunks")
    return person_name, all_chunks
