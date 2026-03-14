"""
GitHub Adapter — Phase 1 (GitHub variant)

Runs AdvancedGitHubScraper and converts its rich output into the same
(person_name, chunks) format the rest of the pipeline expects.
No changes needed to vector_store.py, generator.py, or tts.py.
"""

import re
from github_scraper import AdvancedGitHubScraper
from scraper import chunk_text  # reuse the same chunker


def _clean(text: str) -> str:
    """Strip markdown symbols and collapse whitespace."""
    text = re.sub(r"[#*`_>\-]{2,}", " ", text)
    text = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", text)  # [label](url) → label
    text = re.sub(r"https?://\S+", "", text)                # remove bare URLs
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _profile_to_text(profile: dict) -> str:
    """Turn the profile dict into a readable paragraph."""
    parts = []
    if profile.get("name"):
        parts.append(f"{profile['name']} is a developer on GitHub (@{profile.get('username', '')}).")
    if profile.get("bio"):
        parts.append(_clean(profile["bio"]))
    if profile.get("company"):
        parts.append(f"They work at {profile['company']}.")
    if profile.get("location"):
        parts.append(f"Based in {profile['location']}.")
    if profile.get("followers"):
        parts.append(f"They have {profile['followers']:,} followers on GitHub.")
    if profile.get("hireable"):
        parts.append("They are open to hire.")
    return " ".join(parts)


def _stats_to_text(stats: dict, languages: dict) -> str:
    """Turn statistics into a readable paragraph."""
    parts = []
    if stats.get("total_stars"):
        parts.append(f"Their repositories have earned {stats['total_stars']:,} stars in total.")
    if stats.get("total_forks"):
        parts.append(f"Their work has been forked {stats['total_forks']:,} times.")
    if stats.get("most_starred_repo"):
        r = stats["most_starred_repo"]
        parts.append(f"Their most starred project is '{r['name']}' with {r['stars']:,} stars.")
    if languages:
        top_langs = list(languages.keys())[:5]
        parts.append(f"Top programming languages: {', '.join(top_langs)}.")
    return " ".join(parts)


def _repo_to_text(repo: dict) -> str:
    """Turn a single repo into a descriptive sentence or two."""
    parts = []
    name = repo.get("name", "")
    desc = _clean(repo.get("description") or "")
    stars = repo.get("stars", 0)
    lang = repo.get("language", "")
    topics = repo.get("topics", [])
    features = (repo.get("readme_extracted_info") or {}).get("features", [])

    if name:
        line = f"Project '{name}'"
        if desc:
            line += f": {desc}"
        if stars:
            line += f" ({stars:,} stars)"
        if lang:
            line += f", built in {lang}"
        parts.append(line + ".")
    if topics:
        parts.append(f"Topics: {', '.join(topics[:6])}.")
    for feat in features[:3]:
        cleaned = _clean(feat)
        if cleaned:
            parts.append(cleaned)
    return " ".join(parts)


def _readme_to_text(readme_data: dict) -> str:
    """Extract the most useful text from the profile README."""
    if not readme_data:
        return ""
    parts = []
    info = readme_data.get("extracted_info", {})

    skills = list(set(info.get("skills", [])))[:20]
    if skills:
        parts.append(f"Skills and technologies: {', '.join(skills)}.")

    for exp in info.get("work_experience", [])[:8]:
        cleaned = _clean(exp)
        if cleaned:
            parts.append(cleaned)

    # Also use raw README but trimmed to avoid noise
    raw = _clean(readme_data.get("content") or "")
    if raw:
        words = raw.split()[:300]  # cap at 300 words
        parts.append(" ".join(words))

    return " ".join(parts)


def scrape_github_and_chunk(username: str, token: str = None) -> tuple[str, list[dict]]:
    """
    Full Phase 1 (GitHub variant).
    Returns (person_name, list of {text, section, chunk_id}) — identical shape
    to scrape_and_chunk() in scraper.py.
    """
    scraper = AdvancedGitHubScraper(username, token=token or None)
    success = scraper.scrape_all(repo_limit=30)

    if not success:
        raise ValueError(f"GitHub user '{username}' not found or API rate limit hit.")

    data = scraper.data
    profile = data.get("profile", {})
    person_name = profile.get("name") or username

    # Build named sections → text
    sections = {}

    profile_text = _profile_to_text(profile)
    if profile_text:
        sections["Profile"] = profile_text

    stats_text = _stats_to_text(
        data.get("statistics", {}),
        data.get("languages", {})
    )
    if stats_text:
        sections["Statistics"] = stats_text

    readme_text = _readme_to_text(data.get("profile_readme", {}))
    if readme_text:
        sections["Profile README"] = readme_text

    # Top repos — each gets its own section so retrieval can target them
    for repo in data.get("top_repositories", [])[:10]:
        repo_text = _repo_to_text(repo)
        if repo_text:
            sections[f"repo_{repo['name']}"] = repo_text

    # Chunk everything (reuse same chunker as Wikipedia path)
    all_chunks = []
    for section, text in sections.items():
        for i, chunk in enumerate(chunk_text(text)):
            all_chunks.append({
                "text": chunk,
                "section": section,
                "chunk_id": f"{section}_{i}"
            })

    print(f"[GitHub] '{person_name}' → {len(sections)} sections → {len(all_chunks)} chunks")
    return person_name, all_chunks
