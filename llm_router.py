from dataclasses import dataclass
from typing import List, Dict, Optional
import re, json

@dataclass
class ProviderConfig:
    name: str
    api_key: str
    model: Optional[str] = None

def _prompt_outline(text: str, guidance: Optional[str], max_slides: int) -> str:
    guide = guidance or "Create a concise professional slide deck."
    return f"""You are a presentation planner. Read the input and propose a slide outline.

GUIDANCE: {guide}
MAX_SLIDES: {max_slides}

Return JSON with this shape:
[{{"title": "...","bullets":["...","..."]}}, ...]

INPUT:
{text[:15000]}
"""

def _safe_parse_json(s: str):
    try:
        return json.loads(s)
    except json.JSONDecodeError:
        m = re.search(r'(\[.*\])', s, flags=re.S)
        if m:
            return json.loads(m.group(1))
        raise

def make_outline_with_llm(text: str, guidance: Optional[str], cfg: ProviderConfig, max_slides: int=12) -> List[Dict]:
    prompt = _prompt_outline(text, guidance, max_slides)
    name = (cfg.name or "").lower()
    if "openai" in name:
        # Requires: pip install openai
        from openai import OpenAI
        client = OpenAI(api_key=cfg.api_key)
        model = cfg.model or "gpt-4o-mini"
        resp = client.chat.completions.create(model=model, messages=[{"role":"user","content":prompt}], temperature=0.2)
        content = resp.choices[0].message.content
        return _safe_parse_json(content)
    if "anthropic" in name:
        # Requires: pip install anthropic
        import anthropic
        client = anthropic.Anthropic(api_key=cfg.api_key)
        model = cfg.model or "claude-3-5-sonnet-latest"
        msg = client.messages.create(model=model, max_tokens=2000, temperature=0.2,
                                     messages=[{"role":"user","content":prompt}])
        content = "".join([b.text for b in msg.content if getattr(b, 'type', None)=="text"])
        return _safe_parse_json(content)
    if "gemini" in name or "google" in name:
        # Requires: pip install google-generativeai
        import google.generativeai as genai
        genai.configure(api_key=cfg.api_key)
        model = genai.GenerativeModel(cfg.model or "gemini-1.5-pro")
        resp = model.generate_content(prompt)
        content = resp.text
        return _safe_parse_json(content)
    raise ValueError("Unsupported provider name. Choose OpenAI, Anthropic, or Gemini.")
