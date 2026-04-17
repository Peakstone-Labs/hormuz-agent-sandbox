"""Load souls (actor configs) and tags (scenario modifiers) from markdown files."""

import re
from pathlib import Path

import yaml

BASE_DIR = Path(__file__).parent
SOULS_DIR = BASE_DIR / "souls"
TAGS_DIR = BASE_DIR / "tags"

# Regex to split YAML frontmatter from markdown body
_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n(.*)$", re.DOTALL)

SUPPORTED_LOCALES = ("en", "zh")


def _parse_md(path: Path) -> tuple[dict, str]:
    """Parse a markdown file with YAML frontmatter. Returns (meta, body)."""
    text = path.read_text(encoding="utf-8")
    m = _FRONTMATTER_RE.match(text)
    if not m:
        raise ValueError(f"No valid frontmatter in {path}")
    meta = yaml.safe_load(m.group(1))
    body = m.group(2).strip()
    return meta, body


def load_souls() -> dict[str, dict]:
    """Load all actor soul files."""
    actors = {}
    for path in sorted(SOULS_DIR.glob("*.md")):
        meta, body = _parse_md(path)
        actor_id = meta["id"]
        actors[actor_id] = {
            "display_name": meta["display_name"],
            "emoji": meta.get("emoji", ""),
            "i18n": meta.get("i18n", {}),
            "default_profile": meta["default_profile"],
            "system_prompt": body,  # Always English — for LLM consumption
            "source_file": path.name,
        }
    return actors


def load_tags() -> dict[str, dict]:
    """Load all tag files."""
    tags = {}
    for path in sorted(TAGS_DIR.glob("*.md")):
        meta, body = _parse_md(path)
        tag_id = meta["id"]
        tags[tag_id] = {
            "name": meta["name"],
            "emoji": meta.get("emoji", ""),
            "category": meta.get("category", "misc"),
            "description": meta["description"],
            "i18n": meta.get("i18n", {}),
            "affects": meta.get("affects", []),
            "injection_text": body,  # Always English — for LLM consumption
            "source_file": path.name,
        }
    return tags


def localize_actor(actor: dict, locale: str = "en") -> dict:
    """Return frontend-safe actor dict with localized display fields."""
    i18n = actor.get("i18n", {}).get(locale, {})
    return {
        "display_name": i18n.get("display_name", actor["display_name"]),
        "short_name": i18n.get("short_name", actor["display_name"].split("(")[0].strip()),
        "description": i18n.get("description", ""),
        "emoji": actor["emoji"],
        "default_profile": actor["default_profile"],
        "red_lines": i18n.get("red_lines", actor["default_profile"].get("red_lines", [])),
        "constraints_labels": i18n.get("constraints_labels", {}),
    }


def localize_tag(tag: dict, locale: str = "en") -> dict:
    """Return frontend-safe tag dict with localized display fields."""
    i18n = tag.get("i18n", {}).get(locale, {})
    return {
        "name": i18n.get("name", tag["name"]),
        "description": i18n.get("description", tag["description"]),
        "emoji": tag["emoji"],
        "category": tag["category"],
    }


def get_tag_injection(tags: dict[str, dict], active_tag_ids: list[str], actor_id: str) -> str:
    """Build the combined tag injection text for a specific actor."""
    parts = []
    for tag_id in active_tag_ids:
        tag = tags.get(tag_id)
        if not tag:
            continue
        if not tag["affects"] or actor_id in tag["affects"]:
            parts.append(f"### Active Modifier: {tag['emoji']} {tag['name']}\n{tag['injection_text']}")
    return "\n\n".join(parts)


def get_market_tag_injection(tags: dict[str, dict], active_tag_ids: list[str]) -> str:
    """Build tag injection for the Market agent (always receives all active tags)."""
    parts = []
    for tag_id in active_tag_ids:
        tag = tags.get(tag_id)
        if not tag:
            continue
        parts.append(f"### Active Modifier: {tag['emoji']} {tag['name']}\n{tag['injection_text']}")
    return "\n\n".join(parts)
