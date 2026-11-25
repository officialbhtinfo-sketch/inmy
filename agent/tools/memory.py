"""Simple persistent JSON memory. No dependencies, works offline."""
import json
import os
import re
import time

MEMORY_FILE = os.path.join(os.path.dirname(__file__), "..", "memories.json")


def _load() -> dict:
    if not os.path.exists(MEMORY_FILE):
        return {}
    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _save(data: dict) -> None:
    tmp = MEMORY_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    os.replace(tmp, MEMORY_FILE)


def _tokens(text: str) -> set:
    return set(re.findall(r"[a-z0-9]+", text.lower()))


def memory_save(key: str, text: str, tags=None) -> str:
    if not key or not text:
        return "memory_save needs both 'key' and 'text'."
    data = _load()
    data[key] = {
        "text": text,
        "tags": tags or [],
        "updated": time.strftime("%Y-%m-%d %H:%M"),
    }
    _save(data)
    return f"Saved memory '{key}'."


def memory_search(query: str, limit: int = 5) -> str:
    data = _load()
    if not data:
        return "Memory is empty. Nothing saved yet."
    q = _tokens(query)
    if not q:
        return "Memory is empty. Nothing saved yet."
    scored = []
    for key, mem in data.items():
        m = _tokens(mem["text"] + " " + " ".join(mem.get("tags", [])))
        overlap = len(q & m)
        score = overlap / ((len(m) ** 0.5) * (len(q) ** 0.5) + 0.01)
        if overlap > 0:
            scored.append((score, key, mem["text"]))
    scored.sort(reverse=True)
    results = scored[:limit]
    if not results:
        return "No relevant memories found."
    lines = []
    for score, key, text in results:
        lines.append(f"- [{key}] {text}")
    return "\n".join(lines)


def memory_list() -> str:
    data = _load()
    if not data:
        return "Memory is empty. Nothing saved yet."
    lines = []
    for key, mem in data.items():
        lines.append(f"- {key}: {mem['text']} (tags: {', '.join(mem.get('tags', []))}, updated: {mem['updated']})")
    return "\n".join(lines)