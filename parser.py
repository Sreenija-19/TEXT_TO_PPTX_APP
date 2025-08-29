# parser.py
from typing import List, Dict, Optional
import re
import textwrap

def _split_markdown_sections(md: str) -> List[Dict]:
    # Split by headings if present
    sections = []
    lines = md.splitlines()
    current = {"title": None, "content": []}
    for line in lines:
        m = re.match(r'^(#{1,6})\s+(.*)', line.strip())
        if m:
            if current["title"] or current["content"]:
                sections.append({"title": current["title"] or "Section", "content": "\n".join(current["content"]).strip()})
            current = {"title": m.group(2).strip(), "content": []}
        else:
            current["content"].append(line)
    if current["title"] or current["content"]:
        sections.append({"title": current["title"] or "Section", "content": "\n".join(current["content"]).strip()})
    return [s for s in sections if (s["title"] or s["content"])]

def heuristic_outline(text: str, max_slides: int = 12) -> List[Dict]:
    # If markdown headings exist, use them; else chunk by paragraphs/sentences
    sections = _split_markdown_sections(text)
    if not sections:
        paragraphs = [p.strip() for p in re.split(r'\n\s*\n', text) if p.strip()]
        for p in paragraphs:
            title = p.split('.')[0][:80]
            sections.append({"title": title or "Topic", "content": p})
    # Cap slides
    if len(sections) > max_slides:
        merged = []
        bucket = []
        for s in sections:
            bucket.append(s)
            if len(bucket) >= max(1, len(sections)//max_slides):
                title = bucket[0]["title"]
                content = "\n\n".join(x["content"] for x in bucket)
                merged.append({"title": title, "content": content})
                bucket = []
        if bucket:
            title = bucket[0]["title"]
            content = "\n\n".join(x["content"] for x in bucket)
            merged.append({"title": title, "content": content})
        sections = merged[:max_slides]
    # Create bullets
    outline = []
    for sec in sections[:max_slides]:
        bullets = re.split(r'[\n•\-]\s+', sec["content"])
        bullets = [b.strip() for b in bullets if b.strip()]
        bullets = [b if len(b) <= 240 else textwrap.shorten(b, width=240, placeholder='…') for b in bullets[:8]]
        outline.append({"title": sec["title"][:90], "bullets": bullets})
    return outline

def outline_from_text(text: str, guidance: Optional[str]=None, max_slides: int=12) -> List[Dict]:
    # Try to use headings; if content is clearly structured, prefer that
    secs = _split_markdown_sections(text)
    if secs:
        outline = []
        for s in secs[:max_slides]:
            bullets = [ln.strip(" -•") for ln in s["content"].splitlines() if ln.strip()]
            bullets = [b for b in bullets if len(b) > 0][:8]
            outline.append({"title": s["title"][:90], "bullets": bullets})
        return outline
    return heuristic_outline(text, max_slides=max_slides)

