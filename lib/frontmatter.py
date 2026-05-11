"""
Minimal YAML frontmatter parser for engram memory files.

Handles the --- delimited frontmatter block at the top of markdown files.
Stdlib only — no PyYAML dependency.

Supported value types: strings, numbers, booleans, simple lists (inline [a, b]).

Usage:
    from frontmatter import parse_frontmatter, strip_frontmatter
    from frontmatter import render_frontmatter, update_frontmatter

    meta = parse_frontmatter(content)        # {} if no frontmatter
    body = strip_frontmatter(content)        # content without frontmatter
    header = render_frontmatter(meta)        # "---\\nkey: val\\n---\\n"
    new_content = update_frontmatter(content, {"confidence": "high"})
"""

import re


_FM_RE = re.compile(r'\A---[ \t]*\n(.*?\n)---[ \t]*\n', re.DOTALL)


def parse_frontmatter(content: str) -> dict:
    """Parse YAML frontmatter from content. Returns {} if none found."""
    m = _FM_RE.match(content)
    if not m:
        return {}
    return _parse_yaml_block(m.group(1))


def strip_frontmatter(content: str) -> str:
    """Return content with frontmatter removed."""
    m = _FM_RE.match(content)
    if not m:
        return content
    return content[m.end():]


def render_frontmatter(meta: dict) -> str:
    """Render a dict as a YAML frontmatter block (--- delimited).

    Note: 'yes'/'no' strings round-trip as booleans (YAML 1.1 convention).
    Quote them if you need literal strings: \"'yes'\", \"'no'\".
    """
    if not meta:
        return ""
    lines = ["---"]
    for key, value in meta.items():
        if value is None:
            continue
        lines.append(f"{key}: {_format_value(value)}")
    lines.append("---\n")
    return "\n".join(lines)


def update_frontmatter(content: str, updates: dict) -> str:
    """Update or add frontmatter fields. Preserves body text."""
    existing = parse_frontmatter(content)
    body = strip_frontmatter(content)
    merged = {**existing, **updates}
    # Remove keys set to None
    merged = {k: v for k, v in merged.items() if v is not None}
    if not merged:
        return body
    return render_frontmatter(merged) + body


def _parse_yaml_block(block: str) -> dict:
    """Parse simple YAML key: value lines."""
    result = {}
    for line in block.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            continue
        key, _, raw = line.partition(":")
        key = key.strip()
        raw = raw.strip()
        if not key:
            continue
        result[key] = _parse_value(raw)
    return result


def _parse_value(raw: str):
    """Parse a simple YAML value (string, number, bool, list)."""
    if not raw:
        return ""
    # Boolean
    if raw.lower() in ("true", "yes"):
        return True
    if raw.lower() in ("false", "no"):
        return False
    # Inline list: [a, b, c]
    if raw.startswith("[") and raw.endswith("]"):
        items = raw[1:-1].split(",")
        return [_parse_scalar(i.strip()) for i in items if i.strip()]
    # Numeric
    return _parse_scalar(raw)


def _parse_scalar(raw: str):
    """Parse a scalar: int, float, or string."""
    # Strip quotes
    if len(raw) >= 2 and raw[0] == raw[-1] and raw[0] in ('"', "'"):
        return raw[1:-1]
    # Int
    try:
        return int(raw)
    except ValueError:
        pass
    # Float
    try:
        return float(raw)
    except ValueError:
        pass
    return raw


def _format_value(value) -> str:
    """Format a Python value as YAML."""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, list):
        items = ", ".join(str(v) for v in value)
        return f"[{items}]"
    return str(value)
