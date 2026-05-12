#!/usr/bin/env python3
"""Tests for lib/frontmatter.py — parse/render roundtrip, update, strip."""

import sys
from pathlib import Path

# Add lib/ to path
sys.path.insert(0, str(Path(__file__).parent.parent / "lib"))

from frontmatter import parse_frontmatter, strip_frontmatter, render_frontmatter, update_frontmatter


def test_parse_basic():
    """Parse basic frontmatter with string values."""
    content = "---\nconfidence: high\nurgency: active\n---\n# Body\n"
    meta = parse_frontmatter(content)
    assert meta == {"confidence": "high", "urgency": "active"}, f"Got: {meta}"
    print("  PASS: parse basic frontmatter")


def test_parse_types():
    """Parse different value types."""
    content = "---\ncount: 42\nrate: 3.14\nenabled: true\ntags: [jwt, oauth]\n---\nBody\n"
    meta = parse_frontmatter(content)
    assert meta["count"] == 42
    assert abs(meta["rate"] - 3.14) < 0.01
    assert meta["enabled"] is True
    assert meta["tags"] == ["jwt", "oauth"]
    print("  PASS: parse types (int, float, bool, list)")


def test_parse_no_frontmatter():
    """No frontmatter returns empty dict."""
    content = "# Just a heading\n\nSome text.\n"
    meta = parse_frontmatter(content)
    assert meta == {}, f"Expected empty dict, got: {meta}"
    print("  PASS: no frontmatter returns {}")


def test_strip_frontmatter():
    """Strip removes frontmatter, keeps body."""
    content = "---\nkey: val\n---\n# Body\nText here.\n"
    body = strip_frontmatter(content)
    assert body == "# Body\nText here.\n", f"Got: {repr(body)}"
    print("  PASS: strip frontmatter")


def test_strip_no_frontmatter():
    """Strip on content without frontmatter returns unchanged."""
    content = "# No frontmatter\nJust text.\n"
    body = strip_frontmatter(content)
    assert body == content
    print("  PASS: strip without frontmatter is identity")


def test_render_frontmatter():
    """Render dict to frontmatter block."""
    meta = {"confidence": "high", "tags": ["a", "b"]}
    rendered = render_frontmatter(meta)
    assert rendered.startswith("---\n")
    assert "confidence: high" in rendered
    assert "tags: [a, b]" in rendered
    assert rendered.endswith("---\n")
    print("  PASS: render frontmatter")


def test_render_empty():
    """Render empty dict returns empty string."""
    assert render_frontmatter({}) == ""
    print("  PASS: render empty dict")


def test_update_frontmatter():
    """Update adds/changes fields, preserves body."""
    content = "---\nconfidence: low\ndomain: auth\n---\n# Body\n"
    updated = update_frontmatter(content, {"confidence": "high", "urgency": "active"})
    meta = parse_frontmatter(updated)
    assert meta["confidence"] == "high"
    assert meta["domain"] == "auth"
    assert meta["urgency"] == "active"
    assert "# Body" in strip_frontmatter(updated)
    print("  PASS: update frontmatter merges fields")


def test_update_remove():
    """Setting a key to None removes it."""
    content = "---\nconfidence: high\ndomain: auth\n---\nBody\n"
    updated = update_frontmatter(content, {"confidence": None})
    meta = parse_frontmatter(updated)
    assert "confidence" not in meta
    assert meta["domain"] == "auth"
    print("  PASS: update with None removes key")


def test_update_no_existing():
    """Update on file without frontmatter adds it."""
    content = "# Just text\nBody here.\n"
    updated = update_frontmatter(content, {"confidence": "high"})
    meta = parse_frontmatter(updated)
    assert meta["confidence"] == "high"
    body = strip_frontmatter(updated)
    assert "# Just text" in body
    print("  PASS: update adds frontmatter to plain file")


def test_roundtrip():
    """Parse -> render -> parse roundtrip."""
    original = {"confidence": "high", "urgency": "active", "domain": "auth", "tags": ["jwt", "oauth"]}
    rendered = render_frontmatter(original)
    parsed = parse_frontmatter(rendered + "body\n")
    assert parsed == original, f"Roundtrip failed: {parsed} != {original}"
    print("  PASS: roundtrip parse/render")


if __name__ == "__main__":
    print("Running frontmatter tests...\n")

    test_parse_basic()
    test_parse_types()
    test_parse_no_frontmatter()
    test_strip_frontmatter()
    test_strip_no_frontmatter()
    test_render_frontmatter()
    test_render_empty()
    test_update_frontmatter()
    test_update_remove()
    test_update_no_existing()
    test_roundtrip()

    print("\nAll frontmatter tests passed!")
