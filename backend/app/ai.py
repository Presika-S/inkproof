"""AI layer. The model only PROPOSES findings. Every proposal is re-checked by
engine.verify() in the route, so an invented rule, fact or quote is dropped."""
import json
import re

from .config import settings


class AIUnavailable(Exception):
    pass


SYSTEM = (
    "You review brand copy against approved rules and facts. "
    "Reply with ONLY a JSON array of objects with keys rule_id, fact_id (or null), quote, reason. "
    "Use only the rule and fact ids provided. quote must be an exact substring of the draft. "
    "Do not invent rules or facts. Return [] if nothing is wrong."
)


def propose(text: str, rules: list[dict], facts: list[dict]) -> list[dict]:
    if not settings.anthropic_api_key:
        raise AIUnavailable("AI review is not configured on the server. Rule-based review still works.")
    import anthropic  # imported lazily so the app runs without the key

    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    payload = {
        "rules": [{"id": r["id"], "name": r["name"]} for r in rules],
        "facts": [{"id": f["id"], "text": f["text"], "valid_until": f["valid_until"]} for f in facts],
    }
    try:
        msg = client.messages.create(
            model=settings.ai_model,
            max_tokens=1000,
            system=SYSTEM,
            messages=[{"role": "user", "content": f"{json.dumps(payload)}\n\nDRAFT:\n{text}"}],
        )
        raw = "".join(b.text for b in msg.content if getattr(b, "type", "") == "text")
    except Exception as e:  # network, quota, bad key
        raise AIUnavailable(f"AI call failed ({type(e).__name__}). Rule-based review still works.")
    match = re.search(r"\[.*\]", raw, re.S)
    if not match:
        return []
    try:
        data = json.loads(match.group(0))
    except json.JSONDecodeError:
        return []
    return [d for d in data if isinstance(d, dict)]
